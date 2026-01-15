#!/usr/bin/env python

import collections
import json
import os
import sys

import urllib.request

# from https://triff.tools/api/docs/

API_URL = 'https://triff.tools/api/prices/station/?station_id={}&type_ids={}'

STATIC_TYPES = 'eve-online-static-data-3142455-jsonl/types.jsonl'
STATIC_GROUPS = 'eve-online-static-data-3142455-jsonl/marketGroups.jsonl'

# from https://www.adam4eve.eu/info_stations.php
#
# Perimeter = 1044752365771
# Ashab = 1044857068649
# Botane = 1044961079041

JITA = 60003760
AMARR = 60008494
DODIXIE = 60011866

STATIONS = collections.OrderedDict((
  (JITA, 'Jita'),
  (AMARR, 'Amarr'),
  (DODIXIE, 'Dodixie'),
))

Price = collections.namedtuple('Price', ['item', 'station', 'buy', 'sell'])
Traffic = collections.namedtuple('Traffic', ['trades', 'volume', 'value'])

Item = collections.namedtuple('Item', ('id', 'name', 'group_id'))
MarketGroup = collections.namedtuple('MarketGroup', ('id', 'name', 'parent_id'))

TRAFFIC = {}  # Cache of {station_id => {item_name => Volume}}


def get_traffic(station, item):
  if not TRAFFIC:
    _load_traffic()

  return TRAFFIC[station].get(item)


def _load_traffic():
  for station_id in STATIONS.keys():
    csv_path = 'traffic_{}.csv'.format(station_id)

    if not os.path.exists(csv_path):
      print("Missing traffic information at: {}".format(csv_path))
      sys.exit(1)

    with open(csv_path) as traffic_file:
      for line in traffic_file.readlines():
        item, trades, volume, value = line.rsplit(',', 3)
        TRAFFIC.setdefault(station_id, {})[item] = Traffic(int(trades), int(volume), int(value))


def get_prices(station, items):
  # URLs should be under 2,000 characters. Our URL has a 60 character prefix
  # and items IDs are up to six digits, so let's do batches of 320.

  items = list(items)

  for i in range(0, len(items), 320):
    for price in _get_prices(station, items[i:i + 320]):
      yield price


def _get_prices(station, items):
  url = API_URL.format(station, ','.join(map(str, items)))
  cache_path = os.path.join('cache', '{}:{}'.format(station, hash('-'.join(map(str, items)))))

  if os.path.exists(cache_path):
    with open(cache_path) as cache_file:
      prices_json = json.loads(cache_file.read())
  else:
    if not os.path.exists('cache'):
      os.makedirs('cache')

    try:
      prices_json = json.loads(urllib.request.urlopen(url).read())['rows']
    except:
      print("Unable to download from '{}': {}".format(url, sys.exc_info()[1]))
      sys.exit(1)

    with open(cache_path, 'w') as cache_file:
      cache_file.write(json.dumps(prices_json, indent = 2))

  missing_items = list(items)

  for item in prices_json:
    if item['buy_max'] is None:
      buy_price = None
    elif item['buy_max'].isdigit():
      buy_price = int(item['buy_max'])
    else:
      buy_price = float(item['buy_max'])

    if item['sell_min'] is None:
      sell_price = None
    elif item['sell_min'].isdigit():
      sell_price = int(item['sell_min'])
    else:
      sell_price = float(item['sell_min'])

    missing_items.remove(int(item['type_id']))
    yield Price(int(item['type_id']), int(item['station_id']), buy_price, sell_price)

  if missing_items:
    for item_id in missing_items:
      yield Price(item_id, station, None, None)


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
