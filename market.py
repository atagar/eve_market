#!/usr/bin/env python

import collections
import math

import items
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

DRONES = collections.OrderedDict((
  # Amarr

  ("'Augmented' Acolyte", 28264),
  ("'Integrated' Acolyte", 28262),  # Amarr sells 40/day @ 1M
  ('Acolyte EV-300', 23659),
  ('Acolyte I', 2203),
  ('Acolyte II', 2205),
  ('Acolyte TD-300', 23727),
  ('Imperial Navy Acolyte', 31864),

  #("'Augmented' Infiltrator", 28284),  # low volume
  ("'Integrated' Infiltrator", 28282),
  ('Imperial Navy Infiltrator', 31866),
  ('Infiltrator EV-600', 23702),
  ('Infiltrator I', 2173),
  ('Infiltrator II', 2175),
  ('Infiltrator TD-600', 23725),

  ("'Augmented' Praetor", 28292),
  ("'Integrated' Praetor", 28290),  # Dodixie sells 1/day @ 2M
  ('Imperial Navy Praetor', 31870),
  ('Praetor EV-900', 22572),
  ('Praetor I', 2193),
  ('Praetor II', 2195),
  ('Praetor TD-900', 23510),

  # Caldari

  ("'Augmented' Hornet", 28280),  # Amarr sells 10/day @ 9M
  ("'Integrated' Hornet", 28278),
  ('Caldari Navy Hornet', 31872),
  ('Hornet EC-300', 23707),
  ('Hornet I', 2464),
  ('Hornet II', 2466),

  ("'Augmented' Vespa", 28300),
  ("'Integrated' Vespa", 28298),  # Dodixie sells 3/day @ 2M
  ('Caldari Navy Vespa', 31874),
  ('Vespa EC-600', 23705),
  ('Vespa I', 15508),
  ('Vespa II', 21638),

  ("'Augmented' Wasp", 28308),
  ("'Integrated' Wasp", 28306),  # Dodixie sells 1/day @ 2M
  ('Caldari Navy Wasp', 31876),
  ('Wasp EC-900', 23473),
  ('Wasp I', 1201),
  ('Wasp II', 2436),

  # Gallente

  ("'Augmented' Hobgoblin", 28276),
  ("'Integrated' Hobgoblin", 28274),
  ('Federation Navy Hobgoblin', 31880),
  ('Hobgoblin I', 2454),
  ('Hobgoblin II', 2456),
  ('Hobgoblin SD-300', 23715),

  ("'Augmented' Hammerhead", 28272),
  ("'Integrated' Hammerhead", 28270),
  ('Federation Navy Hammerhead', 31882),
  ('Hammerhead I', 2183),
  ('Hammerhead II', 2185),
  #('Hammerhead SD-600', 23713),  # low volume

  ("'Augmented' Ogre", 28288),
  ("'Integrated' Ogre", 28286),  # Dodixie sells 2/day @ 2M
  ('Federation Navy Ogre', 31884),
  ('Ogre I', 2444),
  ('Ogre II', 2446),
  ('Ogre SD-900', 23506),

  # Minmatar

  ("'Augmented' Warrior", 28304),
  ("'Integrated' Warrior", 28302),
  ('Republic Fleet Warrior', 31888),
  ('Warrior I', 2486),
  ('Warrior II', 2488),
  ('Warrior SW-300', 23731),
  ('Warrior TP-300', 23723),

  ("'Augmented' Valkyrie", 28296),
  ("'Integrated' Valkyrie", 28294),
  ('Republic Fleet Valkyrie', 31890),
  ('Valkyrie I', 15510),
  ('Valkyrie II', 21640),
  ('Valkyrie SW-600', 23729),
  ('Valkyrie TP-600', 23721),

  #("'Augmented' Berserker", 28268),  # low volume
  ("'Integrated' Berserker", 28266),  # Dodixie sells 1/day @ 1M
  ('Berserker I', 2476),
  ('Berserker II', 2478),
  ('Berserker SW-900', 23536),
  ('Berserker TP-900', 23512),
  ('Republic Fleet Berserker', 31892),

  # Utility

  ("'Augmented' Ice Harvesting Drone", 43701),
  ("'Augmented' Mining Drone", 43694),
  ("'Excavator' Ice Harvesting Drone", 43681),
  ("'Excavator' Mining Drone", 41030),
  ('Harvester Mining Drone', 3218),
  ('Ice Harvesting Drone I', 43699),
  ('Ice Harvesting Drone II', 43700),
  ('Mining Drone I', 10246),
  ('Mining Drone II', 10250),

  ("'Dunk' Salvage Drone", 55761),
  ('Salvage Drone I', 32787),
  ('Salvage Drone II', 55760),
))

