#!/usr/bin/env python

import collections
import json
import math
import os
import sys

import util

# from https://triff.tools/api/docs/

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

  ('Small Artillery Specialization', 12201),
  ('Medium Artillery Specialization', 12202),
  ('Large Artillery Specialization', 12203),
  ('Capital Artillery Specialization', 41404),

  ('Small Autocannon Specialization', 11084),
  ('Medium Autocannon Specialization', 12208),
  ('Large Autocannon Specialization', 12209),
  ('Capital Autocannon Specialization', 41403),

  ('Small Beam Laser Specialization', 11083),
  ('Medium Beam Laser Specialization', 12204),
  ('Large Beam Laser Specialization', 12205),
  ('Capital Beam Laser Specialization', 41408),

  ('Small Blaster Specialization', 12210),
  ('Medium Blaster Specialization', 12211),
  ('Large Blaster Specialization', 12212),
  ('Capital Blaster Specialization', 41405),

  ('Small Pulse Laser Specialization', 12213),
  ('Medium Pulse Laser Specialization', 12214),
  ('Large Pulse Laser Specialization', 12215),
  ('Capital Pulse Laser Specialization', 41407),

  ('Amarr Drone Specialization', 12484),
  ('Minmatar Drone Specialization', 12485),
  ('Gallente Drone Specialization', 12486),
  ('Caldari Drone Specialization', 12487),

  ('Small Disintegrator Specialization', 47873),
  ('Medium Disintegrator Specialization', 47874),
  ('Large Disintegrator Specialization', 47875),

  ('Small Vorton Specialization', 54827),
  ('Medium Vorton Specialization', 54828),
  ('Large Vorton Specialization', 54829),
))

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


if __name__ == '__main__':
  prices = {}  # {item => {station => price}}
  items = SKILLS

  for station_id in STATIONS.keys():
    for price in util.get_prices(station_id, items.values()):
      prices.setdefault(price.item, {})[station_id] = price

  lines = []  # list of (item_name, item_id, buy_from, sell_at, margin) tuples

  for item_name, item_id in items.items():
    buy_from = sorted(prices[item_id].values(), key = lambda price: price.sell if price.sell else math.inf)[0]
    sell_at = sorted(prices[item_id].values(), key = lambda price: price.sell if price.sell else -1, reverse = True)[0]
    margin = int((sell_at.sell - buy_from.sell) / buy_from.sell * 100) if (buy_from.sell and sell_at.sell) else None

    lines.append((item_name, item_id, buy_from, sell_at, margin))

  lines.sort(key = lambda entry: entry[4] if entry[4] else math.inf, reverse = True)

  headers = ('Item', 'Jita', 'Amarr', 'Dodixie', 'Buy from...', 'Sell at...')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for item_name, item_id, buy_from, sell_at, margin in lines:
    print(LINE.format(
      item_name,
      '{:,}'.format(prices[item_id][JITA].sell) if prices[item_id][JITA].sell else 'N/A',
      '{:,}'.format(prices[item_id][AMARR].sell) if prices[item_id][AMARR].sell else 'N/A',
      '{:,}'.format(prices[item_id][DODIXIE].sell) if prices[item_id][DODIXIE].sell else 'N/A',
      '{} @ {:,}'.format(STATIONS[buy_from.station], buy_from.sell),
      '{} @ {:,} ({})'.format(STATIONS[sell_at.station], sell_at.sell, '{}%'.format(margin) if margin else 'N/A'),
    ))

  print(DIV)

