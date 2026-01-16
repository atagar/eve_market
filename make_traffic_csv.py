"""
This repository's traffic data is from 1/14/2026.

To update its data...

  1. Open the following URLS...

    Jita (station ID: 60003760):
    https://www.adam4eve.eu/tradeVol_type.php?regionID=10000002

    Amarr (station ID: 60008494):
    https://www.adam4eve.eu/tradeVol_type.php?regionID=10000043

    Dodixie (station ID: 60011866):
    https://www.adam4eve.eu/tradeVol_type.php?regionID=10000032

  2. Copy the table of data to a text file. To do so, highlight the first item
     (indubitably 'Large Skill Injector') then shift-click the end.

  3. Convert its output into a CSV with this script.
"""

import util

# construct a {name => item_id} map

name_to_id = {}

for item in util.list_items():
  name_to_id[item.name] = str(item.id)


with open('input.txt') as input_file:
  with open('output.csv', 'w') as output_file:
    for line in input_file.readlines():
      if line.count('\t') >= 3:
        item_name, trades, volume, value = line.split('\t')[:4]
        item_name = item_name.strip()
        trades = trades.strip().replace('.', '')
        volume = volume.strip().replace('.', '')
        value = value.strip().replace('.', '')

        if item_name in name_to_id:
          output_file.write(','.join((name_to_id[item_name], trades, volume, value)) + '\n')
