import pygame
from Settings.setup import (
    TILE_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MINIMAP_MARGIN
)

# Configuration for sprites
sprite_config = {
    'grass': {
        'filepath': 'assets/grass/grass7-min.png',
        'scale': (TILE_SIZE + 35, TILE_SIZE // 2 + 25)
    },
    'gold': {
        'filepath': 'assets/gold/gold1-min.png',
        'scale': (TILE_SIZE, TILE_SIZE)
    },
    'mountain': {
        'filepath': 'assets/mountain/mountain1-min.png',
        'scale': (TILE_SIZE, TILE_SIZE)
    },
    'wood': {
        'filepath': 'assets/tree/tree_oak/tree1-min.png',
        'scale': (TILE_SIZE, TILE_SIZE)
    }
}

# Dictionary to store each sprite
sprites = {}
# Cache for scaled sprites at different zoom levels
zoom_cache = {}

def load_sprites():
    for name, settings in sprite_config.items():
        load_sprite(name, settings['filepath'], *settings['scale'])

def load_sprite(name, filepath, scale_width, scale_height):
    sprite = pygame.image.load(filepath).convert_alpha()  # Use convert_alpha for better performance
    sprite = pygame.transform.scale(sprite, (scale_width, scale_height))
    sprites[name] = sprite

def get_scaled_sprite(sprite_name, zoom):
    if sprite_name not in zoom_cache:
        zoom_cache[sprite_name] = {}
    
    if zoom not in zoom_cache[sprite_name]:
        original_image = sprites[sprite_name]
        scaled_width = int(original_image.get_width() * zoom)
        scaled_height = int(original_image.get_height() * zoom)
        scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
        zoom_cache[sprite_name][zoom] = scaled_image
    
    return zoom_cache[sprite_name][zoom]

def draw_sprite(screen, sprite_name, screen_x, screen_y, zoom):
    scaled_sprite = get_scaled_sprite(sprite_name, zoom)
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    
    # Draw the scaled image centered at the position
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'grass', screen_x, screen_y, camera.zoom)

def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type != 'food' and terrain_type != 'grass':
        draw_sprite(screen, terrain_type, screen_x, screen_y, camera.zoom)
