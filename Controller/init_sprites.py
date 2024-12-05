# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/Projet_python\Controller\init_sprites.py
# Controller/init_sprites.py

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

sprite_config = {
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'adjust_scale': TILE_SIZE / 400  
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'adjust_scale': TILE_SIZE / 400
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'adjust_scale': TILE_SIZE / 400,
        },
        'archeryrange': {
            'directory': 'assets/buildings/archeryrange/',
            'adjust_scale': TILE_SIZE / 400
        },
        'keep': {
            'directory': 'assets/buildings/keep/',
            'adjust_scale': TILE_SIZE / 400
        },
        'camp': {
            'directory': 'assets/buildings/camp/',
            'adjust_scale': TILE_SIZE / 400
        },
        'house': {
            'directory': 'assets/buildings/house/',
            'adjust_scale': TILE_SIZE / 400
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

sprites = {}
zoom_cache = {}
MAX_ZOOM_CACHE_PER_SPRITE = 60

def load_sprite(filepath=None, scale=None, adjust=None):
    if filepath:
        sprite = pygame.image.load(filepath).convert_alpha()
    if scale:
        sprite = pygame.transform.scale(sprite, (int(scale[0]), int(scale[1])))
    if adjust:
        sprite = pygame.transform.scale(sprite, (
            int(sprite.get_width() * adjust),
            int(sprite.get_height() * adjust)
        ))
    # Conversion en format interne optimisé
    sprite = sprite.convert_alpha()
    return sprite

def extract_frames(sheet, rows, columns, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()

    frame_width = sheet_width // columns
    frame_height = sheet_height // rows

    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)
    for row in range(rows):
        for col in range(columns):
            if col%3==0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.scale(frame, (target_width, target_height))
                frame = frame.convert_alpha()
                frames.append(frame)
    return frames

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
                sprites[category][sprite_name] = []
                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for filename in dir_content:
                    if filename.lower().endswith("webp"):
                        filepath = os.path.join(directory, filename)
                        sprite = load_sprite(filepath, scale, adjust)
                        sprites[category][sprite_name].append(sprite)

            elif category == 'buildings':
                sprites[category][sprite_name] = {}
                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for team in dir_content:
                    team_path = os.path.join(directory, team)
                    if not os.path.isdir(team_path):
                        continue
                    if team not in sprites[category][sprite_name]:
                        sprites[category][sprite_name][team] = []
                    try:
                        team_content = os.listdir(team_path)
                    except FileNotFoundError:
                        continue

                    for filename in team_content:
                        if filename.lower().endswith("webp"):
                            filepath = os.path.join(team_path, filename)
                            sprite = load_sprite(filepath, scale, adjust)
                            sprites[category][sprite_name][team].append(sprite)

            elif category == 'units':
                # Pour le moment, on ne charge pas les unités au complet pour gain de performance.
                # Laisser en l'état ou décommenter pour tests.
                continue

    print("Sprites loaded successfully.")

def get_scaled_sprite(name, category, zoom, team=None, state=None, frame_id=0):
    cache_key = (zoom, frame_id, team, state)
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()
    if cache_key in zoom_cache[name]:
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]

    if category == 'terrain':
        sprite_data = sprites[category][name]
    elif category == 'buildings':
        sprite_data = sprites[category][name][team]
    elif category == 'units':
        sprite_data = sprites[category][name][team][state]

    original_image = sprite_data[frame_id]
    scaled_width = int(original_image.get_width() * zoom)
    scaled_height = int(original_image.get_height() * zoom)
    scaled_image = pygame.transform.scale(original_image, (scaled_width, scaled_height))
    scaled_image = scaled_image.convert_alpha()

    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)
    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image

def draw_sprite(screen, name, category, screen_x, screen_y, zoom, team=None, state=None, frame_id=0):
    scaled_sprite = get_scaled_sprite(name, category, zoom, team, state, frame_id)
    if scaled_sprite is None:
        return
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, 'grass', 'terrain', screen_x, screen_y, camera.zoom)

def draw_terrain(terrain_type, screen, screen_x, screen_y, camera):
    if terrain_type in ['wood', 'gold']:
        draw_sprite(screen, f'{terrain_type}', 'terrain', screen_x, screen_y, camera.zoom)

def draw_building(building, screen, screen_x, screen_y, camera, team_number=0, buildings_acronym=buildings_acronym):
    name = buildings_acronym[building.acronym]
    team = teams[team_number]
    category = 'buildings'
    # On dessine un seul sprite statique
    sprite_data = sprites[category][name][team]
    # On suppose qu'il y a un sprite unique, sprite_data[0]
    original_image = sprite_data[0]
    # Pas de scale ici, on scale à l'appelant si nécessaire
    screen.blit(original_image, (screen_x - original_image.get_width() // 2, screen_y - original_image.get_height() // 2))

def draw_unit(unit, screen, screen_x, screen_y, camera, team_number=0, units_acronym=units_acronym):
    category = 'units'
    name = units_acronym[unit.acronym]
    team = teams[team_number]
    state = states[unit.state]

    # Cette partie reste non-implémentée pour réduire la charge, comme auparavant
    # Si vous voulez gérer les unités, vous pouvez implémenter la logique comme avant,
    # ici on assume un rendu minimal ou statique pour les performances.
    # Exemple: ne rien dessiner ou dessiner un carré simple.
    color = (255, 0, 0) if team_number == 0 else (0, 0, 255)
    pygame.draw.rect(screen, color, (screen_x - 5, screen_y - 5, 10, 10))

