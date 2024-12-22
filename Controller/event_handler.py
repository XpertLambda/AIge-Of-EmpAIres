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
    minimap_margin = game_state['minimap_margin']
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

    # -- Assurer l'existence des clés pour la sélection rectangulaire --
    if 'selecting_units' not in game_state:
        game_state['selecting_units'] = False
    if 'selection_start' not in game_state:
        game_state['selection_start'] = None
    if 'selection_end' not in game_state:
        game_state['selection_end'] = None
    if 'selected_units' not in game_state:
        game_state['selected_units'] = []

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
            # Save the game without prompting for a filename
            game_state['game_map'].save_map()
            print("Game saved successfully.")

        elif event.key == pygame.K_F12:
            # Open a file dialog to select a save file
            try:
                # Hide the root tkinter window
                root = tkinter.Tk()
                root.withdraw()
                # Set the initial directory to the saves folder
                initial_dir = os.path.abspath(SAVE_DIRECTORY)
                # Specify file types
                filetypes = [('Pickle files', '*.pkl')]
                # Open the file dialog
                full_path = filedialog.askopenfilename(
                    title="Select Save File",
                    initialdir=initial_dir,
                    filetypes=filetypes
                )
                root.destroy()
                if full_path:
                    # Reset and load the game map
                    game_state['game_map'] = GameMap(0, False, [], generate=False)
                    game_state['game_map'].load_map(full_path)

                    # Display the map in the terminal
                    print(f"Loaded save: {os.path.basename(full_path)}")
                    game_state['game_map'].display_map_in_terminal()

                    # Clear existing players and update with loaded players
                    game_state['players'].clear()
                    game_state['players'].extend(game_state['game_map'].players)

                    # Update selected_player
                    if game_state['players']:
                        game_state['selected_player'] = game_state['players'][0]
                    else:
                        game_state['selected_player'] = None

                    # Recalculate team colors based on new players
                    team_colors = generate_team_colors(len(game_state['players']))
                    game_state['team_colors'] = team_colors

                    # Reset camera bounds and position based on the new map
                    camera = game_state['camera']
                    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
                    camera.offset_x = 0
                    camera.offset_y = 0
                    camera.zoom = 1.0  # Reset zoom if necessary

                    # Recreate minimap background
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

                    # Force update of player selection and info
                    game_state['player_selection_updated'] = True
                    game_state['player_info_updated'] = True
                    game_state['force_full_redraw'] = True

                    # Clear minimap entities surface and force redraw
                    game_state['minimap_entities_surface'].fill((0, 0, 0, 0))

                    # Force recompute of camera if needed
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
            # Permet de quitter après le load
            try:
                os.remove('full_snapshot.html')
            except FileNotFoundError:
                pass
            pygame.quit()
            sys.exit()

    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos
        if event.button == 1:
            if minimap_rect.collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                player_clicked = False

                # Calcul pour les boutons joueurs
                selection_height = 30
                padding = 5
                players = game_state['players']
                screen_height = game_state['screen_height']
                max_height = screen_height / 3

                columns = 1
                while columns <= 4:
                    rows = (len(players) + columns - 1) // columns
                    total_height = selection_height * rows + padding * (rows - 1)
                    if total_height <= max_height or columns == 4:
                        break
                    columns += 1

                button_width = (minimap_rect.width - padding * (columns - 1)) // columns
                rows = (len(players) + columns - 1) // columns

                surface_height = selection_height * rows + padding * (rows - 1)
                buttons_origin_x = minimap_rect.x
                buttons_origin_y = minimap_rect.y - surface_height - padding

                # Vérifie si on a cliqué sur un bouton de joueur
                for index, player in enumerate(reversed(players)):
                    col = index % columns
                    row = index // columns
                    rect_x = buttons_origin_x + col * (button_width + padding)
                    rect_y = buttons_origin_y + row * (selection_height + padding)
                    rect = pygame.Rect(rect_x, rect_y, button_width, selection_height)
                    if rect.collidepoint(mouse_x, mouse_y):
                        if game_state['selected_player'] != player:
                            game_state['selected_player'] = player
                            player_selection_updated = True
                            player_info_updated = True
                            # Centre caméra sur le TownCentre
                            for building in player.buildings:
                                if isinstance(building, TownCentre):
                                    iso_x, iso_y = to_isometric(building.x, building.y,
                                                               HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
                                    camera.offset_x = -iso_x
                                    camera.offset_y = -iso_y
                                    break
                        player_clicked = True
                        break

                # Sélection d'une entité sur la carte (single-click)
                if not player_clicked:
                    tile_x, tile_y = screen_to_tile(mouse_x, mouse_y,
                                                    screen_width, screen_height,
                                                    camera,
                                                    HALF_TILE_SIZE/2,
                                                    HALF_TILE_SIZE/4)
                    game_map = game_state['game_map']
                    entities_on_tile = game_map.grid.get((tile_x, tile_y), None)
                    if entities_on_tile:
                        clicked_entity = next(iter(entities_on_tile))
                        clicked_entity.notify_clicked()

                    # -- DÉBUT de la sélection rectangulaire (si on veut multi-sélection) --
                    game_state['selecting_units'] = True
                    game_state['selection_start'] = (mouse_x, mouse_y)
                    game_state['selection_end'] = (mouse_x, mouse_y)

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)

        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.MOUSEMOTION:
        # Si on est en train de déplacer la minimap
        if game_state['minimap_dragging']:
            pass  # Géré ailleurs dans update si besoin
        else:
            # Mettre à jour la sélection rectangulaire si activée
            if game_state['selecting_units']:
                game_state['selection_end'] = event.pos

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            # On arrête de drag la minimap
            game_state['minimap_dragging'] = False

            # Fin de la sélection rectangulaire
            if game_state['selecting_units']:
                x1, y1 = game_state['selection_start']
                x2, y2 = game_state['selection_end']
                rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
                rect.normalize()

                # On vide la liste précédente
                game_state['selected_units'].clear()

                # Récupération des unités du joueur sélectionné
                all_units = selected_player.units

                # Test de collision rect <-> position isométrique de l’unité
                for unit in all_units:
                    sx, sy = tile_to_screen(
                        unit.x, unit.y,
                        HALF_TILE_SIZE, HALF_TILE_SIZE / 2,
                        camera, screen_width, screen_height
                    )
                    if rect.collidepoint(sx, sy):
                        game_state['selected_units'].append(unit)

                # Désactivation du mode sélection
                game_state['selecting_units'] = False
                game_state['selection_start'] = None
                game_state['selection_end'] = None

        # Gestion Zoom
        if event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)

    elif event.type == pygame.VIDEORESIZE:
        screen_width, screen_height = event.size
        camera.width = screen_width
        camera.height = screen_height

        minimap_width = int(screen_width * 0.25)
        minimap_height = int(screen_height * 0.25)
        new_rect = pygame.Rect(
            screen_width - minimap_width - minimap_margin,
            screen_height - minimap_height - minimap_margin,
            minimap_width,
            minimap_height
        )

        mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(
            game_state['game_map'], minimap_width, minimap_height
        )

        game_state['minimap_rect'] = new_rect
        game_state['minimap_background'] = mb
        game_state['minimap_scale'] = ms
        game_state['minimap_offset_x'] = mo_x
        game_state['minimap_offset_y'] = mo_y
        game_state['minimap_min_iso_x'] = mi_x
        game_state['minimap_min_iso_y'] = mi_y
        game_state['screen_width'] = screen_width
        game_state['screen_height'] = screen_height

    # Mise à jour des flags
    game_state['player_selection_updated'] = player_selection_updated
    game_state['player_info_updated'] = player_info_updated

    # Mise à jour du state
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
