#!/usr/bin/env python

import collections
import getopt
import os
import sys

import util

DIV = '+{}+'.format('+'.join(['-' * width for width in (70, 10, 10, 10)]))
LINE = '| {:<68} | {:>8} | {:>8} | {:>8} |'
TUPLE_LINE = "  ('{}', {}),"

PRICE_DIV = '+{}+'.format('+'.join(['-' * width for width in (70, 15, 15, 15, 15, 15, 15, 10, 10, 10)]))
PRICE_LINE = '| {:<68} | {:>13} | {:>13} | {:>13} | {:>13} | {:>13} | {:>13} | {:>8} | {:>8} | {:>8} |'

PRICE_PRE_DIV = ' ' * 71 + '+{}+'.format('+'.join(['-' * width for width in (47, 47, 32)]))
PRICE_PRE_LINE = '  {:<68} | {:>45} | {:>45} | {:>30} |'

DEFAULT_ARGS = {
  'name': None,
  'item_id': None,
  'group_id': None,
  'prices': False,
  'print_tuple': False,
  'print_help': False,
}

HELP_TEXT = """\
Lists the Eve Online items that match a criteria.

  --name NAME     look for this substring in its name
  --id ID         look for this item identifier
  --group ID      look for this market group identifier
  -p, --prices    list the market's prices
  -h, --help      presents this help
"""


def parse(argv):
  """
  Parses our arguments, providing a named tuple with their values.

  :param list argv: input arguments to be parsed

  :returns: a **named tuple** with our parsed arguments

  :raises: **ValueError** if we got an invalid argument
  """

  args = dict(DEFAULT_ARGS)

  try:
    recognized_args, unrecognized_args = getopt.getopt(argv, 'pth', ['name=', 'id=', 'group=', 'prices', 'tuple', 'help'])

    if unrecognized_args:
      raise getopt.GetoptError("'%s' aren't recognized arguments" % "', '".join(unrecognized_args))
  except Exception as exc:
    raise ValueError('%s (for usage provide --help)' % exc)

  for opt, arg in recognized_args:
    if opt == '--name':
      args['name'] = arg
    elif opt == '--id':
      if not arg.isdigit():
        raise ValueError("Identifiers must be an integer, not '{}'".format(arg))

      args['item_id'] = int(arg)
    elif opt == '--group':
      if not arg.isdigit():
        raise ValueError("Identifiers must be an integer, not '{}'".format(arg))

      args['group_id'] = int(arg)
    elif opt in ('-p', '--prices'):
      args['prices'] = True
    elif opt in ('-t', '--tuple'):
      args['print_tuple'] = True
    elif opt in ('-h', '--help'):
      args['print_help'] = True

  # translates our args dict into a named tuple

  Args = collections.namedtuple('Args', args.keys())
  return Args(**args)


if __name__ == '__main__':
  try:
    args = parse(sys.argv[1:])
  except ValueError as exc:
    print(exc)
    sys.exit(1)

  if args.print_help:
    print(HELP_TEXT)
    sys.exit()

  if not os.path.exists(util.STATIC_GROUPS) or not os.path.exists(util.STATIC_TYPES):
    print('Please downdoad and extract the json from: https://developers.eveonline.com/static-data')
    sys.exit(1)

  matches = []

  for item in util.list_items():
    if (args.name and args.name in item.name) or args.item_id == item.id:
      matches.append(item)
    elif args.group_id:
      market_group = item.group

      while market_group:
        if market_group.id == args.group_id:
          matches.append(item)

      market_group = market_group.parent

  matches.sort(key = lambda item: item.name)

  prices = {}

  if args.prices:
    for station_id in util.STATIONS.keys():
      for price in util.get_prices(station_id, [item.id for item in matches]):
        prices.setdefault(price.item, {})[station_id] = price

  if args.prices:
    pre_headers = ('', 'Sell', 'Buy', 'Trades')
    print(PRICE_PRE_DIV)
    print(PRICE_PRE_LINE.format(*pre_headers))

    headers = ('Item', 'Jita', 'Amarr', 'Dodixie', 'Jita', 'Amarr', 'Dodixie', 'Jita', 'Amarr', 'Dodixie')

    print(PRICE_DIV)
    print(PRICE_LINE.format(*headers))
    print(PRICE_DIV)
  else:
    headers = ('Item', 'ID', 'Group', 'Category')

    print(DIV)
    print(LINE.format(*headers))
    print(DIV)

  for item in matches:
    if args.print_tuple:
      print(TUPLE_LINE.format(item.name, item.id))
    elif args.prices:
      jita_sell = '{:,}'.format(prices[item.id][util.JITA].sell) if prices[item.id][util.JITA].sell else 'N/A'
      amarr_sell = '{:,}'.format(prices[item.id][util.AMARR].sell) if prices[item.id][util.AMARR].sell else 'N/A'
      dodixie_sell = '{:,}'.format(prices[item.id][util.DODIXIE].sell) if prices[item.id][util.DODIXIE].sell else 'N/A'

      jita_buy = '{:,}'.format(prices[item.id][util.JITA].buy) if prices[item.id][util.JITA].buy else 'N/A'
      amarr_buy = '{:,}'.format(prices[item.id][util.AMARR].buy) if prices[item.id][util.AMARR].buy else 'N/A'
      dodixie_buy = '{:,}'.format(prices[item.id][util.DODIXIE].buy) if prices[item.id][util.DODIXIE].buy else 'N/A'

      jita_traffic = util.get_traffic(util.JITA, item.name)
      amarr_traffic = util.get_traffic(util.AMARR, item.name)
      dodixie_traffic = util.get_traffic(util.DODIXIE, item.name)

      jita_trades = jita_traffic.trades if jita_traffic else 'N/A'
      amarr_trades = amarr_traffic.trades if amarr_traffic else 'N/A'
      dodixie_trades = dodixie_traffic.trades if dodixie_traffic else 'N/A'

      print(PRICE_LINE.format(item.name, jita_sell, amarr_sell, dodixie_sell, jita_buy, amarr_buy, dodixie_buy, jita_trades, amarr_trades, dodixie_trades))
    else:
      category = item.group

      while category.parent is not None:
        category = category.parent

      print(LINE.format(item.name, item.id, item.group.id, category.id))

  if args.prices:
    print(PRICE_DIV)
  else:
    print(DIV)
