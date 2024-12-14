# Controller/init_sprites.py
# Modifications pour afficher les mêmes sprites pour tous les joueurs
# On choisit arbitrairement la couleur "blue" pour tous.
# On ignore le paramètre team et on charge toujours les sprites "blue".

import re
import pygame
import os
import time
from collections import OrderedDict
from Settings.setup import *



Entity_Acronym = {
    'resources': {
        ' ': 'grass',
        'W': 'wood',
        'G': 'gold',
        'F': 'food'
    },
    'buildings': {
        'A': 'archeryrange',
        'B': 'barracks',
        'C': 'camp',
        'F': 'farm',
        'H': 'house',
        'K': 'keep',
        'S': 'stable',
        'T': 'towncenter'
    },
    'units': {
        'a': 'archer',
        'h': 'horseman',
        's': 'swordsman',
        'v': 'villager'
    }
}

# On n'utilise plus l'info team pour choisir les sprites
# Tous les sprites seront ceux du répertoire "blue"
fixed_team_folder = 'blue'
fixed_state = 'idle'  # On garde la logique d'états si besoin, sinon "idle".

states = {
    0 : 'idle',
    1 : 'walk',
    2 : 'attack',
    3 : 'death'
}


sprite_loading_screen = {
    'loading_screen':{
        'directory': 'assets/launcher/',
        'scale':None
    }
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
    'resources': {
        'grass': {
            'directory': 'assets/resources/grass/',
            'scale': (10 * TILE_SIZE // 2, 10 * TILE_SIZE // 4)
        },
        'gold': {
            'directory': 'assets/resources/gold/',
            'scale': (TILE_SIZE, TILE_SIZE)
        },
        'wood': {
            'directory': 'assets/resources/tree/',
            'scale': (TILE_SIZE, TILE_SIZE)
        },
        'food': {
            'directory': 'assets/resources/food/',
            'scale': (TILE_SIZE, TILE_SIZE)
        }
    },
    'units': {
        'swordsman': {
            'directory': 'assets/units/swordsman/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'villager': {
            'directory': 'assets/units/villager/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'archer': {
            'directory': 'assets/units/archer/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        }
    }
}

sprites = {}
zoom_cache = {}
MAX_ZOOM_CACHE_PER_SPRITE = 60

grass_group = pygame.sprite.Group()

def load_sprite(filepath=None, scale=None, adjust=None):
    if filepath:
        sprite = pygame.image.load(filepath).convert_alpha()
    if scale:
        sprite = pygame.transform.smoothscale(sprite, (int(scale[0]), int(scale[1])))
    if adjust:
        sprite = pygame.transform.smoothscale(sprite, (
            int(sprite.get_width() * adjust),
            int(sprite.get_height() * adjust)
        ))
    sprite = sprite.convert_alpha()
    return sprite

def extract_frames(sheet, rows, columns, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows
    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)

    frame_step = columns // FRAMES_PER_UNIT
    for row in range(rows):
        for col in range(columns):
            if col % frame_step == 0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
    return frames

def draw_progress_bar(screen, progress, screen_width, screen_height, loading_text):
    bar_width = screen_width * 0.8
    bar_height = 30
    bar_x = (screen_width - bar_width) / 2
    bar_y = screen_height * 0.6

    # Effacer la zone de la barre de progression
    pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height))

    # Dessiner la barre de progression
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width * progress, bar_height))

    # Afficher le pourcentage
    font = pygame.font.Font(None, 36)
    text = font.render(f"{int(progress * 100)}%", True, (255, 255, 255))
    text_rect = text.get_rect(center=(bar_x + bar_width / 2, bar_y + bar_height / 2))

    # Déterminer la couleur du texte en fonction de la position de la barre de progression
    if progress >=0.5:
        text_color = (0, 0, 0)  # Noir
    else:
        text_color = (255, 255, 255)  # Blanc

    text = font.render(f"{int(progress * 100)}%", True, text_color)
    screen.blit(text, text_rect)

    # Afficher le texte "Loading..."
    loading_text_surface = font.render(loading_text, True, (0, 0, 0))
    loading_text_rect = loading_text_surface.get_rect(midleft=(bar_x + 10, bar_y + bar_height / 2))
    screen.blit(loading_text_surface, loading_text_rect)

    pygame.display.flip()



