#!/usr/bin/env python

import collections
import json
import os
import sys

import urllib.request

# from https://triff.tools/api/docs/

API_URL = 'https://triff.tools/api/prices/station/?station_id=%i&type_ids=%s'
STATIC_TYPES = 'eve-online-static-data-3142455-jsonl/types.jsonl'

DIV = '+----------------------------------------+--------------------+--------------------+--------------------+------------------------------+------------------------------+'
LINE = '| {:<38} | {:>18} | {:>18} | {:>18} | {:>28} | {:>28} |'

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


# Skills from the LP stores (hence no direct NPC sellers).

SKILLS = collections.OrderedDict((
  ('Mining Connections', 3893),
  ('Distribution Connections', 3894),
  ('Security Connections', 3895),

  ('Small Railgun Specialization', 11082),
  ('Small Beam Laser Specialization', 11083),
  ('Small Autocannon Specialization', 11084),
  ('Small Artillery Specialization', 12201),

  ('Medium Artillery Specialization', 12202),
  ('Large Artillery Specialization', 12203),
  ('Medium Beam Laser Specialization', 12204),
  ('Large Beam Laser Specialization', 12205),
  ('Medium Railgun Specialization', 12206),
  ('Large Railgun Specialization', 12207),
  ('Medium Autocannon Specialization', 12208),
  ('Large Autocannon Specialization', 12209),
  ('Small Blaster Specialization', 12210),
  ('Medium Blaster Specialization', 12211),
  ('Large Blaster Specialization', 12212),
  ('Small Pulse Laser Specialization', 12213),
  ('Medium Pulse Laser Specialization', 12214),
  ('Large Pulse Laser Specialization', 12215),

  ('Amarr Drone Specialization', 12484),
  ('Minmatar Drone Specialization', 12485),
  ('Gallente Drone Specialization', 12486),
  ('Caldari Drone Specialization', 12487),

  ('Rocket Specialization', 20209),
  ('Light Missile Specialization', 20210),
  ('Heavy Missile Specialization', 20211),
  ('Cruise Missile Specialization', 20212),
  ('Torpedo Specialization', 20213),
  ('Mining Drone Specialization', 22541),
  ('Heavy Assault Missile Specialization', 25718),

  ('Capital Autocannon Specialization', 41403),
  ('Capital Artillery Specialization', 41404),
  ('Capital Blaster Specialization', 41405),
  ('Capital Railgun Specialization', 41406),
  ('Capital Pulse Laser Specialization', 41407),
  ('Capital Beam Laser Specialization', 41408),
  ('XL Torpedo Specialization', 41409),
  ('XL Cruise Missile Specialization', 41410),

  ('Ice Harvesting Drone Specialization', 43703),

  ('Small Disintegrator Specialization', 47873),
  ('Medium Disintegrator Specialization', 47874),
  ('Large Disintegrator Specialization', 47875),

  ('Small Vorton Specialization', 54827),
  ('Medium Vorton Specialization', 54828),
  ('Large Vorton Specialization', 54829),

  ('Salvage Drone Specialization', 57164),
  ('Mutated Drone Specialization', 60515),
))


Price = collections.namedtuple('Price', ['item', 'station', 'buy', 'sell'])

ID_TO_ITEM = {}


def resolve(item):
  """
  Resolve an item identifier to its name.
  """

  if not os.path.exists(STATIC_TYPES):
    print('Please downdoad and extract the json from: https://developers.eveonline.com/static-data')
    sys.exit(1)

  if not ID_TO_ITEM:
    with open(STATIC_TYPES) as static_file:
      for line in static_file.readlines():
        static_json = json.loads(line)
        item_id, name = static_json['_key'], static_json['name']['en']
        ID_TO_ITEM[item_id] = name

  return ID_TO_ITEM[item]


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

  for item in prices_json:
    yield Price(
      int(item['type_id']),
      int(item['station_id']),
      float(item['buy_max']) if item['buy_max'] else 0.0,
      float(item['sell_min']) if item['sell_min'] else 0.0,
    )


if __name__ == '__main__':
  prices = {}  # {item => {station => price}}
  items = SKILLS

  for station_id in STATIONS.keys():
    for price in get_prices(station_id, items.values()):
      prices.setdefault(price.item, {})[station_id] = price

  headers = ('Item', 'Jita', 'Amarr', 'Dodixie', 'Buy from...', 'Sell at...')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for item_name, item_id in items.items():
    buy_from = sorted(prices[item_id].values(), key = lambda price: price.buy)[0]
    sell_at = sorted(prices[item_id].values(), key = lambda price: price.sell, reverse = True)[0]

    if sell_at.sell and buy_from.buy:
      spread = '{}%'.format(int((sell_at.sell - buy_from.buy) / buy_from.buy * 100))
    else:
      spread = 'N/A'

    print(LINE.format(
      item_name,
      prices[item_id][JITA].sell,
      prices[item_id][AMARR].sell,
      prices[item_id][DODIXIE].sell,
      '{} @ {}'.format(STATIONS[buy_from.station], buy_from.buy),
      '{} @ {} ({})'.format(STATIONS[sell_at.station], sell_at.sell, spread),
    ))

  print(DIV)

