import pygame
import sys
import os
from tkinter import Tk, filedialog
from Entity.Building import TownCentre
from Controller.isometric_utils import to_isometric, screen_to_tile
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

    if event.type == pygame.QUIT:
        try:
            os.remove('full_snapshot.html')
        except FileNotFoundError:
            pass
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F12:
            # Chargement
            save_files = [f for f in os.listdir(SAVE_DIRECTORY)
                        if f.endswith('.pkl') and os.path.isfile(os.path.join(SAVE_DIRECTORY, f))]
            if save_files:
                print("Available saves:")
                for idx, filename in enumerate(save_files):
                    print(f"{idx + 1}: {filename}")
                choice = int(input("Enter the number of the save file to load: ")) - 1
                if 0 <= choice < len(save_files):
                    full_path = os.path.join(SAVE_DIRECTORY, save_files[choice])

                    # Reset et chargement de la map
                    game_state['game_map'] = GameMap(0, False, [], generate=False)
                    game_state['game_map'].load_map(full_path)

                    # Met à jour les joueurs avec ceux de la sauvegarde
                    loaded_players = game_state['game_map'].players
                    game_state['players'] = loaded_players

                    # Recalcule les couleurs d'équipe
                    team_colors = generate_team_colors(len(loaded_players))
                    game_state['team_colors'] = team_colors

                    # Sélectionne un joueur si dispo
                    if len(loaded_players) > 0:
                        game_state['selected_player'] = loaded_players[0]
                    else:
                        game_state['selected_player'] = None

                    # Recalcule bornes caméra
                    camera = game_state['camera']
                    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
                    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

                    # Recréation du background de la minimap
                    minimap_width = int(game_state['screen_width'] * 0.25)
                    minimap_height = int(game_state['screen_height'] * 0.25)
                    minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
                    minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
                        game_state['game_map'], minimap_width, minimap_height
                    )
                    game_state['minimap_background'] = minimap_background
                    game_state['minimap_scale'] = minimap_scale
                    game_state['minimap_offset_x'] = minimap_offset_x
                    game_state['minimap_offset_y'] = minimap_offset_y
                    game_state['minimap_min_iso_x'] = minimap_min_iso_x
                    game_state['minimap_min_iso_y'] = minimap_min_iso_y

                    # Force la mise à jour des boutons joueurs et info
                    game_state['player_selection_updated'] = True
                    game_state['player_info_updated'] = True
                    game_state['force_full_redraw'] = True

                    # Vide la minimap des entités et forcer le redraw
                    game_state['minimap_entities_surface'].fill((0, 0, 0, 0))

                    # Force un recompute de la caméra si besoin
                    game_state['recompute_camera'] = True

                else:
                    print("Invalid choice.")
            else:
                print("No save files found.")
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
                                    iso_x, iso_y = to_isometric(building.x, building.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
                                    camera.offset_x = -iso_x
                                    camera.offset_y = -iso_y
                                    break
                        player_clicked = True
                        break

                # Sélection d'une entité sur la carte
                if not player_clicked:
                    tile_x, tile_y = screen_to_tile(mouse_x, mouse_y, screen_width, screen_height, camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4)
                    game_map = game_state['game_map']
                    entities_on_tile = game_map.grid.get((tile_x, tile_y), None)
                    if entities_on_tile:
                        clicked_entity = next(iter(entities_on_tile))
                        clicked_entity.notify_clicked()

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            game_state['minimap_dragging'] = False
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
        minimap_rect = pygame.Rect(
            screen_width - minimap_width - minimap_margin,
            screen_height - minimap_height - minimap_margin,
            minimap_width,
            minimap_height
        )

        minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
        minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
            game_state['game_map'], minimap_width, minimap_height
        )

    # Mise à jour des flags
    game_state['player_selection_updated'] = player_selection_updated
    game_state['player_info_updated'] = player_info_updated

    # Mise à jour du state
    game_state['camera'] = camera
    game_state['players'] = players
    game_state['selected_player'] = game_state['selected_player']
    game_state['minimap_rect'] = minimap_rect
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
