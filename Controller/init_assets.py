import re
import pygame
import os
import time
from collections import OrderedDict
from Settings.setup import *

sprites = {}
zoom_cache = {}
MAX_ZOOM_CACHE_PER_SPRITE = 60

gui_elements = {}
gui_cache = {}

ASSETS_LOADED = False  # Indique si tout est chargé
# On ajoute deux variables pour le suivi de progression
ASSETS_TOTAL = 1
ASSETS_LOADED_COUNT = 0

def get_assets_progress():
    """
    Renvoie un float [0..1] indiquant l'avancement du chargement.
    """
    global ASSETS_LOADED_COUNT, ASSETS_TOTAL
    return min(1.0, ASSETS_LOADED_COUNT / float(ASSETS_TOTAL))

def is_assets_loaded():
    return ASSETS_LOADED

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

def extract_Unitframes(sheet, rows, columns, frames_entity, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows
    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)

    frame_step = columns // frames_entity
    for row in range(rows):
        if row % 2 != 0:
            continue
        for col in range(columns):
            if col % frame_step == 0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
    return frames

def extract_Projectileframes(sheet, rows, columns, frames_entity, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows
    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)

    frame_step = columns // frames_entity
    for row in range(rows):
        for col in range(columns):
            if col % frame_step == 0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
    return frames

def extract_Buildingframes(sheet, rows, columns, frames_entity, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows
    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)

    frame_step = columns * rows // frames_entity
    # print(f'step {frame_step}, cols : {columns}, frames_entity : {frames_entity}')
    for row in range(rows):
        for col in range(columns):
            index = row * columns + col
            if index % frame_step == 0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
    return frames


def draw_progress_bar(screen, progress, screen_width, screen_height, progress_text, loading_screen_image):
    """
    Fonction déjà existante pour dessiner la barre de progression.
    """
    screen.blit(loading_screen_image, (
        screen_width // 2 - loading_screen_image.get_width() // 2,
        screen_height // 2 - loading_screen_image.get_height() // 2
    ))

    bar_width = screen_width * PROGRESS_BAR_WIDTH_RATIO
    bar_x = (screen_width - bar_width) / 2
    bar_y = screen_height * PROGRESS_BAR_Y_RATIO

    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, BAR_HEIGHT), 2, border_radius=BAR_BORDER_RADIUS)
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width * progress, BAR_HEIGHT), border_radius=BAR_BORDER_RADIUS)

    text_color = BLACK if progress >= 0.5 else WHITE

    font = pygame.font.Font(None, 36)
    percentage_text = font.render(f"{int(progress * 100)}%", True, text_color)

    percentage_text_rect = percentage_text.get_rect(center=(bar_x + bar_width / 2, bar_y + BAR_HEIGHT / 2))
    screen.blit(percentage_text, percentage_text_rect)

    progress_text_surface = font.render("Loading " + progress_text, True, WHITE)
    progress_text_rect = progress_text_surface.get_rect(centerx=(bar_x + bar_width / 2), top=(bar_y + BAR_HEIGHT))
    screen.blit(progress_text_surface, progress_text_rect)

    pygame.display.flip()