def load_sprites(screen,screen_width,screen_height, sprite_config=sprite_config, sprite_loading_screen=sprite_loading_screen):
    total_files = sum(len(files) for _, _, files in os.walk('assets'))
    loaded_files = 0
    loading_text = "Loading..."
    for category, value in sprite_loading_screen.items():
        directory = value.get('directory')
        scale = (screen_width, screen_height)
        try:
            dir_content = os.listdir(directory)
        except FileNotFoundError:
            print(f"Directory not found: {directory}")
            continue

        for filename in dir_content:
            if filename.lower().endswith("webp"):
                filepath = os.path.join(directory, filename)
                sprite = load_sprite(filepath, scale)
                print(f'--> Loaded {filename} of type: {category}')
                # Afficher l'écran de chargement
                if category == 'loading_screen':
                    screen.blit(sprite, (0, 0))
                    pygame.display.flip()
                loaded_files += 1
                progress = loaded_files / total_files
                draw_progress_bar(screen, progress, screen_width, screen_height,loading_text)
                

    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')

            if 'sheet_config' in sprite_config[category][sprite_name]:
                sheet_cols = sprite_config[category][sprite_name]['sheet_config'].get('columns', 0)
                sheet_rows = sprite_config[category][sprite_name]['sheet_config'].get('rows', 0)

            if category == 'resources':
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
                        sprites[category][sprite_name].append(sprite)  # Append sprite to list
                        print(f'--> Loaded {sprite_name} of type : {category}')
                        loaded_files += 1
                        progress = loaded_files / total_files
                        draw_progress_bar(screen, progress, screen_width, screen_height,loading_text)
                        
            elif category == 'buildings':
                # On ne charge que le dossier "blue"
                sprites[category][sprite_name] = []
                team_path = os.path.join(directory, fixed_team_folder)
                if os.path.isdir(team_path):
                    team_content = os.listdir(team_path)
                    for filename in team_content:
                        if filename.lower().endswith("webp"):
                            filepath = os.path.join(team_path, filename)
                            sprite = load_sprite(filepath, scale, adjust)
                            sprites[category][sprite_name].append(sprite)  # Append sprite to list
                            loaded_files += 1
                            progress = loaded_files / total_files
                            draw_progress_bar(screen, progress, screen_width, screen_height,loading_text)
                            
                    print(f'--> Loaded {sprite_name}, type : {category}')

            elif category == 'units':
                # On ne charge que le dossier "blue"
                sprites[category][sprite_name] = {}
                team_path = os.path.join(directory, fixed_team_folder)
                if os.path.isdir(team_path):
                    # On charge tous les états disponibles
                    team_content = os.listdir(team_path)
                    for state_dir in team_content:
                        state_path = os.path.join(team_path, state_dir)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name].setdefault(state_dir, [])
                        state_content = os.listdir(state_path)
                        for sheetname in state_content:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath)
                                    frames = extract_frames(sprite_sheet, sheet_rows, sheet_cols)
                                    sprites[category][sprite_name][state_dir].extend(frames)
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")
                                    print(f"info : category : {category}, sprite_name : {sprite_name}, state : {state}")
                                    exit() 
                                loaded_files += 1
                                progress = loaded_files / total_files
                                draw_progress_bar(screen, progress, screen_width, screen_height,loading_text)
                                
                loaded_files += 1
                progress = loaded_files / total_files
                draw_progress_bar(screen, progress, screen_width, screen_height,loading_text)
                
                print(f'--> Loaded {sprite_name}, type : {category}')
    print("Sprites loaded successfully.")
# Function to get a scaled sprite, handling both static and animated sprites
def get_scaled_sprite(name, category, zoom, state, frame_id):
    cache_key = (zoom, frame_id, state)  # Removed 'team' from cache_key
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()

    if cache_key in zoom_cache[name]:
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]

    if category == 'resources':
        sprite_data = sprites[category][name]
        original_image = sprite_data[frame_id % len(sprite_data)]
    elif category == 'buildings':
        sprite_data = sprites[category][name]
        original_image = sprite_data[frame_id % len(sprite_data)]
    elif category == 'units':
        if state is None:
            state = fixed_state
        sprite_data = sprites[category][name][state]
        original_image = sprite_data[frame_id % len(sprite_data)]

    scaled_width = int(original_image.get_width() * zoom)
    scaled_height = int(original_image.get_height() * zoom)
    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
    
    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)
    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image

def draw_sprite(screen, acronym, category, screen_x, screen_y, zoom, state=None, frame_id=0):
    # On ignore team et on force l'utilisation des sprites "blue".
    # On garde la gestion de l'état si elle est définie, sinon "idle"
    if state is not None:
        state = states[state]
    else:
        state = fixed_state

    name = Entity_Acronym[category][acronym]
    scaled_sprite = get_scaled_sprite(name, category, zoom, state, frame_id)
    if scaled_sprite is None:
        return
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, ' ', 'resources', screen_x, screen_y, camera.zoom)
