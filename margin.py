#!/usr/bin/env python

import collections
import math

import util

MIN_SELL = 1000000  # minimum sale value for an item to be shown
MIN_MARGIN = 85  # minimum margin for an item to be shown
MIN_TRADES = 6  # minimum daily trades for an item to be shown

DIV = '+{}+'.format('+'.join(['-' * width for width in (60, 10, 15, 15, 25)]))
LINE = '| {:<58} | {:>8} | {:>13} | {:>13} | {:>23} |'

# market group identifiers for all items in a category

MODULES = 9
IMPLANTS = 24
DRONES = 157
COMMODITIES = 19
SHIPS = 4


if __name__ == '__main__':
  prices = {}  # {item => {station => price}}
  all_items = {}  # mapping if item names to their identifier

  target_groups = [MODULES, IMPLANTS]

  for item in util.list_items():
    market_group = item.group

    while market_group:
      if market_group.id in target_groups:
        all_items[item.name] = item.id
        break

      market_group = market_group.parent

  for price in util.get_prices(util.JITA, all_items.values()):
    prices[price.item] = price

  lines = []  # list of (item_name, item_id, margin) tuples

  for item_name, item_id in all_items.items():
    price = prices[item_id]

    if price.buy is None or price.sell is None:
      continue  # item with a shortage tend to be too obscure

    margin = int((price.sell - price.buy) / price.sell * 100)

    if margin >= MIN_MARGIN and price.sell >= MIN_SELL and (price.trades and price.trades >= MIN_TRADES):
      lines.append((item_name, item_id, margin))

  lines.sort(key = lambda entry: prices[entry[1]].sell - prices[entry[1]].buy)

  headers = ('Item', 'Trades', 'Buy', 'Sell', 'Margin')

  print(DIV)
  print(LINE.format(*headers))
  print(DIV)

  for item_name, item_id, margin in lines:
    price = prices[item_id]

    print(LINE.format(
      item_name,
      '{:,}'.format(price.trades) if price.trades else 'N/A',
      '{:,}'.format(price.buy) if price.buy else 'N/A',
      '{:,}'.format(price.sell) if price.sell else 'N/A',
      '{:,} ({})'.format(int(price.sell - price.buy), '{}%'.format(margin) if margin is not None else 'N/A'),
    ))

  print(DIV)

