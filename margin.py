#!/usr/bin/env python

import collections
import getopt
import math
import sys

import util

DIV = '+{}+'.format('+'.join(['-' * width for width in (60, 10, 15, 15, 25)]))
LINE = '| {:<58} | {:>8} | {:>13} | {:>13} | {:>23} |'

# market group identifiers for all items in a category

CATEGORIES = {
  'M': 9,     # modules
  'I': 24,    # implants
  'S': 4,     # ships
  'D': 157,   # drones
  'M': 2436,  # mutaplasmids
  'F': 2456,  # filaments
}

DEFAULT_ARGS = {
  'trade_hub': util.JITA,
  'min_margin': 85,
  'min_trades': 6,
  'min_sell': 1000000,
  'categories': [9],
  'print_help': False,
}

HELP_TEXT = """\
Lists all items at a trade hub that match this criteria.

  --amarr         check Amarr instead of Jita
  --dodixie       check Dodixie instead of Jita

  --margin        minimum percentage for items to show (default: 85)
  --trades        minimum number of daily trades for items to show (default: 6)
  --sell          minimum sell price for items to show (default: 1M ISK)

  --categories    letters for the categoires to include (default: MI)

                  M = Modules           I = Implants
                  S = Ships             D = Drones
                  M = Mutaplasmids      F = Filaments

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
    recognized_args, unrecognized_args = getopt.getopt(argv, 'h', ['amarr', 'dodixie', 'margin=', 'trades=', 'sell=', 'categories=', 'help'])

    if unrecognized_args:
      raise getopt.GetoptError("'%s' aren't recognized arguments" % "', '".join(unrecognized_args))
  except Exception as exc:
    raise ValueError('%s (for usage provide --help)' % exc)

  for opt, arg in recognized_args:
    if opt == '--amarr':
      args['trade_hub'] = util.AMARR
    elif opt == '--dodixie':
      args['trade_hub'] = util.DODIXIE
    elif opt == '--margin':
      if not arg.isdigit():
        raise ValueError("Margin must be an integer, not '{}'".format(arg))

      args['min_margin'] = int(arg)
    elif opt == '--trades':
      if not arg.isdigit():
        raise ValueError("Trades must be an integer, not '{}'".format(arg))

      args['min_trades'] = int(arg)
    elif opt == '--sell':
      if not arg.isdigit():
        raise ValueError("Sell price must be an integer, not '{}'".format(arg))

      args['min_sell'] = int(arg)
    elif opt == '--categories':
      catagories = []

      for cat_character in arg:
        if cat_character not in CATEGORIES.keys():
          raise ValueError("Valid catagories are {}, not '{}'".format(''.join(CATEGORIES.keys()), cat_character))

        catagories.append(CATEGORIES[cat_character])

      args['categories'] = catagories
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

  prices = {}  # {item => {station => price}}
  all_items = {}  # mapping if item names to their identifier

  for item in util.list_items():
    market_group = item.group

    while market_group:
      if market_group.id in args.categories:
        all_items[item.name] = item.id
        break

      market_group = market_group.parent

  for price in util.get_prices(args.trade_hub, all_items.values()):
    prices[price.item] = price

  lines = []  # list of (item_name, item_id, margin) tuples

  for item_name, item_id in all_items.items():
    price = prices[item_id]

    if price.buy is None or price.sell is None:
      continue  # item with a shortage tend to be too obscure

    margin = int((price.sell - price.buy) / price.sell * 100)

    if margin >= args.min_margin and price.sell >= args.min_sell and (price.trades and price.trades >= args.min_trades):
      lines.append((item_name, item_id, margin))

  lines.sort(key = lambda entry: entry[2])

  headers = ('Item', 'Trades', 'Buy', 'Sell', 'Margin')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for item_name, item_id, margin in lines:
    price = prices[item_id]

    print(LINE.format(
      item_name,
      '{:,}'.format(price.trades) if price.trades else 'N/A',
      '{:,}'.format(price.buy) if price.buy else 'N/A',
      '{:,}'.format(price.sell) if price.sell else 'N/A',
      '{:,} ({})'.format(int(price.sell - price.buy), '{}%'.format(margin) if margin is not None else 'N/A'),
    ))

  print(DIV)

