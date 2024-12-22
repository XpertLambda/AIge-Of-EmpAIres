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

def handle_events(event, game_state):
    camera = game_state['camera']
    players = game_state['players']
    selected_player = game_state['selected_player']
    minimap_rect = game_state['minimap_rect']
    minimap_dragging = game_state['minimap_dragging']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    screen = game_state['screen']
    fullscreen = game_state['fullscreen']

    minimap_background = game_state.get('minimap_background', None)
    minimap_scale = game_state.get('minimap_scale', 1)
    minimap_offset_x = game_state.get('minimap_offset_x', 0)
    minimap_offset_y = game_state.get('minimap_offset_y', 0)
    minimap_min_iso_x = game_state.get('minimap_min_iso_x', 0)
    minimap_min_iso_y = game_state.get('minimap_min_iso_y', 0)

    player_selection_updated = game_state.get('player_selection_updated', False)
    player_info_updated = game_state.get('player_info_updated', False)

    # Récupération des variables pour la sélection rectangulaire
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
        if event.key == pygame.K_F11:
            # Sauvegarde rapide
            game_state['game_map'].save_map()
            print("Game saved successfully.")
        elif event.key == pygame.K_F12:
            # Chargement
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

                    camera = game_state['camera']
                    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
                    camera.offset_x = 0
                    camera.offset_y = 0
                    camera.zoom = 1.0

                    minimap_width = int(game_state['screen_width'] * 0.25)
                    minimap_height = int(game_state['screen_height'] * 0.25)
                    mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(
                        game_state['game_map'], minimap_width, minimap_height
                    )
                    game_state['minimap_background'] = mb
                    game_state['minimap_scale'] = ms
                    game_state['minimap_offset_x'] = mo_x
                    game_state['minimap_offset_y'] = mo_y
                    game_state['minimap_min_iso_x'] = mi_x
                    game_state['minimap_min_iso_y'] = mi_y

                    game_state['player_selection_updated'] = True
                    game_state['player_info_updated'] = True
                    game_state['force_full_redraw'] = True

                    game_state['minimap_entities_surface'].fill((0, 0, 0, 0))
                    game_state['recompute_camera'] = True
                else:
                    print("No save file selected.")
            except Exception as e:
                print(f"Error loading save: {e}")

        elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
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
            # Clic gauche
            if minimap_rect.collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                # --- Début de la sélection rectangulaire ---
                game_state['selecting_units'] = True
                game_state['selection_start'] = (mouse_x, mouse_y)
                game_state['selection_end'] = (mouse_x, mouse_y)

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.MOUSEMOTION:
        if game_state['minimap_dragging']:
            # Drag sur la minimap
            pass
        else:
            # Si on est en train de sélectionner
            if game_state['selecting_units']:
                game_state['selection_end'] = event.pos

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            if game_state['minimap_dragging']:
                game_state['minimap_dragging'] = False
            else:
                if game_state['selecting_units']:
                    # Fin de la sélection
                    x1, y1 = game_state['selection_start']
                    x2, y2 = game_state['selection_end']
                    selection_rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
                    selection_rect.normalize()

                    # On vide la liste précédente
                    game_state['selected_units'].clear()

                    # Récupération de toutes les unités sur la carte
                    # (On parcourt tous les players et toutes leurs unités)
                    all_units = []
                    for p in game_state['players']:
                        all_units.extend(p.units)

                    # Test de collision rect <-> position isométrique de l’unité
                    for unit in all_units:
                        sx, sy = tile_to_screen(unit.x, unit.y, HALF_TILE_SIZE,
                                                HALF_TILE_SIZE / 2, camera, 
                                                screen_width, screen_height)
                        if selection_rect.collidepoint(sx, sy):
                            game_state['selected_units'].append(unit)

                    game_state['selecting_units'] = False
                    game_state['selection_start'] = None
                    game_state['selection_end'] = None

        if event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.VIDEORESIZE:
        # Resize gère la fenêtre, inchangé
        sw, sh = event.size
        camera.width = sw
        camera.height = sh

        minimap_width = int(sw * 0.25)
        minimap_height = int(sh * 0.25)
        new_rect = pygame.Rect(
            sw - minimap_width - game_state['minimap_margin'],
            sh - minimap_height - game_state['minimap_margin'],
            minimap_width,
            minimap_height
        )
        mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(game_state['game_map'],
                                                                  minimap_width, 
                                                                  minimap_height)
        game_state['minimap_rect'] = new_rect
        game_state['minimap_background'] = mb
        game_state['minimap_scale'] = ms
        game_state['minimap_offset_x'] = mo_x
        game_state['minimap_offset_y'] = mo_y
        game_state['minimap_min_iso_x'] = mi_x
        game_state['minimap_min_iso_y'] = mi_y
        game_state['screen_width'] = sw
        game_state['screen_height'] = sh

    game_state['player_selection_updated'] = player_selection_updated
    game_state['player_info_updated'] = player_info_updated
    game_state['camera'] = camera
    game_state['players'] = players
    game_state['selected_player'] = game_state['selected_player']
    game_state['minimap_rect'] = game_state['minimap_rect']
    game_state['minimap_dragging'] = game_state['minimap_dragging']
    game_state['minimap_background'] = minimap_background
    game_state['minimap_scale'] = minimap_scale
    game_state['minimap_offset_x'] = minimap_offset_x
    game_state['minimap_offset_y'] = minimap_offset_y
    game_state['minimap_min_iso_x'] = minimap_min_iso_x
    game_state['minimap_min_iso_y'] = minimap_min_iso_y
    game_state['screen_width'] = screen_width
    game_state['screen_height'] = screen_height
    game_state['screen'] = screen
    game_state['fullscreen'] = fullscreen
