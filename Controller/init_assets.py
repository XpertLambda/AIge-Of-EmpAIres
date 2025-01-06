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

def draw_progress_bar(screen, progress, screen_width, screen_height, progress_text, loading_screen_image):
    screen.blit(loading_screen_image, (0, 0))

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

def load_sprites(screen, screen_width, screen_height):
    global gui_elements
    gui_elements.clear()
    
    total_files = sum(len(files) for _, _, files in os.walk('assets'))
    loaded_files = 0
    
    # Load GUI assets
    for gui_key, gui_val in gui_config.items():
        directory = gui_val.get('directory')
        gui_scale = gui_val.get('scale')
        gui_adjust_scale = gui_val.get('adjust_scale')
        if not directory:
            continue
        gui_elements[gui_key] = []
        try:
            dir_content = os.listdir(directory)
        except FileNotFoundError:
            print(f"Directory not found: {directory}")
            continue

        for filename in dir_content:
            if filename.lower().endswith("webp"):
                filepath = os.path.join(directory, filename)
                if gui_key == 'loading_screen':
                    loading_screen = load_sprite(filepath, (screen_width, screen_height))
                    screen.blit(loading_screen, (0, 0))
                    pygame.display.flip()
                    continue
                loaded_sprite = load_sprite(filepath, gui_scale, gui_adjust_scale)
                gui_elements[gui_key].append(loaded_sprite)
                loaded_files += 1
                progress = loaded_files / total_files
                draw_progress_bar(screen, progress, screen_width, screen_height, gui_key, loading_screen)

    # Load sprites from sprite_config
    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')
            if 'sheet_config' in value:
                sheet_cols = value['sheet_config'].get('columns', 0)
                sheet_rows = value['sheet_config'].get('rows', 0)

            if category in ['resources', 'buildings']:
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
                        loaded_files += 1
                        progress = loaded_files / total_files
                        # Re-blit loading screen last loaded for continuity
                        draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name,loading_screen)

            elif category == 'units':
                sprites[category][sprite_name] = {}
                sprite_path = directory
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
                                    frames = extract_frames(sprite_sheet, sheet_rows, sheet_cols)
                                    print(f"frames : {len(frames)} for {sprite_name} : {state_dir}")
                                    for direction_index in range(len(frames) // FRAMES_PER_UNIT):
                                        direction_frames = frames[direction_index * FRAMES_PER_UNIT : (direction_index + 1) * FRAMES_PER_UNIT]
                                        sprites[category][sprite_name][state_dir][direction_index] = direction_frames
                                        print(f'{len(direction_frames)} for direction : {direction_index} : {state_dir}')
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")
                                loaded_files += 1
                                progress = loaded_files / total_files
                                draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_screen)

                progress = loaded_files / total_files
                draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_screen)

    print("Sprites loaded successfully.")
    
def get_scaled_sprite(name, category, zoom, state, direction, frame_id, variant):
    # same as before except we clamp scaled_width, scaled_height >=1
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()
    cache_key = (zoom, state, frame_id, variant, direction)
    if cache_key in zoom_cache[name]:
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]

    if category in ['resources', 'buildings']:
        original_image = sprites[category][name][variant]
    elif category == 'units':
        original_image = sprites[category][name][state][direction][frame_id]

    scaled_width = int(original_image.get_width() * zoom)
    scaled_height= int(original_image.get_height()* zoom)

    # clamp
    if scaled_width <1: scaled_width=1
    if scaled_height<1: scaled_height=1

    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))

    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)
    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image

def draw_sprite(screen, acronym, category, screen_x, screen_y, zoom, state=None, frame=0, variant=0, direction=0):
    name = Entity_Acronym[category][acronym]
    if state is not None:
        state = states[state]

    scaled_sprite = get_scaled_sprite(name, category, zoom, state, direction, frame, variant)
    if scaled_sprite is None:
        return
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, ' ', 'resources', screen_x, screen_y, camera.zoom)

def draw_hitbox(screen, corners, zoom):
    if len(corners) != 4:
        raise ValueError("Hitbox must have exactly 4 corners.")
    scaled_corners = [(x * zoom, y * zoom) for x, y in corners]
    pygame.draw.polygon(screen, (255, 255, 255), corners, width=1)

def draw_path(screen, unit_center, screenPath, zoom, color):
    if len(screenPath) >= 2:
        pygame.draw.lines(screen, color, False, screenPath, max(1, int(4 * zoom)))
    pygame.draw.circle(screen, color, unit_center, int(5 * zoom))