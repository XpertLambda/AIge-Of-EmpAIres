from collections import namedtuple
import os

# -------------------
# Global Constants
# Classe Villager / Team restriction
# -------------------
BUILDING_TIME_REDUCTION = 0.75
RESOURCE_COLLECTION_RATE = 25
RESOURCE_CAPACITY = 20
START_MAXIMUM_POPULATION = 0
MAXIMUM_POPULATION=200

# -------------------
# Entity Resources NamedTuple
# -------------------
Resources = namedtuple("Resources", ["food", "gold", "wood"])

# -------------------
# Unit constants
# -------------------
ALLOWED_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
UPDATE_EVERY_N_MILLISECOND = 20
ONE_SECOND = 1000
FRAMES_PER_UNIT = 10


# -------------------
# Difficulty Settings
# -------------------
# LEAN
LEAN_STARTING_FOOD = 50
LEAN_STARTING_GOLD = 200
LEAN_STARTING_WOOD = 50
LEAN_STARTING_VILLAGERS = 3
LEAN_NUMBER_OF_TOWER_CENTRE = 1

# MEAN
MEAN_STARTING_FOOD = 2000
MEAN_STARTING_GOLD = 2000
MEAN_STARTING_WOOD = 2000
MEAN_STARTING_VILLAGERS = 3
MEAN_NUMBER_OF_TOWER_CENTRE = 1

# MARINES
MARINES_STARTING_FOOD = 20000
MARINES_STARTING_GOLD = 20000
MARINES_STARTING_WOOD = 20000
MARINES_STARTING_VILLAGERS = 15
MARINES_NUMBER_OF_TOWER_CENTRE = 3
MARINES_NUMBER_OF_BARRACKS = 2
MARINES_NUMBER_OF_STABLES = 2
MARINES_NUMBER_OF_ARCHERY_RANGES = 2

# -------------------
# Map Configuration
# -------------------
TILE_SIZE = 200
HALF_TILE_SIZE = TILE_SIZE / 2
MAP_WIDTH = 120 * TILE_SIZE
MAP_HEIGHT = 120 * TILE_SIZE
MIN_ZOOM = 0.15
MAX_ZOOM = 3.0
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1200
NUM_GOLD_TILES = 500
NUM_WOOD_TILES = 500
NUM_FOOD_TILES = 500
DIFFICULTY = 'DEBUG'
GOLD_SPAWN_MIDDLE = False
MAP_PADDING = 650

# -------------------
# Minimap Settings
# -------------------
MINIMAP_WIDTH = 600
MINIMAP_HEIGHT = 280
MINIMAP_MARGIN = 20

# -------------------
# Save Directory
# -------------------
SAVE_DIRECTORY = 'saves'
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

# -------------------
# Sprites Configuration
# -------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

gui_config = {
    'loading_screen': {
        'directory': 'assets/launcher/',
        'scale': None
    },

    'ResourcesPanel' :{
        'directory' : 'assets/UI/Panels/resourcesPan', 
    }, 

    'minimapPanel' :{
        'directory' : 'assets/UI/Panels/minimapPan', 
    },

    'gold':{
        'directory' : 'assets/UI/Resources/gold',
    },

    'wood':{
        'directory' : 'assets/UI/Resources/wood',
    },

    'food':{
        'directory' : 'assets/UI/Resources/food',
    }
}

BAR_HEIGHT = 30
BAR_BORDER_RADIUS = 30
PROGRESS_BAR_WIDTH_RATIO = 0.8
PROGRESS_BAR_Y_RATIO = 0.7

BUILDING_RATIO = 200
UNIT_RATIO = 100

Entity_Acronym = {
    'resources': {
        ' ': 'grass',
        'W': 'tree',
        'G': 'gold',
        'F': 'food'
    },
    'buildings': {
        'A': 'archeryrange',
        'B': 'barracks',
        'C': 'camp',
        'F': 'farm',
        'H': 'house',
        'K': 'keep',
        'S': 'stable',
        'T': 'towncenter'
    },
    'units': {
        'a': 'archer',
        'h': 'horseman',
        's': 'swordsman',
        'v': 'villager'
    }
}

states = {
     0: 'idle',
     1: 'walk',
     2: 'attack',
     3: 'death',
     4: 'decay',
     5: 'task'
}

sprite_config = {
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO
        },
        'archeryrange': {
            'directory': 'assets/buildings/archeryrange/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO
        },
        'keep': {
            'directory': 'assets/buildings/keep/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO
        },
        'camp': {
            'directory': 'assets/buildings/camp/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO
        },
        'house': {
            'directory': 'assets/buildings/house/',
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'variant': 4
        },
        'farm': {
            'directory': 'assets/buildings/farm/',
            'adjust_scale': TILE_SIZE / 120
        },
    },
    'resources': {
        'grass': {
            'directory': 'assets/resources/grass/',
            'scale': (10 * TILE_SIZE // 2, 10 * TILE_SIZE // 4)
        },
        'gold': {
            'directory': 'assets/resources/gold/',
            'scale': (TILE_SIZE, TILE_SIZE),
            'variant': 4
        },
        'tree': {
            'directory': 'assets/resources/tree/',
            'variant': 4
        }
    },
    'units': {
        'swordsman': {
            'directory': 'assets/units/swordsman/',
            'states': 5,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'villager': {
            'directory': 'assets/units/villager/',
            'states': 6,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'archer': {
            'directory': 'assets/units/archer/',
            'states': 5,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'horseman': {
            'directory': 'assets/units/horseman/',
            'states': 5,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        }
    }
}