FACTION_MODULES = collections.OrderedDict((
  ('Centus X-Type EM Armor Hardener', 18935),
  ('Centus X-Type Explosive Armor Hardener', 18939),
  ('Centus X-Type Kinetic Armor Hardener', 18943),
  ('Centus X-Type Large Armor Repairer', 19046),
  ('Centus X-Type Thermal Armor Hardener', 18947),
  ('Core X-Type 100MN Afterburner', 18698),
  ('Core X-Type 500MN Microwarpdrive', 19335),
  ('Core X-Type EM Armor Hardener', 18973),
  ('Core X-Type Explosive Armor Hardener', 18975),
  ('Core X-Type Kinetic Armor Hardener', 18977),
  ('Core X-Type Large Armor Repairer', 19038),
  ('Core X-Type Thermal Armor Hardener', 18979),
  ('Corpus X-Type EM Armor Hardener', 18933),
  ('Corpus X-Type Explosive Armor Hardener', 18937),
  ('Corpus X-Type Heavy Energy Neutralizer', 37631),
  ('Corpus X-Type Heavy Energy Nosferatu', 19119),
  ('Corpus X-Type Kinetic Armor Hardener', 18941),
  ('Corpus X-Type Large Armor Repairer', 19045),
  ('Corpus X-Type Thermal Armor Hardener', 18945),
  ('Gist X-Type 100MN Afterburner', 18676),
  ('Gist X-Type 500MN Microwarpdrive', 19359),
  ('Gist X-Type EM Shield Hardener', 19281),
  ('Gist X-Type Explosive Shield Hardener', 19285),
  ('Gist X-Type Kinetic Shield Hardener', 19287),
  ('Gist X-Type Large Shield Booster', 19200),
  ('Gist X-Type Shield Boost Amplifier', 19301),
  ('Gist X-Type Thermal Shield Hardener', 19283),
  ('Gist X-Type X-Large Shield Booster', 19198),
  ('Pith X-Type EM Shield Hardener', 19282),
  ('Pith X-Type Explosive Shield Hardener', 19286),
  ('Pith X-Type Kinetic Shield Hardener', 19288),
  ('Pith X-Type Large Shield Booster', 19207),
  ('Pith X-Type Shield Boost Amplifier', 19295),
  ('Pith X-Type Thermal Shield Hardener', 19284),
  ('Pith X-Type X-Large Shield Booster', 19208),

  ('Centii A-Type EM Coating', 18762),
  ('Centii A-Type Explosive Coating', 18758),
  ('Centii A-Type Kinetic Coating', 18754),
  ('Centii A-Type Multispectrum Coating', 18710),
  ('Centii A-Type Small Armor Repairer', 19009),
  ('Centii A-Type Small Remote Armor Repairer', 19051),
  ('Centii A-Type Small Remote Capacitor Transmitter', 19075),
  ('Centii A-Type Thermal Coating', 18766),
  ('Centum A-Type EM Energized Membrane', 18871),
  ('Centum A-Type Explosive Energized Membrane', 18875),
  ('Centum A-Type Kinetic Energized Membrane', 18879),
  ('Centum A-Type Medium Armor Repairer', 19027),
  ('Centum A-Type Medium Remote Armor Repairer', 19057),
  ('Centum A-Type Medium Remote Capacitor Transmitter', 19087),
  ('Centum A-Type Multispectrum Energized Membrane', 18883),
  ('Centum A-Type Thermal Energized Membrane', 18867),
  ('Centus A-Type EM Armor Hardener', 18931),
  ('Centus A-Type Explosive Armor Hardener', 18927),
  ('Centus A-Type Kinetic Armor Hardener', 18923),
  ('Centus A-Type Large Armor Repairer', 19044),
  ('Centus A-Type Thermal Armor Hardener', 18919),
  ('Core A-Type 100MN Afterburner', 18696),
  ('Core A-Type 500MN Microwarpdrive', 19329),
  ('Core A-Type EM Armor Hardener', 18965),
  ('Core A-Type Explosive Armor Hardener', 18967),
  ('Core A-Type Kinetic Armor Hardener', 18969),
  ('Core A-Type Large Armor Repairer', 19037),
  ('Core A-Type Thermal Armor Hardener', 18971),
  ('Coreli A-Type 1MN Afterburner', 18692),
  ('Coreli A-Type 5MN Microwarpdrive', 19325),
  ('Coreli A-Type EM Coating', 18795),
  ('Coreli A-Type Explosive Coating', 18793),
  ('Coreli A-Type Kinetic Coating', 18791),
  ('Coreli A-Type Multispectrum Coating', 18789),
  ('Coreli A-Type Small Armor Repairer', 19015),
  ('Coreli A-Type Small Remote Armor Repairer', 18985),
  ('Coreli A-Type Thermal Coating', 18797),
  ('Corelum A-Type 10MN Afterburner', 18694),
  ('Corelum A-Type 50MN Microwarpdrive', 19327),
  ('Corelum A-Type EM Energized Membrane', 18825),
  ('Corelum A-Type Explosive Energized Membrane', 18823),
  ('Corelum A-Type Kinetic Energized Membrane', 18821),
  ('Corelum A-Type Medium Armor Repairer', 19033),
  ('Corelum A-Type Medium Remote Armor Repairer', 18991),
  ('Corelum A-Type Multispectrum Energized Membrane', 18819),
  ('Corelum A-Type Thermal Energized Membrane', 18827),
  ('Corpii A-Type EM Coating', 18760),
  ('Corpii A-Type Explosive Coating', 18756),
  ('Corpii A-Type Kinetic Coating', 18752),
  ('Corpii A-Type Multispectrum Coating', 18708),
  ('Corpii A-Type Small Armor Repairer', 19003),
  ('Corpii A-Type Small Energy Neutralizer', 37624),
  ('Corpii A-Type Small Energy Nosferatu', 19105),
  ('Corpii A-Type Small Remote Capacitor Transmitter', 19069),
  ('Corpii A-Type Thermal Coating', 18764),
  ('Corpum A-Type EM Energized Membrane', 18869),
  ('Corpum A-Type Explosive Energized Membrane', 18873),
  ('Corpum A-Type Kinetic Energized Membrane', 18877),
  ('Corpum A-Type Medium Armor Repairer', 19021),
  ('Corpum A-Type Medium Energy Neutralizer', 37627),
  ('Corpum A-Type Medium Energy Nosferatu', 19111),
  ('Corpum A-Type Medium Remote Capacitor Transmitter', 19081),
  ('Corpum A-Type Multispectrum Energized Membrane', 18881),
  ('Corpum A-Type Thermal Energized Membrane', 18865),
  ('Corpus A-Type EM Armor Hardener', 18929),
  ('Corpus A-Type Explosive Armor Hardener', 18925),
  ('Corpus A-Type Heavy Energy Neutralizer', 37630),
  ('Corpus A-Type Heavy Energy Nosferatu', 19117),
  ('Corpus A-Type Kinetic Armor Hardener', 18921),
  ('Corpus A-Type Large Armor Repairer', 19043),
  ('Corpus A-Type Thermal Armor Hardener', 18917),
  ('Gist A-Type 100MN Afterburner', 18674),
  ('Gist A-Type 500MN Microwarpdrive', 19353),
  ('Gist A-Type EM Shield Hardener', 19279),
  ('Gist A-Type Explosive Shield Hardener', 19275),
  ('Gist A-Type Kinetic Shield Hardener', 19273),
  ('Gist A-Type Large Shield Booster', 19199),
  ('Gist A-Type Shield Boost Amplifier', 19293),
  ('Gist A-Type Thermal Shield Hardener', 19277),
  ('Gist A-Type X-Large Shield Booster', 19197),
  ('Gistii A-Type 1MN Afterburner', 18670),
  ('Gistii A-Type 5MN Microwarpdrive', 19349),
  ('Gistii A-Type Small Remote Shield Booster', 19133),
  ('Gistii A-Type Small Shield Booster', 19173),
  ('Gistum A-Type 10MN Afterburner', 18672),
  ('Gistum A-Type 50MN Microwarpdrive', 19351),
  ('Gistum A-Type EM Shield Amplifier', 19255),
  ('Gistum A-Type Explosive Shield Amplifier', 19249),
  ('Gistum A-Type Kinetic Shield Amplifier', 19253),
  ('Gistum A-Type Medium Remote Shield Booster', 19145),
  ('Gistum A-Type Medium Shield Booster', 19185),
  ('Gistum A-Type Multispectrum Shield Hardener', 4346),
  ('Gistum A-Type Thermal Shield Amplifier', 19251),
  ('Pith A-Type EM Shield Hardener', 19280),
  ('Pith A-Type Explosive Shield Hardener', 19276),
  ('Pith A-Type Kinetic Shield Hardener', 19274),
  ('Pith A-Type Large Shield Booster', 19205),
  ('Pith A-Type Shield Boost Amplifier', 19311),
  ('Pith A-Type Thermal Shield Hardener', 19278),
  ('Pith A-Type X-Large Shield Booster', 19206),
  ('Pithi A-Type Small Remote Shield Booster', 19139),
  ('Pithi A-Type Small Shield Booster', 19179),
  ('Pithum A-Type EM Shield Amplifier', 19231),
  ('Pithum A-Type Explosive Shield Amplifier', 19225),
  ('Pithum A-Type Kinetic Shield Amplifier', 19229),
  ('Pithum A-Type Medium Remote Shield Booster', 19151),
  ('Pithum A-Type Medium Shield Booster', 19191),
  ('Pithum A-Type Multispectrum Shield Hardener', 4347),
  ('Pithum A-Type Thermal Shield Amplifier', 19227),

  ('Centii B-Type EM Coating', 18750),
  #('Centii B-Type Explosive Coating', 18746),  # low volume
  ('Centii B-Type Kinetic Coating', 18742),
  ('Centii B-Type Multispectrum Coating', 18706),
  ('Centii B-Type Small Armor Repairer', 19007),
  ('Centii B-Type Small Remote Armor Repairer', 19049),
  ('Centii B-Type Small Remote Capacitor Transmitter', 19073),
  ('Centii B-Type Thermal Coating', 18730),
  ('Centum B-Type EM Energized Membrane', 19363),
  ('Centum B-Type Explosive Energized Membrane', 18859),
  ('Centum B-Type Kinetic Energized Membrane', 18855),
  ('Centum B-Type Medium Armor Repairer', 19025),
  ('Centum B-Type Medium Remote Armor Repairer', 19055),
  ('Centum B-Type Medium Remote Capacitor Transmitter', 19085),
  ('Centum B-Type Multispectrum Energized Membrane', 18851),
  ('Centum B-Type Thermal Energized Membrane', 18863),
  ('Centus B-Type EM Armor Hardener', 18903),
  ('Centus B-Type Explosive Armor Hardener', 18907),
  ('Centus B-Type Kinetic Armor Hardener', 18911),
  ('Centus B-Type Large Armor Repairer', 19042),
  ('Centus B-Type Thermal Armor Hardener', 18915),
  ('Core B-Type 100MN Afterburner', 18690),
  ('Core B-Type 500MN Microwarpdrive', 19323),
  ('Core B-Type EM Armor Hardener', 18957),
  ('Core B-Type Explosive Armor Hardener', 18959),
  ('Core B-Type Kinetic Armor Hardener', 18961),
  ('Core B-Type Large Armor Repairer', 19036),
  ('Core B-Type Thermal Armor Hardener', 18963),
  ('Coreli B-Type 1MN Afterburner', 18686),
  ('Coreli B-Type 5MN Microwarpdrive', 19319),
  ('Coreli B-Type EM Coating', 18785),
  ('Coreli B-Type Explosive Coating', 18783),
  ('Coreli B-Type Kinetic Coating', 18781),
  ('Coreli B-Type Multispectrum Coating', 18779),
  ('Coreli B-Type Small Armor Repairer', 19013),
  ('Coreli B-Type Small Remote Armor Repairer', 18983),
  ('Coreli B-Type Thermal Coating', 18787),
  ('Corelum B-Type 10MN Afterburner', 18688),
  ('Corelum B-Type 50MN Microwarpdrive', 19321),
  ('Corelum B-Type EM Energized Membrane', 18815),
  ('Corelum B-Type Explosive Energized Membrane', 18813),
  ('Corelum B-Type Kinetic Energized Membrane', 18811),
  ('Corelum B-Type Medium Armor Repairer', 19031),
  ('Corelum B-Type Medium Remote Armor Repairer', 18989),
  ('Corelum B-Type Multispectrum Energized Membrane', 18809),
  ('Corelum B-Type Thermal Energized Membrane', 18817),
  ('Corpii B-Type EM Coating', 18748),
  ('Corpii B-Type Explosive Coating', 18744),
  ('Corpii B-Type Kinetic Coating', 18740),
  ('Corpii B-Type Multispectrum Coating', 18704),
  ('Corpii B-Type Small Armor Repairer', 19001),
  ('Corpii B-Type Small Energy Neutralizer', 37623),
  ('Corpii B-Type Small Energy Nosferatu', 19103),
  ('Corpii B-Type Small Remote Capacitor Transmitter', 19067),
  ('Corpii B-Type Thermal Coating', 18728),
  ('Corpum B-Type EM Energized Membrane', 19361),
  ('Corpum B-Type Explosive Energized Membrane', 18857),
  ('Corpum B-Type Kinetic Energized Membrane', 18853),
  ('Corpum B-Type Medium Armor Repairer', 19019),
  ('Corpum B-Type Medium Energy Neutralizer', 37626),
  ('Corpum B-Type Medium Energy Nosferatu', 19109),
  ('Corpum B-Type Medium Remote Capacitor Transmitter', 19079),
  ('Corpum B-Type Multispectrum Energized Membrane', 18849),
  ('Corpum B-Type Thermal Energized Membrane', 18861),
  ('Corpus B-Type EM Armor Hardener', 18901),
  ('Corpus B-Type Explosive Armor Hardener', 18905),
  ('Corpus B-Type Heavy Energy Neutralizer', 37629),
  ('Corpus B-Type Heavy Energy Nosferatu', 19115),
  ('Corpus B-Type Kinetic Armor Hardener', 18909),
  ('Corpus B-Type Large Armor Repairer', 19041),
  ('Corpus B-Type Thermal Armor Hardener', 18913),
  ('Gist B-Type 100MN Afterburner', 18668),
  ('Gist B-Type 500MN Microwarpdrive', 19347),
  ('Gist B-Type EM Shield Hardener', 19265),
  ('Gist B-Type Explosive Shield Hardener', 19269),
  ('Gist B-Type Kinetic Shield Hardener', 19271),
  ('Gist B-Type Large Shield Booster', 19194),
  ('Gist B-Type Shield Boost Amplifier', 19299),
  ('Gist B-Type Thermal Shield Hardener', 19267),
  ('Gist B-Type X-Large Shield Booster', 19196),
  ('Gistii B-Type 1MN Afterburner', 18664),
  ('Gistii B-Type 5MN Microwarpdrive', 19343),
  ('Gistii B-Type Small Remote Shield Booster', 19131),
  ('Gistii B-Type Small Shield Booster', 19171),
  ('Gistum B-Type 10MN Afterburner', 18666),
  ('Gistum B-Type 50MN Microwarpdrive', 19345),
  ('Gistum B-Type EM Shield Amplifier', 19247),
  ('Gistum B-Type Explosive Shield Amplifier', 19235),
  #('Gistum B-Type Kinetic Shield Amplifier', 19243),  # low volume
  ('Gistum B-Type Medium Remote Shield Booster', 19143),
  ('Gistum B-Type Medium Shield Booster', 19183),
  ('Gistum B-Type Multispectrum Shield Hardener', 4345),
  #('Gistum B-Type Thermal Shield Amplifier', 19239),  # low volume
  ('Pith B-Type EM Shield Hardener', 19266),
  ('Pith B-Type Explosive Shield Hardener', 19270),
  ('Pith B-Type Kinetic Shield Hardener', 19272),
  ('Pith B-Type Large Shield Booster', 19203),
  ('Pith B-Type Shield Boost Amplifier', 19303),
  ('Pith B-Type Thermal Shield Hardener', 19268),
  ('Pith B-Type X-Large Shield Booster', 19204),
  ('Pithi B-Type Small Remote Shield Booster', 19137),
  ('Pithi B-Type Small Shield Booster', 19177),
  ('Pithum B-Type EM Shield Amplifier', 19223),
  ('Pithum B-Type Explosive Shield Amplifier', 19217),
  ('Pithum B-Type Kinetic Shield Amplifier', 19221),
  ('Pithum B-Type Medium Remote Shield Booster', 19149),
  ('Pithum B-Type Medium Shield Booster', 19189),
  ('Pithum B-Type Multispectrum Shield Hardener', 4348),
  ('Pithum B-Type Thermal Shield Amplifier', 19219),

  ('Centii C-Type EM Coating', 18722),
  ('Centii C-Type Explosive Coating', 18718),
  #('Centii C-Type Kinetic Coating', 18714),  # low volume
  ('Centii C-Type Multispectrum Coating', 18702),
  ('Centii C-Type Small Armor Repairer', 19005),
  ('Centii C-Type Small Remote Armor Repairer', 19047),
  ('Centii C-Type Small Remote Capacitor Transmitter', 19071),
  ('Centii C-Type Thermal Coating', 18726),
  ('Centum C-Type EM Energized Membrane', 18843),
  ('Centum C-Type Explosive Energized Membrane', 18839),
  ('Centum C-Type Kinetic Energized Membrane', 18835),
  ('Centum C-Type Medium Armor Repairer', 19023),
  ('Centum C-Type Medium Remote Armor Repairer', 19053),
  ('Centum C-Type Medium Remote Capacitor Transmitter', 19083),
  ('Centum C-Type Multispectrum Energized Membrane', 18831),
  ('Centum C-Type Thermal Energized Membrane', 18847),
  ('Centus C-Type EM Armor Hardener', 18887),
  ('Centus C-Type Explosive Armor Hardener', 18891),
  ('Centus C-Type Kinetic Armor Hardener', 18895),
  ('Centus C-Type Large Armor Repairer', 19040),
  ('Centus C-Type Thermal Armor Hardener', 18899),
  ('Core C-Type 100MN Afterburner', 18684),
  ('Core C-Type 500MN Microwarpdrive', 19317),
  ('Core C-Type EM Armor Hardener', 18949),
  ('Core C-Type Explosive Armor Hardener', 18951),
  ('Core C-Type Kinetic Armor Hardener', 18953),
  ('Core C-Type Large Armor Repairer', 19035),
  ('Core C-Type Thermal Armor Hardener', 18955),
  ('Coreli C-Type 1MN Afterburner', 18680),
  ('Coreli C-Type 5MN Microwarpdrive', 19313),
  ('Coreli C-Type EM Coating', 18775),
  ('Coreli C-Type Explosive Coating', 18772),
  ('Coreli C-Type Kinetic Coating', 18770),
  ('Coreli C-Type Multispectrum Coating', 18768),
  ('Coreli C-Type Small Armor Repairer', 19011),
  ('Coreli C-Type Small Remote Armor Repairer', 18981),
  ('Coreli C-Type Thermal Coating', 18777),
  ('Corelum C-Type 10MN Afterburner', 18682),
  ('Corelum C-Type 50MN Microwarpdrive', 19315),
  #('Corelum C-Type EM Energized Membrane', 18805),  # low volume
  ('Corelum C-Type Explosive Energized Membrane', 18803),
  ('Corelum C-Type Kinetic Energized Membrane', 18801),
  ('Corelum C-Type Medium Armor Repairer', 19029),
  ('Corelum C-Type Medium Remote Armor Repairer', 18987),
  ('Corelum C-Type Multispectrum Energized Membrane', 18799),
  ('Corelum C-Type Thermal Energized Membrane', 18807),
  ('Corpii C-Type EM Coating', 18720),
  ('Corpii C-Type Explosive Coating', 18716),
  ('Corpii C-Type Kinetic Coating', 18712),
  ('Corpii C-Type Multispectrum Coating', 18700),
  ('Corpii C-Type Small Armor Repairer', 18999),
  ('Corpii C-Type Small Energy Neutralizer', 37622),
  ('Corpii C-Type Small Energy Nosferatu', 19101),
  #('Corpii C-Type Small Remote Capacitor Transmitter', 19065),  # low volume
  ('Corpii C-Type Thermal Coating', 18724),
  #('Corpum C-Type EM Energized Membrane', 18841),  # low volume
  ('Corpum C-Type Explosive Energized Membrane', 18837),
  ('Corpum C-Type Kinetic Energized Membrane', 18833),
  ('Corpum C-Type Medium Armor Repairer', 19017),
  ('Corpum C-Type Medium Energy Neutralizer', 37625),
  ('Corpum C-Type Medium Energy Nosferatu', 19107),
  ('Corpum C-Type Medium Remote Capacitor Transmitter', 19077),
  ('Corpum C-Type Multispectrum Energized Membrane', 18829),
  ('Corpum C-Type Thermal Energized Membrane', 18845),
  ('Corpus C-Type EM Armor Hardener', 18885),
  ('Corpus C-Type Explosive Armor Hardener', 18889),
  ('Corpus C-Type Heavy Energy Neutralizer', 37628),
  ('Corpus C-Type Heavy Energy Nosferatu', 19113),
  ('Corpus C-Type Kinetic Armor Hardener', 18893),
  ('Corpus C-Type Large Armor Repairer', 19039),
  ('Corpus C-Type Thermal Armor Hardener', 18897),
  ('Gist C-Type 100MN Afterburner', 18662),
  ('Gist C-Type 500MN Microwarpdrive', 19341),
  ('Gist C-Type EM Shield Hardener', 19263),
  ('Gist C-Type Explosive Shield Hardener', 19259),
  ('Gist C-Type Kinetic Shield Hardener', 19257),
  ('Gist C-Type Large Shield Booster', 19193),
  ('Gist C-Type Shield Boost Amplifier', 19297),
  ('Gist C-Type Thermal Shield Hardener', 19261),
  ('Gist C-Type X-Large Shield Booster', 19195),
  ('Gistii C-Type 1MN Afterburner', 18658),
  ('Gistii C-Type 5MN Microwarpdrive', 19337),
  ('Gistii C-Type Small Remote Shield Booster', 19129),
  ('Gistii C-Type Small Shield Booster', 19169),
  ('Gistum C-Type 10MN Afterburner', 18660),
  ('Gistum C-Type 50MN Microwarpdrive', 19339),
  ('Gistum C-Type EM Shield Amplifier', 19245),
  ('Gistum C-Type Explosive Shield Amplifier', 19233),
  ('Gistum C-Type Kinetic Shield Amplifier', 19241),
  ('Gistum C-Type Medium Remote Shield Booster', 19141),
  ('Gistum C-Type Medium Shield Booster', 19181),
  ('Gistum C-Type Multispectrum Shield Hardener', 2050),
  ('Gistum C-Type Thermal Shield Amplifier', 19237),
  ('Pith C-Type EM Shield Hardener', 19264),
  ('Pith C-Type Explosive Shield Hardener', 19260),
  ('Pith C-Type Kinetic Shield Hardener', 19258),
  ('Pith C-Type Large Shield Booster', 19201),
  ('Pith C-Type Shield Boost Amplifier', 19289),
  ('Pith C-Type Thermal Shield Hardener', 19262),
  ('Pith C-Type X-Large Shield Booster', 19202),
  ('Pithi C-Type Small Remote Shield Booster', 19135),
  ('Pithi C-Type Small Shield Booster', 19175),
  ('Pithum C-Type EM Shield Amplifier', 19215),
  ('Pithum C-Type Explosive Shield Amplifier', 19209),
  #('Pithum C-Type Kinetic Shield Amplifier', 19213),  # low volume
  ('Pithum C-Type Medium Remote Shield Booster', 19147),
  ('Pithum C-Type Medium Shield Booster', 19187),
  ('Pithum C-Type Multispectrum Shield Hardener', 4349),
  ('Pithum C-Type Thermal Shield Amplifier', 19211),  # Dodixie sells 1/day @ 4M

  ('Dread Guristas Drone Damage Amplifier', 33846),
  ('Federation Navy Drone Damage Amplifier', 33842),
  ('Imperial Navy Drone Damage Amplifier', 33844),
  ('Sentient Drone Damage Amplifier', 33848),
))

