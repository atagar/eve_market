#!/usr/bin/env python

import collections
import math

import util

MIN_SELL = 1000000  # minimum sale value for an item to be shown
MIN_MARGIN = 50  # minimum margin for an item to be shown
MIN_TRADES = 10  # minimum daily trades for an item to be shown

DIV = '+{}+'.format('+'.join(['-' * width for width in (60, 15, 15, 15, 30, 30)]))
LINE = '| {:<58} | {:>13} | {:>13} | {:>13} | {:>28} | {:>28} |'

# Other bulk items to consider: PI

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

  ('Small Artillery Specialization', 12201),  # Amarr sells 0.5/day @ 2M
  ('Medium Artillery Specialization', 12202),  # Amarr sells 1/day @ shortage
  ('Large Artillery Specialization', 12203),
  ('Capital Artillery Specialization', 41404),

  ('Small Autocannon Specialization', 11084),  # Dodixie sells 1/day @ 2M
  ('Medium Autocannon Specialization', 12208),  # Dodixie sells 0.3/day @ shortage
  ('Large Autocannon Specialization', 12209),
  ('Capital Autocannon Specialization', 41403),

  ('Small Beam Laser Specialization', 11083),  # Dodixie sells 0.5/day @ 3M
  ('Medium Beam Laser Specialization', 12204),
  ('Large Beam Laser Specialization', 12205),  # Dodixie sells 1/week @ shortage
  ('Capital Beam Laser Specialization', 41408),

  ('Small Blaster Specialization', 12210),  # Amarr sells 1/day @ 3M
  ('Medium Blaster Specialization', 12211),  # Amarr sells 2/day @ 4M
  ('Large Blaster Specialization', 12212),  # Amarr sells 1/day @ 10M
  ('Capital Blaster Specialization', 41405),

  ('Small Pulse Laser Specialization', 12213),  # Dodixie sells 0.5/day @ 3M
  ('Medium Pulse Laser Specialization', 12214),  # Dodixie sells 0.5/day @ 6M
  ('Large Pulse Laser Specialization', 12215),
  ('Capital Pulse Laser Specialization', 41407),

  ('Amarr Drone Specialization', 12484),
  ('Minmatar Drone Specialization', 12485),  # Dodixie sells 2/day @ 7M
  ('Gallente Drone Specialization', 12486),  # Amarr sells 5/day @ 5M
  ('Caldari Drone Specialization', 12487),  # Dodixie sells 3/day @ 3M

  ('Small Disintegrator Specialization', 47873),  # Dodixie sells 2/day @ 4M
  ('Medium Disintegrator Specialization', 47874),  # Dodixie sells 2/day @ 6M
  ('Large Disintegrator Specialization', 47875),  # Amarr sells 2/day @ 272M

  ('Small Vorton Specialization', 54827),  # Dodixie sells 0.5/day @ 66M
  ('Medium Vorton Specialization', 54828),  # Amarr sells 2/day @ 45M
  ('Large Vorton Specialization', 54829),  # Amarr sells 1/day @ 81M
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

# Additional items to consider.

EXTRA = collections.OrderedDict((
  ('Graviton Physics', 11446),  # Dodixie sells 2/day @ 7M
  ('High Energy Physics', 11433),  # Amarr sells 5/day @ 4M
  ('Hydromagnetic Physics', 11443),  # Dodixie sells 2/day @ 10M
  ('Quantum Physics', 11455),  # Dodixie sells 1/day @ 4M

  ('Sisters Core Probe Launcher', 28758),  # Amarr buys 50/day @ 71M
))

# Items with at least 5 trades and 1B ISK per day at Amarr or Dodixie (except
# ships, cosmetics, and minerals).

