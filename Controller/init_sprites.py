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

sprite_config = {
    'buildings': {
        'castle': {
            'directory': 'assets/buildings/',
            'scale': (128, 128)
        },
        'barracks': {
            'directory': 'assets/buildings/',
            'scale': (100, 100)
        }
    },
    'terrain': {
        'grass': {
            'directory': 'assets/terrain/grass/',
            'scale': (TILE_SIZE + 35, TILE_SIZE // 2 + 25)
        },
        'mountain': {
            'directory': 'assets/terrain/mountain/',
            'scale': (TILE_SIZE, TILE_SIZE)
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

def load_sprite(filepath, scale):
    sprite = pygame.image.load(filepath).convert_alpha()  # Load and convert the image with transparency
    scaled_sprite = pygame.transform.scale(sprite, scale)  # Scale the image
    return scaled_sprite

def load_sprites(sprite_config=sprite_config):
    for section in sprite_config:
        sprites[section] = {}
        for key, value in sprite_config[section].items():
            directory = value['directory']
            scale = value['scale']
            sprites[section][key] = [load_sprite(os.path.join(directory, filename), scale)
                                     for filename in os.listdir(directory) if filename.endswith(".png")]
    return sprites

def get_scaled_sprite(sprite_name, zoom):
    section, name = sprite_name.split('/') # Assuming sprite_name format as 'section/name'
    if name not in zoom_cache:
        zoom_cache[name] = {}

    if zoom not in zoom_cache[name]:
        original_image = sprites[section][name][0]  # Assuming first sprite from the list for demonstration
        scaled_width = int(original_image.get_width() * zoom)
        scaled_height = int(original_image.get_height() * zoom)
        scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
        zoom_cache[name][zoom] = scaled_image

    return zoom_cache[name][zoom]

def draw_sprite(screen, sprite_name, screen_x, screen_y, zoom):
    scaled_sprite = get_scaled_sprite(sprite_name, zoom)
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'terrain/grass', screen_x, screen_y, camera.zoom)

def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type in ['mountain', 'wood', 'gold' ]:  # Make sure to only draw known terrain types
        draw_sprite(screen, f'terrain/{terrain_type}', screen_x, screen_y, camera.zoom)
