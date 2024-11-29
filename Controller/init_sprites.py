import re
import pygame
import os
from Settings.setup import (
    TILE_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MINIMAP_MARGIN
)

# Mapping of building acronyms to their full names
buildings_acronym = {
    'A': 'archeryrange',
    'B': 'barracks',
    'C': 'camp',
    'F': 'farm',
    'H': 'house',
    'K': 'keep',
    'S': 'stable',
    'T': 'towncenter'
}

teams_acronym = {
    0 : 'blue',
    1 : 'red' 
}

# Configuration for sprites
sprite_config = {
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'adjust_scale': TILE_SIZE / 400  # 400 to match the grass sprite
            # No 'animation_types' field; it's a static sprite
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'adjust_scale': TILE_SIZE / 400
            # Static sprite
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'adjust_scale': TILE_SIZE / 400,
            #'animation_types': 3  # Animated sprite with 3 animation types
        },
        'archeryrange': {
            'directory': 'assets/buildings/archeryrange/',
            'adjust_scale': TILE_SIZE / 400
            # Static sprite
        },
        'keep': {
            'directory': 'assets/buildings/keep/',
            'adjust_scale': TILE_SIZE / 400
            # Static sprite
        },
        'camp': {
            'directory': 'assets/buildings/camp/',
            'adjust_scale': TILE_SIZE / 400
            # Static sprite
        },
        'house': {
            'directory': 'assets/buildings/house/',
            'adjust_scale': TILE_SIZE / 400
            # Static sprite
        }
    },
    'terrain': {
        'grass': {
            'directory': 'assets/terrain/grass/',
            'scale': (TILE_SIZE // 2, TILE_SIZE // 4)
            # Static sprite
        },
        'gold': {
            'directory': 'assets/terrain/gold/',
            'scale': (TILE_SIZE, TILE_SIZE)
            # Static sprite
        },
        'wood': {
            'directory': 'assets/terrain/tree/',
            'scale': (TILE_SIZE, TILE_SIZE)
            # Static sprite
        }
    },
    'units': {
        'swordsman': {
            'directory': 'assets/units/swordsman/',
            'animation_types': 3
        },
        'knight': {
            'directory': 'assets/units/knight/',
            'scale': (60, 60),
            'animation_types': 3  # Animated unit
        }
    }
}

# Dictionary to store each sprite
sprites = {}
# Cache for scaled sprites at different zoom levels
zoom_cache = {}

# Function to load a sprite with conditional scaling
def load_sprite(filepath, scale=None, adjust=None):
    sprite = pygame.image.load(filepath).convert_alpha()  # Load the image with transparency
    if scale:
        sprite = pygame.transform.scale(sprite, (int(scale[0]), int(scale[1])))
    if adjust:
        sprite = pygame.transform.scale(sprite, (
            int(sprite.get_width() * adjust),
            int(sprite.get_height() * adjust)
        ))
    return sprite

# Function to load sprites, handling both static and animated sprites
def load_sprites(sprite_config=sprite_config):
    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')

            if category == 'terrain':
                # Initialize terrain category
                sprites[category][sprite_name] = []

                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for filename in dir_content:
                    if filename.lower().endswith((".jpeg", ".jpg", ".png")):
                        filepath = os.path.join(directory, filename)
                        sprite = load_sprite(filepath, scale, adjust)
                        sprites[category][sprite_name].append(sprite)  # Append sprite to list

            elif category == 'buildings':
                # Initialize buildings category
                sprites[category][sprite_name] = {}

                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for team in dir_content:
                    team_path = os.path.join(directory, team)
                    if not os.path.isdir(team_path):
                        print(f"Skipping non-directory: {team_path}")
                        continue

                    # Initialize team-specific dictionary
                    if team not in sprites[category][sprite_name]:
                        sprites[category][sprite_name][team] = []

                    try:
                        team_content = os.listdir(team_path)
                    except FileNotFoundError:
                        print(f"Directory not found: {team_path}")
                        continue

                    for filename in team_content:
                        if filename.lower().endswith((".jpeg", ".jpg", ".png")):
                            filepath = os.path.join(team_path, filename)
                            sprite = load_sprite(filepath, scale, adjust)
                            sprites[category][sprite_name][team].append(sprite)  # Append sprite to list
            else : 
                ## units loading
                continue
    print("Sprites loaded successfully.")

# Function to get a scaled sprite, handling both static and animated sprites
def get_scaled_sprite(name, category, zoom, variant=0, team=None, animation_type=0, frame_id=0):
    if category == 'terrain':
        sprite_data = sprites[category][name]
    elif category == 'buildings':
        sprite_data = sprites[category][name][team]
    else:
        # Handle other categories if necessary
        return None

    if not sprite_data:
        print(f"No sprites available for {category} '{name}'")
        return None

    original_image = sprite_data[variant % len(sprite_data)]  # Use variant to select sprite
    cache_key = (zoom, variant, team)

    # Use zoom_cache to store scaled images per team
    if name not in zoom_cache:
        zoom_cache[name] = {}
    if cache_key not in zoom_cache[name]:
        scaled_width = int(original_image.get_width() * zoom)
        scaled_height = int(original_image.get_height() * zoom)
        scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
        zoom_cache[name][cache_key] = scaled_image

    return zoom_cache[name][cache_key]


# Function to draw a sprite on the screen
def draw_sprite(screen, name, category, screen_x, screen_y, zoom, variant=0, team=None, animation_type=0, frame_id=0):
    scaled_sprite = get_scaled_sprite(name, category, zoom, variant, team, animation_type, frame_id)
    if scaled_sprite is None:
        return  # Unable to get sprite
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

# Adjusted function to draw buildings, iterating through animated sprites
def draw_building(building, screen, screen_x, screen_y, camera, team_number=0, buildings_acronym=buildings_acronym):
    name = buildings_acronym[building.acronym]
    team = teams_acronym[team_number]
    category = 'buildings'
    building_config = sprite_config[category][name]
    draw_sprite(screen, name, category, screen_x, screen_y, camera.zoom, team=team)

# Function to fill the background with grass tiles
def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'grass', 'terrain', screen_x, screen_y, camera.zoom)

# Function to draw terrain elements like wood and gold
def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type in ['wood', 'gold']:  # Ensure we only draw known terrain types
        draw_sprite(screen, f'{terrain_type}', 'terrain', screen_x, screen_y, camera.zoom)