TOP_TRADE_VALUE = collections.OrderedDict((
  ('Large Skill Injector', 40520),  # 146 trades for 137T @ Amarr, 59 trades for 72T @ Dodixie
  ('Skill Extractor', 40519),  # 44 trades for 34B @ Amarr, 15 trades for 26T @ Dodixie
  ('Small Skill Injector', 45635),  # 44 trades for 11B @ Amarr, 20 trades for 4.3B @ Dodixie
  ('ORE Strip Miner', 28754),  # 22 trades for 9B @ Amarr, 6 trades for 1.6B @ Dodixie
  ('Intact Armor Plates', 25624),  # 80 trades for 6B @ Amarr
  ('Helium Isotopes', 16274),  # 58 trades for 5.7B @ Amarr
  ('Helium Fuel Block', 4247),  # 65 trades for 5.6B @ Amarr
  ('Mining Laser Efficiency Charge Blueprint', 90734),  # 5 trades for 5.1B @ Amarr
  ('Pithum C-Type Multispectrum Shield Hardener', 4349),  # 11 trades for 3.5B @ Amarr
  ('Pithum C-Type Medium Shield Booster', 19187),  # 21 trades for 3.4B @ Amarr
  ('Mining Laser Efficiency Charge', 90733),  # 60 trades for 3.2B @ Amarr
  ('Centii A-Type Multispectrum Coating', 18710),  # 14 trades for 2.9B @ Amarr
  ('Daily Alpha Injector', 46375),  # 18 trades for 2.7B @ Amarr, 14 trades for 1.2B @ Dodixie
  ('Sisters Expanded Probe Launcher', 28756),  # 45 trades for 2.5B @ Amarr
  ('Compressed Clear Icicle', 28434),  # 32 trades for 2.4B @ Amarr
  ('Thukker Large Cap Battery', 41220),  # 19 trades for 2.3B @ Amarr
  ('Imperial Navy Heat Sink', 15810),  # 14 trades for 2.2B @ Amarr
  ('ORE Ice Harvester', 28752),  # 9 trades for 2.1B @ Amarr
  ('Caldari Navy Ballistic Control System', 15681),  # 18 trades for 2.1B @ Amarr
  ('Robotics', 9848),  # 66 trades for 2.1B @ Amarr
  ('Electro-Neural Signaller', 57450),  # 9 trades for 2.1B @ Amarr
  ('Nano Regulation Gate', 57449),  # 6 trades for 2B @ Amarr
  ('Neurovisual Input Matrix', 30251),  # 29 trades for 2B @ Amarr
  ('Pith X-Type X-Large Shield Booster', 19208),  # 6 trades for 2B @ Amarr
  ('Pith X-Type Large Shield Booster', 19207),  # 8 trades for 2B @ Amarr
  ('Nanite Repair Paste', 28668),  # 360 trades for 1.9B @ Amarr
  ('Medium Core Defense Field Extender II', 31796),  # 87 trades for 1.8B @ Amarr
  ('Hydrocarbons', 16633),  # 27 trades for 1.8B @ Amarr
  ('Republic Fleet Large Cap Battery', 41218),  # 100 trades for 1.7B @ Amarr
  ('Dread Guristas Multispectrum Shield Hardener', 13969),  # 6 trades for 1.7B @ Amarr
  ('Imperial Navy Multispectrum Energized Membrane', 15729),  # 24 trades for 1.7B @ Amarr
  ('Evaporite Deposits', 16635),  # 24 trades for 1.6B @ Amarr
  ('Large Core Defense Field Extender II', 26448),  # 10 trades for 1.6B @ Amarr
  ('Sisters Core Probe Launcher', 28758),  # 76 trades for 1.5B @ Amarr
  ('Syndicate Gas Cloud Scoop', 28788),  # 12 trades for 1.5B @ Amarr
  ('Large Trimark Armor Pump II', 26302),  # 9 trades for 1.5B @ Amarr
  ('Imperial Navy Large EMP Smartbomb', 15963),  # 7 trades for 1.5B @ Amarr
  ('Large Capacitor Control Circuit II', 26374),  # 43 trades for 1.5B @ Amarr, 14 trades for 1.4B @ Dodixie
  ('Corpii A-Type Multispectrum Coating', 18708),  # 6 trades for 1.5B @ Amarr
  ('Dread Guristas Drone Damage Amplifier', 33846),  # 12 trades for 1.4B @ Amarr
  ('Silicates', 16636),  # 21 trades for 1.4B @ Amarr
  ('Logic Circuit', 25619),  # 162 trades for 1.4B @ Amarr
  ('Standup Dragonfly II', 47142),  # 7 trades for 1.4B @ Amarr
  ('Federation Navy Stasis Webifier', 17559),  # 30 trades for 1.4B @ Amarr
  ('Cybernetic Subprocessor - Improved', 10222),  # 10 trades for 1.3B @ Amarr
  ('Coolant', 9832),  # 35 trades for 1.3B @ Amarr
  ('Medium Core Defense Field Purger II', 31812),  # 19 trades for 1.3B @ Amarr
  ('Neural Boost - Improved', 10213),  # 10 trades for 1.2B @ Amarr
  ('Tangled Power Conduit', 25594),  # 292 trades for 1.1B @ Amarr
  ('Heavy Water', 16272),  # 138 trades for 1.1B @ Amarr
  ('Memory Augmentation - Improved', 10209),  # 11 trades for 1.1B @ Amarr
  ('Compressed Veldspar', 62516),  # 57 trades for 1.1B @ Amarr
  ('Compressed Veldspar II-Grade', 62517),  # 54 trades for 1.1B @ Amarr
  ('Medium Trimark Armor Pump II', 31059),  # 37 trades for 1.1B @ Amarr
  ('Mobile Tractor Unit', 33475),  # 120 trades for 1.1B @ Amarr
  ("Inherent Implants 'Highwall' Mining MX-1005", 22535),  # 7 trades for 1.1B @ Amarr
  ("Zainou 'Beancounter' Reprocessing RX-804", 27174),  # 5 trades for 1B @ Amarr
  ('Covert Research Tools', 33577),  # 41 trades for 1B @ Amarr
  ('Ocular Filter - Improved', 10217),  # 10 trades for 1B @ Amarr
  ('Enhanced Ward Console', 25625),  # 51 trades for 1B @ Amarr
  ('Self-Harmonizing Power Core', 2872),  # 28 trades for 1B @ Amarr
  ('Magmatic Gas', 81143),  # 10 trades for 1B @ Amarr
  ('Imperial Navy 1600mm Steel Plates', 31900),  # 20 trades for 1B @ Amarr
  ('Zero-Point Condensate', 48112),  # 111 trades for 1B @ Amarr
  ('Mid-grade Crystal Epsilon', 22110),  # 5 trades for 1B @ Amarr
  ('Modulated Strip Miner II', 17912),  # 61 trades for 1B @ Amarr
  ('Oxygen Isotopes', 17887),  # 20 trades for 3.8B @ Dodixie
  ('Compressed Blue Ice', 28433),  # 22 trades for 3.5B @ Dodixie
  ('Coreli A-Type Multispectrum Coating', 18789),  # 10 trades for 1.9B @ Dodixie
  ('Oxygen Fuel Block', 4312),  # 18 trades for 1.6B @ Dodixie
  ('Contaminated Lorentz Fluid', 25591),  # 173 trades for 1.5B @ Dodixie
  ('Unstable 100MN Afterburner Mutaplasmid', 47755),  # 6 trades for 1B @ Dodixie
))


