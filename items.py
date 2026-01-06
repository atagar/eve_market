#!/usr/bin/env python

import collections
import getopt
import os
import json
import sys

DIV = '+{}+'.format('+'.join(['-' * width for width in (70, 10, 10)]))
LINE = '| {:<68} | {:>8} | {:>8} |'

STATIC_TYPES = 'eve-online-static-data-3142455-jsonl/types.jsonl'

DEFAULT_ARGS = {
  'name': None,
  'item_id': None,
  'group_id': None,
  'print_help': False,
}

HELP_TEXT = """\
Lists the Eve Online items that match a criteria.

  --name NAME     look for this substring in its name
  --id ID         look for this item identifier
  --group ID      look for this group identifier
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
    recognized_args, unrecognized_args = getopt.getopt(argv, 'h', ['name=', 'id=', 'group=', 'help'])

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

  if not os.path.exists(STATIC_TYPES):
    print('Please downdoad and extract the json from: https://developers.eveonline.com/static-data')
    sys.exit(1)

  matches = []  # (name, item_id, group_id) tuples

  with open(STATIC_TYPES) as static_file:
    for line in static_file.readlines():
      static_json = json.loads(line)
      name, item_id, group_id = static_json['name']['en'], static_json['_key'], static_json['groupID']

      if (args.name and args.name in name) or args.item_id == item_id or args.group_id == group_id:
        matches.append((name, item_id, group_id))

  headers = ('Item', 'ID', 'Group ID')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for name, item_id, group_id in matches:
    print(LINE.format(name, item_id, group_id))
  
  print(DIV)