IMPLANTS = collections.OrderedDict((
  ('Cybernetic Subprocessor - Basic', 9943),
  ('Cybernetic Subprocessor - Improved', 10222),
  ('Cybernetic Subprocessor - Standard', 10221),
  ('Limited Cybernetic Subprocessor', 13287),  # Amarr sells 2/day @ 4M
  ('Limited Cybernetic Subprocessor - Beta', 14298),
  ('Limited Memory Augmentation', 13284),
  ('Limited Memory Augmentation - Beta', 14297),
  ('Limited Neural Boost', 13285),  # Amarr sells 2/day @ 1M
  ('Limited Neural Boost - Beta', 14296),  # Amarr sells 2/day @ 8M
  ('Limited Ocular Filter', 13283),
  ('Limited Ocular Filter - Beta', 14295),
  ('Limited Social Adaptation Chip', 13286),
  ('Limited Social Adaptation Chip - Beta', 14299),
  ('Memory Augmentation - Basic', 9941),
  ('Memory Augmentation - Improved', 10209),
  ('Memory Augmentation - Standard', 10208),
  ('Neural Boost - Basic', 9942),
  ('Neural Boost - Improved', 10213),
  ('Neural Boost - Standard', 10212),
  ('Ocular Filter - Basic', 9899),
  ('Ocular Filter - Improved', 10217),
  ('Ocular Filter - Standard', 10216),
  ('Social Adaptation Chip - Basic', 9956),
  ('Social Adaptation Chip - Improved', 10226),
  ('Social Adaptation Chip - Standard', 10225),

  ('High-grade Ascendancy Alpha', 33516),
  ('High-grade Ascendancy Beta', 33525),
  ('High-grade Ascendancy Delta', 33526),
  ('High-grade Ascendancy Epsilon', 33527),
  ('High-grade Ascendancy Gamma', 33528),
  ('High-grade Ascendancy Omega', 33529),
  ('High-grade Asklepian Alpha', 42210),
  ('High-grade Asklepian Beta', 42211),
  ('High-grade Asklepian Delta', 42213),
  ('High-grade Asklepian Epsilon', 42214),
  ('High-grade Asklepian Gamma', 42212),
  ('High-grade Asklepian Omega', 42215),
  ('High-grade Crystal Alpha', 20121),
  ('High-grade Crystal Beta', 20157),
  ('High-grade Crystal Delta', 20159),
  ('High-grade Crystal Epsilon', 20160),
  ('High-grade Crystal Gamma', 20158),
  ('High-grade Crystal Omega', 20161),
  ('High-grade Hydra Alpha', 54392),
  ('High-grade Hydra Beta', 54393),
  ('High-grade Hydra Delta', 54395),
  ('High-grade Hydra Epsilon', 54396),
  ('High-grade Hydra Gamma', 54394),
  ('High-grade Hydra Omega', 54397),
  ('High-grade Snake Alpha', 19540),
  ('High-grade Snake Beta', 19551),
  ('High-grade Snake Delta', 19554),
  ('High-grade Snake Epsilon', 19555),
  ('High-grade Snake Gamma', 19553),  # Amarr sells 2/week @ 390M
  ('High-grade Snake Omega', 19556),
  ('Low-grade Asklepian Alpha', 42145),
  ('Low-grade Asklepian Beta', 42146),  # Amarr sells 1/day @ 50M
  ('Low-grade Asklepian Delta', 42200),
  ('Low-grade Asklepian Epsilon', 42201),
  ('Low-grade Asklepian Gamma', 42202),
  #('Low-grade Asklepian Omega', 42203),  # low volume
  ('Low-grade Crystal Alpha', 33923),  # Amarr sells 2/week @ 150M
  ('Low-grade Crystal Beta', 33924),
  ('Low-grade Crystal Delta', 33925),  # Amarr sells 3/week @ 177M
  ('Low-grade Crystal Epsilon', 33926),
  ('Low-grade Crystal Gamma', 33927),
  ('Low-grade Crystal Omega', 33928),
  ('Low-grade Hydra Alpha', 54404),
  ('Low-grade Hydra Beta', 54405),
  ('Low-grade Hydra Delta', 54407),
  ('Low-grade Hydra Epsilon', 54408),
  ('Low-grade Hydra Gamma', 54406),
  ('Low-grade Hydra Omega', 54409),
  ('Low-grade Snake Alpha', 33959),
  #('Low-grade Snake Beta', 33960),  # low volume
  #('Low-grade Snake Delta', 33961),  # low volume
  ('Low-grade Snake Epsilon', 33962),
  ('Low-grade Snake Gamma', 33963),  # Amarr sells 0.3/day @ 80M
  ('Low-grade Snake Omega', 33964),
  ('Low-grade Virtue Alpha', 33971),
  ('Low-grade Virtue Beta', 33972),
  #('Low-grade Virtue Delta', 33973),  # low volume
  ('Low-grade Virtue Epsilon', 33974),
  ('Low-grade Virtue Gamma', 33975),
  ('Low-grade Virtue Omega', 33976),
  ('Mid-grade Ascendancy Alpha', 33555),
  ('Mid-grade Ascendancy Beta', 33557),
  ('Mid-grade Ascendancy Delta', 33559),
  ('Mid-grade Ascendancy Epsilon', 33561),
  ('Mid-grade Ascendancy Gamma', 33563),
  ('Mid-grade Ascendancy Omega', 33565),
  ('Mid-grade Asklepian Alpha', 42204),
  ('Mid-grade Asklepian Beta', 42205),  # Amarr sells 2/day @ 75M
  ('Mid-grade Asklepian Delta', 42207),  # Dodixie sells 0.5/day @ 265M
  ('Mid-grade Asklepian Epsilon', 42208),
  ('Mid-grade Asklepian Gamma', 42206),
  ('Mid-grade Asklepian Omega', 42209),
  ('Mid-grade Crystal Alpha', 22107),
  ('Mid-grade Crystal Beta', 22108),
  ('Mid-grade Crystal Delta', 22109),
  ('Mid-grade Crystal Epsilon', 22110),
  ('Mid-grade Crystal Gamma', 22111),  # Dodixie sells 0.5/day @ 146M
  ('Mid-grade Crystal Omega', 22112),
  ('Mid-grade Hydra Alpha', 54398),
  ('Mid-grade Hydra Beta', 54399),
  ('Mid-grade Hydra Delta', 54401),
  ('Mid-grade Hydra Epsilon', 54402),
  ('Mid-grade Hydra Gamma', 54400),
  ('Mid-grade Hydra Omega', 54403),
  ('Mid-grade Snake Alpha', 22125),
  ('Mid-grade Snake Beta', 22126),
  ('Mid-grade Snake Delta', 22127),
  ('Mid-grade Snake Epsilon', 22128),
  ('Mid-grade Snake Gamma', 22129),
  ('Mid-grade Snake Omega', 22130),
  ('Mid-grade Virtue Alpha', 28808),  # Amarr sells 1/day @ 145M
  ('Mid-grade Virtue Beta', 28809),
  ('Mid-grade Virtue Delta', 28810),
  ('Mid-grade Virtue Epsilon', 28811),
  ('Mid-grade Virtue Gamma', 28812),  # Amarr sells 1/day @ 281M
  ('Mid-grade Virtue Omega', 28813),  # Amarr sells 1/day @ 887M

  ("Neural Lace 'Blackglass' Net Intrusion 920-40", 47028),
  #("Neural Lace 'Bluefire' Net Ablation 960-10", 85748),  # low volume
  ("Poteque 'Prospector' Archaeology AC-905", 27196),  # Dodixie sells 0.5/day @ 44M
  ("Poteque 'Prospector' Astrometric Acquisition AQ-702", 27193),  # Dodixie sells 1/day @ 7M
  ("Poteque 'Prospector' Astrometric Acquisition AQ-706", 27187),
  ("Poteque 'Prospector' Astrometric Acquisition AQ-710", 27192),
  ("Poteque 'Prospector' Astrometric Pinpointing AP-602", 27191),
  ("Poteque 'Prospector' Astrometric Pinpointing AP-606", 27186),
  ("Poteque 'Prospector' Astrometric Pinpointing AP-610", 27190),
  ("Poteque 'Prospector' Astrometric Rangefinding AR-802", 27195),  # Dodixie sells 1/day @ 6M
  ("Poteque 'Prospector' Astrometric Rangefinding AR-806", 27188),
  ("Poteque 'Prospector' Astrometric Rangefinding AR-810", 27194),
  ("Poteque 'Prospector' Environmental Analysis EY-1005", 27260),  # Dodixie sells 1/day @ shortage
  ("Poteque 'Prospector' Hacking HC-905", 27197),  # Dodixie sells 0.5/day @ shortage
  ("Poteque 'Prospector' Salvaging SV-905", 27198),
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

  groups = items.list_market_groups()
  target_group = 9  # all modules

  for item in items.list_items():
    category = groups[item.group_id]
    is_group_match = target_group == category.id

    while category.parent_id is not None:
      category = groups[category.parent_id]
      is_group_match = is_group_match or (target_group == category.id)

    if is_group_match:
      all_items[item.name] = item.id


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

