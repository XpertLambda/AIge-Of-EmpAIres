# Settings/setup.py

# -------------------
# Classe Villager
# -------------------

BUILDING_TIME_REDUCTION = 0.75  # Facteur de réduction du temps de construction
RESOURCE_COLLECTION_RATE = 25    # Taux de collecte de ressources (unités par minute)
RESOURCE_CAPACITY = 20            # Capacité de transport des ressources

####################

# -------------------
# Difficultés du jeu
# -------------------

# LEAN

LEAN_STARTING_FOOD = 50          # Nourriture de départ
LEAN_STARTING_GOLD = 200         # Or de départ
LEAN_STARTING_WOOD = 50          # Bois de départ
LEAN_STARTING_VILLAGERS = 3      # Nombre de villageois de départ
LEAN_NUMBER_OF_TOWER_CENTRE = 1  # Nombre de tower centre 

####################

# MEAN

MEAN_STARTING_FOOD = 2000        # Nourriture de départ
MEAN_STARTING_GOLD = 2000        # Or de départ
MEAN_STARTING_WOOD = 2000        # Bois de départ
MEAN_STARTING_VILLAGERS = 3      # Nombre de villageois de départ
MEAN_NUMBER_OF_TOWER_CENTRE = 1  # Nombre de tower centre 

####################

# MARINES

MARINES_STARTING_FOOD = 20000       # Nourriture de départ
MARINES_STARTING_GOLD = 20000       # Or de départ
MARINES_STARTING_WOOD = 20000       # Bois de départ
MARINES_STARTING_VILLAGERS = 15     # Nombre de villageois de départ
MARINES_NUMBER_OF_TOWER_CENTRE = 3  # Nombre de tower centre 
MARINES_NUMBER_OF_BARRACKS = 2      # Nombre de casernes
MARINES_NUMBER_OF_STABLES = 2       # Nombre d'écuries
MARINES_NUMBER_OF_ARCHERY_RANGES = 2  # Nombre de champs de tir à l'arc

####################

# -------------------
# Configuration de la Carte
# -------------------

# Dimensions des tuiles
TILE_SIZE = 16  # Taille d'une tuile en pixels

# Dimensions de la carte en pixels
MAP_WIDTH = 120 * TILE_SIZE  # 1920 pixels
MAP_HEIGHT = 120 * TILE_SIZE # 1920 pixels

# Nombre de tuiles visibles en largeur et hauteur
TILES_IN_VIEW = 75  # Nombre de tuiles visibles

# Dimensions de la fenêtre en pixels
WINDOW_WIDTH = TILES_IN_VIEW * TILE_SIZE  # 1200 pixels
WINDOW_HEIGHT = TILES_IN_VIEW * TILE_SIZE # 1200 pixels

# Nombre de tuiles de chaque type
NUM_MOUNTAIN_TILES = 1000
NUM_GOLD_TILES = 1000
NUM_WOOD_TILES = 1000
NUM_FOOD_TILES = 1000

# Difficulté du jeu
DIFFICULTY = 'lean'


# Minimap settings
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 100
MINIMAP_MARGIN = 10
