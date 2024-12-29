import pygame
import sys
import os
import tkinter
from tkinter import Tk, filedialog
from Entity.Building import TownCentre
from Controller.isometric_utils import to_isometric, screen_to_tile, tile_to_screen
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY
from Controller.drawing import create_minimap_background, compute_map_bounds, generate_team_colors
from Models.Map import GameMap
from AiUtils.aStar import a_star
from Controller.gui import get_scaled_gui

PANEL_RATIO = 0.25
BG_RATIO    = 0.20

def get_centered_rect_in_bottom_right(w, h, scr_w, scr_h, margin=10):
    rect = pygame.Rect(0, 0, w, h)
    cx = scr_w - margin - (w // 2)
    cy = scr_h - margin - (h // 2)
    rect.center = (cx, cy)
    return rect

def handle_events(event, game_state):
    camera = game_state['camera']
    players = game_state['players']
    selected_player = game_state['selected_player']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    screen = game_state['screen']
    fullscreen = game_state['fullscreen']

    minimap_dragging = game_state['minimap_dragging']
    minimap_panel_sprite = game_state['minimap_panel_sprite']
    minimap_panel_rect = game_state['minimap_panel_rect']
    minimap_background_rect = game_state['minimap_background_rect']
    minimap_background_surface = game_state.get('minimap_background', None)
    minimap_scale = game_state.get('minimap_scale', 1)
    minimap_offset_x = game_state.get('minimap_offset_x', 0)
    minimap_offset_y = game_state.get('minimap_offset_y', 0)
    minimap_min_iso_x = game_state.get('minimap_min_iso_x', 0)
    minimap_min_iso_y = game_state.get('minimap_min_iso_y', 0)

    if 'selecting_units' not in game_state:
        game_state['selecting_units'] = False
    if 'selection_start' not in game_state:
        game_state['selection_start'] = None
    if 'selection_end' not in game_state:
        game_state['selection_end'] = None
    if 'selected_units' not in game_state:
        game_state['selected_units'] = []
    if 'show_all_health_bars' not in game_state:
        game_state['show_all_health_bars'] = False

    selecting_units = game_state['selecting_units']
    selection_start = game_state['selection_start']
    selection_end = game_state['selection_end']
    selected_units = game_state['selected_units']

    if event.type == pygame.QUIT:
        try:
            os.remove('full_snapshot.html')
        except FileNotFoundError:
            pass
        pygame.quit()
        sys.exit()

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F2:
            game_state['show_all_health_bars'] = not game_state['show_all_health_bars']
        elif event.key == pygame.K_F12:
            try:
                root = tkinter.Tk()
                root.withdraw()
                initial_dir = os.path.abspath(SAVE_DIRECTORY)
                filetypes = [('Pickle files', '*.pkl')]
                full_path = filedialog.askopenfilename(
                    title="Select Save File",
                    initialdir=initial_dir,
                    filetypes=filetypes
                )
                root.destroy()
                if full_path:
                    game_state['game_map'] = GameMap(0, False, [], generate=False)
                    game_state['game_map'].load_map(full_path)
                    print(f"Loaded save: {os.path.basename(full_path)}")
                    game_state['game_map'].display_map_in_terminal()

                    game_state['players'].clear()
                    game_state['players'].extend(game_state['game_map'].players)
                    if game_state['players']:
                        game_state['selected_player'] = game_state['players'][0]
                    else:
                        game_state['selected_player'] = None

                    team_colors = generate_team_colors(len(game_state['players']))
                    game_state['team_colors'] = team_colors

                    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
                    camera.offset_x = 0
                    camera.offset_y = 0
                    camera.zoom = 1.0

                    sw = game_state['screen_width']
                    sh = game_state['screen_height']

                    bg_width  = int(sw * BG_RATIO)
                    bg_height = int(sh * BG_RATIO)
                    mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(
                        game_state['game_map'], bg_width, bg_height
                    )
                    game_state['minimap_background'] = mb
                    game_state['minimap_scale'] = ms
                    game_state['minimap_offset_x'] = mo_x
                    game_state['minimap_offset_y'] = mo_y
                    game_state['minimap_min_iso_x'] = mi_x
                    game_state['minimap_min_iso_y'] = mi_y

                    new_bg_rect = mb.get_rect()
                    new_bg_rect.center = game_state['minimap_panel_rect'].center
                    new_bg_rect.y -= 10
                    game_state['minimap_background_rect'] = new_bg_rect

                    game_state['minimap_entities_surface'] = pygame.Surface(
                        (mb.get_width(), mb.get_height()),
                        pygame.SRCALPHA
                    )
                    game_state['minimap_entities_surface'].fill((0, 0, 0, 0))

                    game_state['player_selection_updated'] = True
                    game_state['player_info_updated'] = True
                    game_state['force_full_redraw'] = True
                    game_state['recompute_camera'] = True
                else:
                    print("No save file selected.")
            except Exception as e:
                print(f"Error loading save: {e}")

        elif event.key == pygame.K_F11:
            game_state['game_map'].save_map()
            print("Game saved successfully.")
        elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
            camera.set_zoom(camera.zoom * 1.1)
        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            camera.set_zoom(camera.zoom / 1.1)
        elif event.key == pygame.K_m:
            camera.zoom_out_to_global()
        elif event.key == pygame.K_ESCAPE:
            try:
                os.remove('full_snapshot.html')
            except FileNotFoundError:
                pass
            pygame.quit()
            sys.exit()

    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos
        if event.button == 1:
            if minimap_background_rect.collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                if game_state['selected_units']:
                    tile_x, tile_y = screen_to_tile(
                            mouse_x, mouse_y,
                            screen_width, screen_height,
                            camera,
                            HALF_TILE_SIZE/2,
                            HALF_TILE_SIZE/4
                        )
                    for unit in game_state['selected_units']:
                        a_star(unit, (tile_x, tile_y), game_state['game_map'])
                player_clicked = False
                selection_height = 30
                padding = 5
                max_height = screen_height / 3
                columns = 1
                while columns <= 4:
                    rows = (len(players) + columns - 1) // columns
                    total_height = selection_height * rows + padding*(rows - 1)
                    if total_height <= max_height or columns == 4:
                        break
                    columns += 1

                button_width = (minimap_background_rect.width - padding*(columns - 1)) // columns
                rows = (len(players) + columns - 1) // columns
                surface_height = selection_height * rows + padding*(rows - 1)
                buttons_origin_x = minimap_background_rect.x
                buttons_origin_y = minimap_background_rect.y - surface_height - padding

                for index, player in enumerate(reversed(players)):
                    col = index % columns
                    row = index // columns
                    rect_x = buttons_origin_x + col*(button_width + padding)
                    rect_y = buttons_origin_y + row*(selection_height + padding)
                    rect_btn = pygame.Rect(rect_x, rect_y, button_width, selection_height)
                    if rect_btn.collidepoint(mouse_x, mouse_y):
                        if game_state['selected_player'] != player:
                            game_state['selected_player'] = player
                            game_state['player_selection_updated'] = True
                            game_state['player_info_updated'] = True
                            for building in player.buildings:
                                if isinstance(building, TownCentre):
                                    iso_x, iso_y = to_isometric(
                                        building.x, building.y,
                                        HALF_TILE_SIZE, HALF_TILE_SIZE / 2
                                    )
                                    camera.offset_x = -iso_x
                                    camera.offset_y = -iso_y
                                    camera.limit_camera()
                                    break
                        player_clicked = True
                        break

                if not player_clicked:
                    tile_x, tile_y = screen_to_tile(
                        mouse_x, mouse_y,
                        screen_width, screen_height,
                        camera,
                        HALF_TILE_SIZE/2,
                        HALF_TILE_SIZE/4
                    )
                    game_map = game_state['game_map']
                    entities_on_tile = game_map.grid.get((tile_x, tile_y), None)
                    if entities_on_tile:
                        clicked_entity = next(iter(entities_on_tile))
                        clicked_entity.notify_clicked()

                    game_state['selecting_units'] = True
                    game_state['selection_start'] = (mouse_x, mouse_y)
                    game_state['selection_end'] = (mouse_x, mouse_y)

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.MOUSEMOTION:
        if game_state['minimap_dragging']:
            pass
        else:
            if game_state['selecting_units']:
                game_state['selection_end'] = event.pos

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            game_state['minimap_dragging'] = False
            if game_state['selecting_units']:
                x1, y1 = game_state['selection_start']
                x2, y2 = game_state['selection_end']
                rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
                rect.normalize()
                game_state['selected_units'].clear()
                if game_state['selected_player']:
                    all_units = game_state['selected_player'].units
                    for unit in all_units:
                        sx, sy = tile_to_screen(
                            unit.x, unit.y,
                            HALF_TILE_SIZE, HALF_TILE_SIZE / 2,
                            camera, screen_width, screen_height
                        )
                        if rect.collidepoint(sx, sy):
                            game_state['selected_units'].append(unit)
                game_state['selecting_units'] = False
                game_state['selection_start'] = None
                game_state['selection_end'] = None

        if event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.VIDEORESIZE:
        sw, sh = event.size
        camera.width = sw
        camera.height = sh

        panel_width  = int(sw * PANEL_RATIO)
        panel_height = int(sh * PANEL_RATIO)
        minimap_panel_sprite = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
        game_state['minimap_panel_sprite'] = minimap_panel_sprite

        new_panel_rect = get_centered_rect_in_bottom_right(
            panel_width, panel_height, sw, sh, game_state['minimap_margin']
        )
        game_state['minimap_panel_rect'] = new_panel_rect

        bg_width  = int(sw * BG_RATIO)
        bg_height = int(sh * BG_RATIO)
        mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(
            game_state['game_map'], bg_width, bg_height
        )
        game_state['minimap_background'] = mb
        game_state['minimap_scale'] = ms
        game_state['minimap_offset_x'] = mo_x
        game_state['minimap_offset_y'] = mo_y
        game_state['minimap_min_iso_x'] = mi_x
        game_state['minimap_min_iso_y'] = mi_y

        new_bg_rect = mb.get_rect()
        new_bg_rect.center = new_panel_rect.center
        new_bg_rect.y -= panel_height /50
        new_bg_rect.x += panel_width / 18
        game_state['minimap_background_rect'] = new_bg_rect

        game_state['minimap_entities_surface'] = pygame.Surface(
            (mb.get_width(), mb.get_height()),
            pygame.SRCALPHA
        )
        game_state['minimap_entities_surface'].fill((0, 0, 0, 0))

        game_state['screen_width'] = sw
        game_state['screen_height'] = sh
        game_state['player_selection_updated'] = True