def resolve_asset_path(relative_path):
    """Helper function to resolve asset paths relative to project root"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)

def load_sprites(screen, screen_width, screen_height, show_progress=False):
    """
    Chargement complet des sprites (GUI, ressources, unités, bâtiments).
    show_progress=False => on ne dessine pas la barre de progression
                           (chargement en arrière-plan).
    """
    global ASSETS_LOADED, ASSETS_TOTAL, ASSETS_LOADED_COUNT
    if ASSETS_LOADED:
        return

    ASSETS_LOADED = False
    ASSETS_LOADED_COUNT = 0

    global gui_elements
    gui_elements.clear()

    # Calculate total files using absolute path
    total_files = sum(len(files) for _, _, files in os.walk(resolve_asset_path('assets')))
    ASSETS_TOTAL = max(1, total_files)

    loading_screen = None
    if show_progress:
        try:
            from Controller.init_assets import get_scaled_gui
            pass
        except:
            pass

    # --- CHARGEMENT GUI ---
    for gui_key, gui_val in gui_config.items():
        directory = gui_val.get('directory')
        gui_scale = gui_val.get('scale')
        gui_adjust_scale = gui_val.get('adjust_scale')
        if not directory:
            continue
        gui_elements[gui_key] = []
        
        # Use absolute path for directory
        abs_directory = resolve_asset_path(directory)
        try:
            dir_content = os.listdir(abs_directory)
        except FileNotFoundError:
            print(f"Directory not found: {abs_directory}")
            continue

        for filename in dir_content:
            if filename.lower().endswith("webp"):
                filepath = os.path.join(abs_directory, filename)
                loaded_sprite = load_sprite(filepath, gui_scale, gui_adjust_scale)
                gui_elements[gui_key].append(loaded_sprite)

                ASSETS_LOADED_COUNT += 1
                if show_progress:
                    from Controller.init_assets import draw_progress_bar
                    progress = get_assets_progress()
                    # On récupère l'écran de chargement (scalé) pour l'affichage
                    from Controller.init_assets import get_scaled_gui
                    loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=screen_height)
                    draw_progress_bar(screen, progress, screen_width, screen_height, gui_key, loading_screen)

    # --- CHARGEMENT SPRITES ---
    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            abs_directory = resolve_asset_path(directory)
            scale = value.get('scale')
            adjust = value.get('adjust_scale')
            if 'sheet_config' in value:
                sheet_cols = value['sheet_config'].get('columns', 0)
                sheet_rows = value['sheet_config'].get('rows', 0)

            if category in ['resources']:
                sprites[category][sprite_name] = []
                try:
                    dir_content = os.listdir(abs_directory)
                except FileNotFoundError:
                    print(f"Directory not found: {abs_directory}")
                    continue
                for filename in dir_content:
                    if filename.lower().endswith("webp"):
                        filepath = os.path.join(abs_directory, filename)
                        sprite = load_sprite(filepath, scale, adjust)
                        sprites[category][sprite_name].append(sprite)

                        ASSETS_LOADED_COUNT += 1
                        if show_progress:
                            from Controller.init_assets import draw_progress_bar
                            progress = get_assets_progress()
                            from Controller.init_assets import get_scaled_gui
                            loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=screen_height)
                            draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_screen)

            elif category == 'buildings':
                sprites[category][sprite_name] = {}
                sprite_path = abs_directory
                if os.path.isdir(sprite_path):
                    state_dirs = os.listdir(sprite_path)
                    for state_dir in state_dirs:
                        state_path = os.path.join(sprite_path, state_dir)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name].setdefault(state_dir, {})
                        sheets = os.listdir(state_path)
                        for sheetname in sheets:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath, scale, adjust)
                                    if state_dir == 'death':
                                        frames = extract_Buildingframes(
                                            sprite_sheet, sheet_rows, sheet_cols, FRAMES_PER_BUILDING
                                        )
                                    else:
                                        frames = extract_Buildingframes(sprite_sheet, 1, 1, 1)
                                    sprites[category][sprite_name][state_dir] = frames
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")

                                ASSETS_LOADED_COUNT += 1
                                if show_progress:
                                    from Controller.init_assets import draw_progress_bar
                                    progress = get_assets_progress()
                                    from Controller.init_assets import get_scaled_gui
                                    loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=screen_height)
                                    draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_screen)

            elif category == 'units':
                sprites[category][sprite_name] = {}
                sprite_path = abs_directory
                if os.path.isdir(sprite_path):
                    state_dirs = os.listdir(sprite_path)
                    for state_dir in state_dirs:
                        state_path = os.path.join(sprite_path, state_dir)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name].setdefault(state_dir, {})
                        sheets = os.listdir(state_path)
                        for sheetname in sheets:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath, scale, adjust)
                                    frames = extract_Unitframes(sprite_sheet, sheet_rows, sheet_cols, FRAMES_PER_UNIT)
                                    for direction_index in range(len(frames) // FRAMES_PER_UNIT):
                                        direction_frames = frames[
                                            direction_index * FRAMES_PER_UNIT:
                                            (direction_index + 1) * FRAMES_PER_UNIT
                                        ]
                                        sprites[category][sprite_name][state_dir][direction_index] = direction_frames
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")

                                ASSETS_LOADED_COUNT += 1
                                if show_progress:
                                    from Controller.init_assets import draw_progress_bar
                                    progress = get_assets_progress()
                                    from Controller.init_assets import get_scaled_gui
                                    loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=screen_height)
                                    draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_screen)
            elif category == 'projectiles':
                sprites[category][sprite_name] = {}
                sprite_path = abs_directory
                if os.path.isdir(sprite_path):
                    state_dirs = os.listdir(sprite_path)
                    for state_dir in state_dirs:
                        state_path = os.path.join(sprite_path, state_dir)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name].setdefault(state_dir, {})
                        sheets = os.listdir(state_path)
                        for sheetname in sheets:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath, scale, adjust)
                                    frames = extract_Projectileframes(sprite_sheet, sheet_rows, sheet_cols, FRAMES_PER_PROJECTILE)
                                    for direction_index in range(len(frames) // FRAMES_PER_PROJECTILE):
                                        direction_frames = frames[
                                            direction_index * FRAMES_PER_PROJECTILE:
                                            (direction_index + 1) * FRAMES_PER_PROJECTILE
                                        ]
                                        sprites[category][sprite_name][state_dir][direction_index] = direction_frames
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")

                                ASSETS_LOADED_COUNT += 1
                                if show_progress:
                                    from Controller.init_assets import draw_progress_bar
                                    progress = get_assets_progress()
                                    from Controller.init_assets import get_scaled_gui
                                    loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=screen_height)
                                    draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_screen)

    ASSETS_LOADED = True
    print("Sprites loaded successfully.")
    
def get_scaled_sprite(name, category, zoom, state, direction, frame_id, variant):
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()
    
    cache_key = (zoom, state, frame_id, variant, direction)
    if cache_key in zoom_cache[name]:
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]

    if state not in sprites[category][name]:
        state = 'idle'
    try:
        if category == 'buildings':
            frame_id = frame_id % len(sprites[category][name][state])
            original_image = sprites[category][name][state][frame_id]
        elif category == 'units' or category == 'projectiles':
            frame_id = frame_id % len(sprites[category][name][state][direction])
            original_image = sprites[category][name][state][direction][frame_id]
        else:
            original_image = sprites[category][name][variant]
    except IndexError as e:
        raise ValueError(f"Error accessing sprite: {e}")
    
    scaled_width = max(1, int(original_image.get_width() * zoom))
    scaled_height = max(1, int(original_image.get_height() * zoom))

    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)

    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image


def get_scaled_gui(ui_name, variant=0, target_width=None, target_height=None):
    global gui_cache
    key = (ui_name, variant, target_width, target_height)
    if key in gui_cache:
        return gui_cache[key]


    original = gui_elements[ui_name][variant]
    ow, oh = original.get_width(), original.get_height()

    if target_width and not target_height:
        ratio = target_width / ow
        target_height = int(oh * ratio)
    elif target_height and not target_width:
        ratio = target_height / oh
        target_width = int(ow * ratio)
    elif not target_width and not target_height:
        gui_cache[key] = original
        return original  # Add this return statement for consistency

    scaled = pygame.transform.smoothscale(original, (target_width, target_height))
    gui_cache[key] = scaled
    return scaled
