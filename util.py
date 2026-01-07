#!/usr/bin/env python

import collections
import json
import os
import sys

import urllib.request

# from https://triff.tools/api/docs/

API_URL = 'https://triff.tools/api/prices/station/?station_id=%i&type_ids=%s'

Price = collections.namedtuple('Price', ['item', 'station', 'buy', 'sell'])


def get_prices(station, items):
  url = API_URL % (station, ','.join(map(str, items)))
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
