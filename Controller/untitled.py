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
    0 : blue 
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
            'animation_types': 3  # Animated sprite with 3 animation types
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

# Function to parse sprite filenames according to the pattern
def parse_sprite_filename(filename):
    # Regex pattern to match the filename structure
    pattern = r'(\d+)_(\d+)x(\d+)_(\w+)\.(png|jpeg|jpg)'
    match = re.match(pattern, filename)
    if match:
        team_number = int(match.group(1))
        animation_type = int(match.group(2))
        frame_id = int(match.group(3))
        object_name = match.group(4)
        return team_number, animation_type, frame_id, object_name
    else:
        return None

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
        for key, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')
            # Check if 'animation_types' is specified
            if 'animation_types' in value:
                # Animated sprite
                sprites[category][key] = {}
                try:
                    filenames = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for filename in filenames:
                    if filename.lower().endswith((".jpeg", ".jpg", ".png")):
                        parsed = parse_sprite_filename(filename)
                        if parsed:
                            team_number, animation_type, frame_id, object_name = parsed
                            # Ensure the object name matches the key
                            if object_name != key:
                                continue

                            # Load the sprite
                            filepath = os.path.join(directory, filename)
                            sprite = load_sprite(filepath, scale, adjust)

                            # Organize the sprite in the nested dictionary
                            team_dict = sprites[category][key].setdefault(team_number, {})
                            animation_dict = team_dict.setdefault(animation_type, [])

                            # Insert the sprite at the correct frame index
                            if frame_id >= len(animation_dict):
                                # Extend the list to accommodate the new frame index
                                animation_dict.extend([None] * (frame_id - len(animation_dict) + 1))
                            animation_dict[frame_id] = sprite
                        else:
                            print(f"Filename does not match the expected pattern: {filename}")
            else:
                # Static sprite
                sprites[category][key] = []
                try:
                    filenames = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for filename in filenames:
                    if filename.lower().endswith((".jpeg", ".jpg", ".png")):
                        filepath = os.path.join(directory, filename)
                        sprite = load_sprite(filepath, scale, adjust)
                        sprites[category][key].append(sprite)  # Append sprite to list

    print("Sprites loaded successfully.")

# Function to get a scaled sprite, handling both static and animated sprites
def get_scaled_sprite(sprite_name, zoom, variant=0, team_number=0, animation_type=0, frame_id=0):
    section, name = sprite_name.split('/')  # Assuming sprite_name format as 'category/name'
    sprite_data = sprites[section][name]

    # Determine if sprite is animated or static
    if isinstance(sprite_data, dict):
        # Animated sprite
        try:
            original_image = sprite_data[team_number][animation_type][frame_id]
        except KeyError:
            print(f"Sprite not found for {section} '{name}', team {team_number}, animation type {animation_type}, frame {frame_id}")
            return None
        cache_key = (zoom, team_number, animation_type, frame_id)
    else:
        # Static sprite
        if not sprite_data:
            print(f"No sprites available for {section} '{name}'")
            return None
        original_image = sprite_data[variant % len(sprite_data)]  # Use variant to select sprite
        cache_key = (zoom, variant)

    # Use zoom_cache to store scaled images
    if name not in zoom_cache:
        zoom_cache[name] = {}
    if cache_key not in zoom_cache[name]:
        scaled_width = int(original_image.get_width() * zoom)
        scaled_height = int(original_image.get_height() * zoom)
        scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
        zoom_cache[name][cache_key] = scaled_image
    return zoom_cache[name][cache_key]

# Function to draw a sprite on the screen
def draw_sprite(screen, sprite_name, screen_x, screen_y, zoom, variant=0, team_number=0, animation_type=0, frame_id=0):
    scaled_sprite = get_scaled_sprite(sprite_name, zoom, variant, team_number, animation_type, frame_id)
    if scaled_sprite is None:
        return  # Unable to get sprite
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

# Adjusted function to draw buildings, iterating through animated sprites
def draw_building(building, screen, screen_x, screen_y, camera, team=0, buildings_acronym=buildings_acronym):
    building_name = buildings_acronym[building.acronym]
    sprite_name = f'buildings/{building_name}'
    building_config = sprite_config['buildings'][building_name]

    if 'animation_types' in building_config:
        # Animated building
        animation_type = building.state  # Current animation type
        team_number = 1
        sprites_dict = sprites['buildings'][building_name]
        total_frames = len(sprites_dict[team_number][animation_type])

        # Update frame for animation
        frame_duration = building.frame_duration  # Duration each frame is displayed
        building.frame_counter += 1
        if building.frame_counter >= frame_duration:
            building.frame_counter = 0
            building.current_frame = (building.current_frame + 1) % total_frames

        # Draw the current frame of the animation
        draw_sprite(screen, sprite_name, screen_x, screen_y, camera.zoom,
                    team_number=team_number, animation_type=animation_type, frame_id=building.current_frame)
    else:
        # Static building
        variant = team  # Optionally use team as variant if you have different sprites per team
        draw_sprite(screen, sprite_name, screen_x, screen_y, camera.zoom, variant=variant)

# Function to fill the background with grass tiles
def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'terrain/grass', screen_x, screen_y, camera.zoom)

# Function to draw terrain elements like wood and gold
def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type in ['wood', 'gold']:  # Ensure we only draw known terrain types
        draw_sprite(screen, f'terrain/{terrain_type}', screen_x, screen_y, camera.zoom)

