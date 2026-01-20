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

JITA = 60003760
AMARR = 60008494
DODIXIE = 60011866

STATIONS = collections.OrderedDict((
  (JITA, 'Jita'),
  (AMARR, 'Amarr'),
  (DODIXIE, 'Dodixie'),
))

# buy orders are often at a tax haven instead

TAX_HAVENS = {
  JITA: [
    1044752365771,  # Perimeter - 0.0% Neutral States Market HQ
    1038069922162,  # Perimeter - Tranquilty Trading Tower
  ], AMARR: [
    1044857068649,  # Ashab - 0.4% Market Cheaper than AMARR
  ], DODIXIE: [
    1044961079041,  # Botane - Cheapest Market BE SMART 0.3%
  ],
}

Item = collections.namedtuple('Item', ('id', 'name', 'group'))
MarketGroup = collections.namedtuple('MarketGroup', ('id', 'name', 'parent'))
Price = collections.namedtuple('Price', ['item', 'station', 'buy', 'sell', 'trades', 'volume', 'value'])

ALL_ITEMS = {}  # cache of {item_id => item}
MARKET_GROUPS = {}  # cache of {group_id => (name, parent_id)}
TRAFFIC = {}  # cache of {station_id => {item_id => (trades, volume, value)}}


def list_items():
  """
  Provides a list of all Items.

  :returns: a **list** of Items
  """

  if not ALL_ITEMS:
    with open(STATIC_TYPES) as static_file:
      for line in static_file.readlines():
        static_json = json.loads(line)

        if 'marketGroupID' not in static_json:
          continue

        item_id, name, group_id = static_json['_key'], static_json['name']['en'], static_json['marketGroupID']
        ALL_ITEMS[item_id] = Item(item_id, name, _get_market_group(group_id))

  return list(ALL_ITEMS.values())


def _get_market_group(group_id):
  """
  Provides the **MarketGroup** with a given identifier.
  """

  if group_id is None:
    return None

  if not MARKET_GROUPS:
    with open(STATIC_GROUPS) as static_file:
      for line in static_file.readlines():
        static_json = json.loads(line)

        group_id, name, parent_id = static_json['_key'], static_json['name']['en'], static_json.get('parentGroupID')
        MARKET_GROUPS[group_id] = (name, parent_id)

  name, parent_id = MARKET_GROUPS[group_id]

  return MarketGroup(group_id, name, _get_market_group(parent_id))


def _load_traffic():
  for station_id in STATIONS.keys():
    csv_path = 'traffic_{}.csv'.format(station_id)

    if not os.path.exists(csv_path):
      print("Missing traffic information at: {}".format(csv_path))
      sys.exit(1)

    with open(csv_path) as traffic_file:
      for line in traffic_file.readlines():
        item_id, trades, volume, value = line.rsplit(',', 3)
        TRAFFIC.setdefault(station_id, {})[int(item_id)] = (int(trades), int(volume), int(value))


def get_prices(station, items):
  # URLs should be under 2,000 characters. Our URL has a 60 character prefix
  # and items IDs are up to six digits, so let's do batches of 320.

  items = list(items)

  prices = []
  tax_haven_price = {}  # item id => max buy price

  for i in range(0, len(items), 320):
    prices += _get_prices(station, items[i:i + 320])

    # TODO: The triff.tools API doen't provide data for POS (responses are
    # empty). Maybe we can do this if/when we call an official CCP API?

    # for tax_haven in TAX_HAVENS.get(station, []):
    #   for price in _get_prices(tax_haven, items[i:i + 320]):
    #     if price.buy:
    #       tax_haven_price[price.item] = max(tax_haven_price.get(price.item, 0), price.buy)

  for price in prices:
    if price.buy is None:
      buy_price = tax_haven_price.get(price.item, None)
    else:
      buy_price = max(price.buy, tax_haven_price.get(price.item, 0))

    yield Price(price.item, price.station, buy_price, price.sell, price.trades, price.volume, price.value)


def _get_prices(station, items):
  if not TRAFFIC:
    _load_traffic()

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

    item_id = int(item['type_id'])

    if item_id in TRAFFIC[station]:
      trades, volume, value = TRAFFIC[station][item_id]
    else:
      trades, volume, value = None, None, None

    missing_items.remove(item_id)
    yield Price(item_id, int(item['station_id']), buy_price, sell_price, trades, volume, value)

  if missing_items:
    for item_id in missing_items:
      yield Price(item_id, station, None, None, None, None, None)
