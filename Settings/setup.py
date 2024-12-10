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
TILE_SIZE = 200  # Taille d'une tuile en pixels 
HALF_TILE_SIZE = TILE_SIZE / 2

# Dimensions de la carte en pixels
MAP_WIDTH = 120 * TILE_SIZE  
MAP_HEIGHT = 120 * TILE_SIZE 

# Niveaux de zoom
MIN_ZOOM = 0.3
MAX_ZOOM = 3.0

# Dimensions de la fenêtre en pixels
WINDOW_WIDTH = 1200  # Ajustez selon vos besoins
WINDOW_HEIGHT = 1200  # Ajustez selon vos besoins

# Nombre de tuiles de chaque type
NUM_GOLD_TILES = 500
NUM_WOOD_TILES = 500
NUM_FOOD_TILES = 500

# Difficulté du jeu
DIFFICULTY = 'DEBUG'

# Spawn gold centre
GOLD_SPAWN_MIDDLE = False

# Minimap settings
MINIMAP_WIDTH = 600  # Largeur de la minimap
MINIMAP_HEIGHT = 280  # Hauteur de la minimap
MINIMAP_MARGIN = 20   # Marge de la minimap

# Nombre de joueurs 
NUMBER_OF_PLAYERS = 2 

# Autres constantes
MAP_PADDING = 650

# Répertoire de sauvegarde
SAVE_DIRECTORY = 'saves'

# Assurez-vous que le répertoire de sauvegarde existe
import os
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

####################

# -------------------
# Configuration Animation
# -------------------
FRAMES_PER_UNIT = 10
