#!/usr/bin/env python

import collections
import math

import util

MIN_SELL = 1000000  # minimum sale value for an item to be shown
MIN_MARGIN = 50  # minimum margin for an item to be shown

DIV = '+{}+'.format('+'.join(['-' * width for width in (40, 20, 20, 20, 30, 30)]))
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

MINERALS = collections.OrderedDict((
  ('Tritanium', 34),
  ('Pyerite', 35),
  ('Mexallon', 36),
  ('Isogen', 37),
  ('Nocxium', 38),
  ('Zydrine', 39),
  ('Megacyte', 40),
  ('Morphite', 11399),
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

# High tier abyssal filaments.

FILAMENTS = collections.OrderedDict((
  ('Cataclysmic Dark Filament', 56140),
  ('Cataclysmic Electrical Filament', 56139),
  ('Cataclysmic Exotic Filament', 56141),
  ('Cataclysmic Firestorm Filament', 56142),
  ('Cataclysmic Gamma Filament', 56143),
  ('Chaotic Dark Filament', 47895),
  ('Chaotic Electrical Filament', 47907),
  ('Chaotic Exotic Filament', 47891),
  ('Chaotic Firestorm Filament', 47899),
  ('Chaotic Gamma Filament', 47903),
  ('Fierce Dark Filament', 47893),
  ('Fierce Electrical Filament', 47905),
  ('Fierce Exotic Filament', 47889),
  ('Fierce Firestorm Filament', 47897),
  ('Fierce Gamma Filament', 47901),
  ('Raging Dark Filament', 47894),
  ('Raging Electrical Filament', 47906),
  ('Raging Exotic Filament', 47890),
  ('Raging Firestorm Filament', 47898),
  ('Raging Gamma Filament', 47902),
))

FACTION_MODULES = collections.OrderedDict((
  ('Dread Guristas Drone Damage Amplifier', 33846),
  ('Federation Navy Drone Damage Amplifier', 33842),
  ('Imperial Navy Drone Damage Amplifier', 33844),
  ('Sentient Drone Damage Amplifier', 33848),
))


# Additional items to consider.

EXTRA = collections.OrderedDict((
  ('Graviton Physics', 11446),
  ('High Energy Physics', 11433),
  ('Hydromagnetic Physics', 11443),
  ('Quantum Physics', 11455),
))


if __name__ == '__main__':
  prices = {}  # {item => {station => price}}
  items = MINERALS | SKILLS | FILAMENTS | FACTION_MODULES | EXTRA

  for station_id in STATIONS.keys():
    for price in util.get_prices(station_id, items.values()):
      prices.setdefault(price.item, {})[station_id] = price

  lines = []  # list of (item_name, item_id, buy_from, sell_at, margin) tuples

  for item_name, item_id in items.items():
    buy_from = sorted(prices[item_id].values(), key = lambda price: price.sell if price.sell else math.inf)[0]
    sell_at = sorted(prices[item_id].values(), key = lambda price: price.sell if price.sell else -1, reverse = True)[0]
    margin = int((sell_at.sell - buy_from.sell) / buy_from.sell * 100) if (buy_from.sell and sell_at.sell) else None
    has_shortage = prices[item_id][JITA].sell is None or prices[item_id][AMARR].sell is None or prices[item_id][DODIXIE].sell is None

    if has_shortage or (margin >= MIN_MARGIN and sell_at.sell >= MIN_SELL):
      lines.append((item_name, item_id, buy_from, sell_at, margin))

  lines.sort(key = lambda entry: entry[4] if entry[4] is not None else -1, reverse = True)

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
      '{} @ {:,} ({})'.format(STATIONS[sell_at.station], sell_at.sell, '{}%'.format(margin) if margin is not None else 'N/A'),
    ))

  print(DIV)

