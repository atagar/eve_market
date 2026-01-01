#!/usr/bin/env python

import collections
import json
import os
import sys

import urllib.request

# from https://triff.tools/api/docs/

API_URL = 'https://triff.tools/api/prices/station/?station_id=%i&type_ids=%s'

DIV = '+--------------------+----------+----------+----------+--------------------+--------------------+'
LINE = '| {:<18} | {:>8} | {:>8} | {:>8} | {:>18} | {:>18} |'

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

# from https://www.adam4eve.eu/info_types.php

ORES = collections.OrderedDict((
  ('Tritanium', 34),
))


Price = collections.namedtuple('Price', ['item', 'station', 'buy', 'sell'])


def get_prices(station, items):
  url = API_URL % (station, ','.join(map(str, items)))
  cache_path = os.path.join('cache', '{}:{}'.format(station, '-'.join(map(str, items))))

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

  for item in prices_json:
    yield Price(
      int(item['type_id']),
      int(item['station_id']),
      float(item['buy_max']),
      float(item['sell_min']),
    )


if __name__ == '__main__':
  prices = {}  # {item => {station => price}}
  items = ORES

  for station_id in STATIONS.keys():
    for price in get_prices(station_id, items.values()):
      prices.setdefault(price.item, {})[station_id] = price

  headers = ('Item', 'Jita', 'Amarr', 'Dodixie', 'Buy from...', 'Sell at...')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for item_name, item_id in ORES.items():
    buy_from = sorted(prices[item_id].values(), key = lambda price: price.buy)[0]
    sell_at = sorted(prices[item_id].values(), key = lambda price: price.sell, reverse = True)[0]
    spread = (sell_at.sell - buy_from.buy) / buy_from.buy

    print(LINE.format(
      item_name,
      prices[item_id][JITA].sell,
      prices[item_id][AMARR].sell,
      prices[item_id][DODIXIE].sell,
      '{} @ {}'.format(STATIONS[buy_from.station], buy_from.buy),
      '{} @ {} ({}%)'.format(STATIONS[sell_at.station], sell_at.sell, int(spread * 100)),
    ))

  print(DIV)

