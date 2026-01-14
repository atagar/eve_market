#!/usr/bin/env python

import collections
import getopt
import os
import json
import sys

DIV = '+{}+'.format('+'.join(['-' * width for width in (70, 10, 10, 10)]))
LINE = '| {:<68} | {:>8} | {:>8} | {:>8} |'
TUPLE_LINE = "  ('{}', {}),"

STATIC_TYPES = 'eve-online-static-data-3142455-jsonl/types.jsonl'
STATIC_GROUPS = 'eve-online-static-data-3142455-jsonl/marketGroups.jsonl'

DEFAULT_ARGS = {
  'name': None,
  'item_id': None,
  'group_id': None,
  'print_tuple': False,
  'print_help': False,
}

HELP_TEXT = """\
Lists the Eve Online items that match a criteria.

  --name NAME     look for this substring in its name
  --id ID         look for this item identifier
  --group ID      look for this market group identifier
  -h, --help      presents this help
"""

Item = collections.namedtuple('Item', ('id', 'name', 'group_id'))
MarketGroup = collections.namedtuple('MarketGroup', ('id', 'name', 'parent_id'))


def list_items():
  """
  Provides a list of all Items.

  :returns: a **list** of Items
  """

  items = []

  with open(STATIC_TYPES) as static_file:
    for line in static_file.readlines():
      static_json = json.loads(line)

      if 'marketGroupID' not in static_json:
        continue

      name, item_id, group_id = static_json['name']['en'], static_json['_key'], static_json['marketGroupID']
      items.append(Item(item_id, name, group_id))

  return items


def list_market_groups():
  """
  Provides the mapping of market group identifiers to their MarketGroup.

  :returns: a **dict** of **int** identifiers to their MarketGroup
  """

  groups = {}  # {id => MarketGroup}

  with open(STATIC_GROUPS) as static_file:
    for line in static_file.readlines():
      static_json = json.loads(line)

      name, group_id, parent_id = static_json['name']['en'], static_json['_key'], static_json.get('parentGroupID')
      groups[group_id] = MarketGroup(group_id, name, parent_id)

  return groups


def parse(argv):
  """
  Parses our arguments, providing a named tuple with their values.

  :param list argv: input arguments to be parsed

  :returns: a **named tuple** with our parsed arguments

  :raises: **ValueError** if we got an invalid argument
  """

  args = dict(DEFAULT_ARGS)

  try:
    recognized_args, unrecognized_args = getopt.getopt(argv, 'th', ['name=', 'id=', 'group=', 'tuple', 'help'])

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

  if not os.path.exists(STATIC_GROUPS) or not os.path.exists(STATIC_TYPES):
    print('Please downdoad and extract the json from: https://developers.eveonline.com/static-data')
    sys.exit(1)

  items = list_items()
  groups = list_market_groups()

  matches = []  # (name, item_id, group_id, category_id) tuples

  for item in items:
    # get this group's top parent

    category = groups[item.group_id]
    is_group_match = args.group_id == category.id

    while category.parent_id is not None:
      category = groups[category.parent_id]
      is_group_match = is_group_match or (args.group_id == category.id)

    if (args.name and args.name in item.name) or args.item_id == item.id or is_group_match:
      matches.append((item.name, item.id, item.group_id, category.id))

  matches.sort(key = lambda entry: entry[0])

  headers = ('Item', 'ID', 'Group ID', 'Category')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for name, item_id, group_id, category_id in matches:

    if args.print_tuple:
      print(TUPLE_LINE.format(name, item_id))
    else:
      print(LINE.format(name, item_id, group_id, category_id))
  
  print(DIV)

