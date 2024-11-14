import pygame
from Settings.setup import (
    TILE_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MINIMAP_MARGIN
)

# Dictionary to store each sprite and its dimensions
sprites = {}
# Cache for scaled sprites at different zoom levels
zoom_cache = {}

def load_sprites():
    load_sprite('grass', 'assets/grass/grass7.png', TILE_SIZE+35, TILE_SIZE//2 + 25)
    load_sprite('gold', 'assets/gold/gold1.png')
    load_sprite('mountain', 'assets/mountain/mountain1.png')
    load_sprite('wood', 'assets/tree/tree_oak/tree1.png')

def load_sprite(name, filepath, scale_width=TILE_SIZE, scale_height=TILE_SIZE):
    sprite = pygame.image.load(filepath)
    sprite = pygame.transform.scale(sprite, (scale_width, scale_height))
    width, height = sprite.get_size()
    sprites[name] = {"image": sprite, "width": width, "height": height}

def get_scaled_sprite(sprite, zoom):
    if sprite not in zoom_cache:
        # Store the original high-quality sprite
        zoom_cache[sprite] = {"original": sprites[sprite]["image"]}
    
    if zoom not in zoom_cache[sprite]:
        # Scale from the original high-resolution sprite for best quality
        original_image = zoom_cache[sprite]["original"]
        scaled_width = int(sprites[sprite]["width"] * zoom)
        scaled_height = int(sprites[sprite]["height"] * zoom)
        scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
        zoom_cache[sprite][zoom] = scaled_image
    
    return zoom_cache[sprite][zoom]


def draw_sprite(screen, sprite_name, screen_x, screen_y, zoom):
    if sprite_name not in sprites:
        raise Exception("Sprite not loaded. Call load_sprites() before drawing.")
    
    # Get the cached scaled sprite
    scaled_sprite = get_scaled_sprite(sprite_name, zoom)
    scaled_width, scaled_height = scaled_sprite.get_size()
    
    # Draw the scaled image centered at the position
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'grass', screen_x, screen_y, camera.zoom)

def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type != 'food':
        draw_sprite(screen, terrain_type, screen_x, screen_y, camera.zoom)