if __name__ == '__main__':
  prices = {}  # {item => {station => price}}
  #all_items = MINERALS | SKILLS | FILAMENTS | DRONES | IMPLANTS | EXTRA
  #all_items = MINERALS | TOP_TRADE_VALUE

  all_items = {}  # mapping if item names to their identifier

  target_group = 9  # all modules

  for item in util.list_items():
    market_group = item.group

    while market_group:
      if market_group.id == target_group:
        all_items[item.name] = item.id
        break

      market_group = market_group.parent

  for station_id in util.STATIONS.keys():
    for price in util.get_prices(station_id, all_items.values()):
      prices.setdefault(price.item, {})[station_id] = price

  lines = []  # list of (item_name, item_id, buy_from, sell_at, margin) tuples

  for item_name, item_id in all_items.items():
    buy_from = sorted(prices[item_id].values(), key = lambda price: price.sell if price.sell else math.inf)[0]
    sell_at = sorted(prices[item_id].values(), key = lambda price: price.sell if price.sell else -1, reverse = True)[0]

    if prices[item_id][util.JITA].sell is None or prices[item_id][util.AMARR].sell is None or prices[item_id][util.DODIXIE].sell is None:
      continue  # item with a shortage tend to be too obscure

    margin = int((sell_at.sell - buy_from.sell) / buy_from.sell * 100) if (buy_from.sell and sell_at.sell) else None
    traffic = util.get_traffic(sell_at.station, item_name)

    if not traffic:
      continue

    if margin >= MIN_MARGIN and sell_at.sell >= MIN_SELL and traffic.trades >= MIN_TRADES:
      lines.append((item_name, item_id, buy_from, sell_at, margin))

  lines.sort(key = lambda entry: entry[4] if entry[4] is not None else -1, reverse = True)

  headers = ('Item', 'Jita', 'Amarr', 'Dodixie', 'Buy from...', 'Sell at...')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for item_name, item_id, buy_from, sell_at, margin in lines:
    print(LINE.format(
      item_name,
      '{:,}'.format(prices[item_id][util.JITA].sell) if prices[item_id][util.JITA].sell else 'N/A',
      '{:,}'.format(prices[item_id][util.AMARR].sell) if prices[item_id][util.AMARR].sell else 'N/A',
      '{:,}'.format(prices[item_id][util.DODIXIE].sell) if prices[item_id][util.DODIXIE].sell else 'N/A',
      '{} @ {:,}'.format(util.STATIONS[buy_from.station], buy_from.sell),
      '{} @ {:,} ({})'.format(util.STATIONS[sell_at.station], sell_at.sell, '{}%'.format(margin) if margin is not None else 'N/A'),
    ))

  print(DIV)

