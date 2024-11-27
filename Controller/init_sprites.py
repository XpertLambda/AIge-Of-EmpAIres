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

buildings_acronym = {
    'A' : 'archeryrange',
    'B' : 'barracks',
    'C' : 'camp',
    'F' : 'farm',
    'H' : 'house',
    'K' : 'keep',
    'S' : 'stable',
    'T' : 'towncenter'
}
sprite_config = {
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'adjust_scale' : TILE_SIZE/400  #400 to match the grass sprite
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'adjust_scale' : TILE_SIZE/400
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'adjust_scale' : TILE_SIZE/400
        },
        'archeryrange': {
            'directory': 'assets/buildings/archeryrange/',
            'adjust_scale' : TILE_SIZE/400
        },
        'keep': {
            'directory': 'assets/buildings/keep/',
            'adjust_scale' : TILE_SIZE/400
        },
        'camp': {
            'directory': 'assets/buildings/camp/',
            'adjust_scale' : TILE_SIZE/400
        },
        'house': {
            'directory': 'assets/buildings/house/',
            'adjust_scale' : TILE_SIZE/400
        }
    },
    'terrain': {
        'grass': {
            'directory': 'assets/terrain/grass/',
            'scale': (TILE_SIZE // 2, TILE_SIZE // 4)
        },
        'gold': {
            'directory': 'assets/terrain/gold/',
            'scale': (TILE_SIZE, TILE_SIZE)
        },
        'wood': {
            'directory': 'assets/terrain/tree/',
            'scale': (TILE_SIZE, TILE_SIZE)
        }
    },
    'units': {
        'archer': {
            'directory': 'assets/units/',
            'scale': (60, 60)
        },
        'knight': {
            'directory': 'assets/units/',
            'scale': (60, 60)
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
        sprite = pygame.transform.scale(sprite, scale)
    if adjust:
        sprite = pygame.transform.scale(sprite, (sprite.get_width() * adjust, sprite.get_height() * adjust))
    return sprite

# Updated function to load sprites
def load_sprites(sprite_config=sprite_config):
    for section in sprite_config:
        sprites[section] = {}
        for key, value in sprite_config[section].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')
            sprites[section][key] = [load_sprite(os.path.join(directory, filename), scale, adjust)
                                     for filename in os.listdir(directory) if filename.endswith(".jpeg") or filename.endswith(".png")]
    return sprites

def get_scaled_sprite(sprite_name, zoom, variant=0):
    section, name = sprite_name.split('/')  # Assuming sprite_name format as 'section/name'
    if name not in zoom_cache:
        zoom_cache[name] = {}

    cache_key = (zoom, variant)
    if cache_key not in zoom_cache[name]:
        sprites_list = sprites[section][name]
        original_image = sprites_list[variant % len(sprites_list)]  # Ensure variant index is within bounds
        scaled_width = int(original_image.get_width() * zoom)
        scaled_height = int(original_image.get_height() * zoom)
        scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
        zoom_cache[name][cache_key] = scaled_image

    return zoom_cache[name][cache_key]

def draw_sprite(screen, sprite_name, screen_x, screen_y, zoom, variant=0):
    scaled_sprite = get_scaled_sprite(sprite_name, zoom, variant)
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'terrain/grass', screen_x, screen_y, camera.zoom)

def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type in ['wood', 'gold' ]:  # Make sure to only draw known terrain types
        draw_sprite(screen, f'terrain/{terrain_type}', screen_x, screen_y, camera.zoom)

def draw_building(building, screen, screen_x, screen_y, camera, team, buildings_acronym=buildings_acronym):
    draw_sprite(screen, f'buildings/{buildings_acronym[building.acronym]}',screen_x, screen_y, camera.zoom, team)
