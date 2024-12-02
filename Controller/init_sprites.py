import re
import pygame
import os
from collections import OrderedDict
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

units_acronym = {
    'A' : 'archer',
    'H' : 'horseman',
    'S' : 'swordsman',
    'V' : 'villager'
}

teams = {
    0 : 'blue',
    1 : 'red' 
}

states = {
    0 : 'idle',
    1 : 'walk',
    2 : 'attack',
    3 : 'death'
}



# Configuration for sprites
sprite_config = {
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'adjust_scale': TILE_SIZE / 400  # 400 to match the grass sprite
            # No 'states' field; it's a static sprite
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'adjust_scale': TILE_SIZE / 400
            # Static sprite
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'adjust_scale': TILE_SIZE / 400,
            #'states': 3  # Animated sprite with 3 animation types
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
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config' : {
                'columns' : 30,
                'rows' : 16        
            },
        },
        'villager': {
            'directory': 'assets/units/villager/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config' : {
                'columns' : 30,
                'rows' : 16        
            },
        },
        'archer': {
            'directory': 'assets/units/archer/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config' : {
                'columns' : 30,
                'rows' : 16        
            },
        }
    }
}

# Dictionary to store each sprite
sprites = {}
# Cache for scaled sprites at different zoom levels
zoom_cache = {}
MAX_ZOOM_CACHE_PER_SPRITE = 60

# Function to load a sprite with conditional scaling
def load_sprite(filepath=None, scale=None, adjust=None):
    if filepath:
        sprite = pygame.image.load(filepath).convert_alpha()  # Load the image with transparency
    if scale:
        sprite = pygame.transform.scale(sprite, (int(scale[0]), int(scale[1])))
    if adjust:
        sprite = pygame.transform.scale(sprite, (
            int(sprite.get_width() * adjust),
            int(sprite.get_height() * adjust)
        ))
    return sprite
# Extracts frames from a sprite sheet based on rows and columns, and scales them by a factor.
def extract_frames(sheet, rows, columns, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()

    # Calculate frame dimensions
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows

    # Calculate new frame dimensions based on the scaling factor
    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)
    for row in range(rows):
        for col in range(columns):
            # Compute the position of the frame in the sprite sheet
            if col%3==0:
                x = col * frame_width
                y = row * frame_height

                # Extract the frame
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                
                # Resize frame to the new dimensions
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
            else :
                continue
    return frames


# Function to load sprites, handling both static and animated sprites
def load_sprites(sprite_config=sprite_config):
    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')
            
            if 'sheet_config' in sprite_config[category][sprite_name]:
                sheet_cols = sprite_config[category][sprite_name]['sheet_config'].get('columns', 0)
                sheet_rows = sprite_config[category][sprite_name]['sheet_config'].get('rows', 0)

            if category == 'terrain':
                # Initialize terrain category
                sprites[category][sprite_name] = []

                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for filename in dir_content:
                    if filename.lower().endswith(("webp")):
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
                        if filename.lower().endswith(("webp")):
                            filepath = os.path.join(team_path, filename)
                            sprite = load_sprite(filepath, scale, adjust)
                            sprites[category][sprite_name][team].append(sprite)  # Append sprite to list
            elif category == 'units' :
                #Uncomment this continue to get faster loading
                #continue

                # Initialize buildings category
                sprites[category][sprite_name] = {}
                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    return

                for team in dir_content:
                    team_path = os.path.join(directory, team)
                    if not os.path.isdir(team_path):
                        continue
                    sprites[category][sprite_name].setdefault(team, {})

                    try:
                        team_content = os.listdir(team_path)
                    except FileNotFoundError:
                        continue

                    for state in team_content:
                        state_path = os.path.join(team_path, state)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name][team].setdefault(state, [])

                        try:
                            state_content = os.listdir(state_path)
                        except FileNotFoundError:
                            continue

                        for sheetname in state_content:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath)
                                    frames = extract_frames(sprite_sheet, sheet_rows, sheet_cols)
                                    sprites[category][sprite_name][team][state].extend(frames)
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")
                                    print(f"info : category : {category}, sprite_name : {sprite_name}, team : {team}, state : {state}")
                                    exit()        
    print("Sprites loaded successfully.")

# Function to get a scaled sprite, handling both static and animated sprites
def get_scaled_sprite(name, category, zoom, team=None, state=None, frame_id=0):
    cache_key = (zoom, frame_id, team, state)
    
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()
    
    if cache_key in zoom_cache[name]:
        # Move to end to show it's recently used
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]
    # Load and scale the sprite
    if category == 'terrain':
        sprite_data = sprites[category][name]
    elif category == 'buildings':
        sprite_data = sprites[category][name][team]
    elif category == 'units':
        sprite_data = sprites[category][name][team][state]
    
    original_image = sprite_data[frame_id]
    scaled_width = int(original_image.get_width() * zoom)
    scaled_height = int(original_image.get_height() * zoom)
    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
    
    # Add to cache
    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)
    
    # Evict least recently used if over capacity
    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image


# Function to draw a sprite on the screen
def draw_sprite(screen, name, category, screen_x, screen_y, zoom, team=None, state=None, frame_id=0):
    scaled_sprite = get_scaled_sprite(name, category, zoom, team, state, frame_id)
    if scaled_sprite is None:
        return  # Unable to get sprite
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

# Function to fill the background with grass tiles
def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'grass', 'terrain', screen_x, screen_y, camera.zoom)

# Function to draw terrain elements like wood and gold
def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type in ['wood', 'gold']:  # Ensure we only draw known terrain types
        draw_sprite(screen, f'{terrain_type}', 'terrain', screen_x, screen_y, camera.zoom)

# Adjusted function to draw buildings, iterating through animated sprites
def draw_building(building, screen, screen_x, screen_y, camera, team_number=0, buildings_acronym=buildings_acronym):
    name = buildings_acronym[building.acronym]
    team = teams[team_number]
    category = 'buildings'
    draw_sprite(screen, name, category, screen_x, screen_y, camera.zoom, team=team)

def draw_unit(unit, screen, screen_x, screen_y, camera, team_number=0, units_acronym=units_acronym):
    category = 'units'
    name = units_acronym[unit.acronym]
    team = teams[team_number]
    state = states[unit.state]

    # Animated unit
    sprites_dict = sprites[category][name][team][state]
    total_frames = 10

    # Update frame for animation
    frame_duration = unit.frame_duration  # Duration each frame is displayed
    unit.frame_counter += 1
    if unit.frame_counter >= frame_duration:
        unit.frame_counter = 0
        unit.current_frame = (unit.current_frame + 1) % total_frames
    # Draw the current frame of the animation
    draw_sprite(screen, name, category, screen_x, screen_y, camera.zoom, team, state, unit.current_frame)

