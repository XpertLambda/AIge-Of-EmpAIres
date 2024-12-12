import pygame
import sys
from tkinter import Tk, filedialog
from Entity.Building import TownCentre
from Controller.isometric_utils import to_isometric, screen_to_tile
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY

def handle_events(event, game_state):
    """
    Gère les événements utilisateur.
    """
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

    # Données de la minimap
    minimap_background = game_state.get('minimap_background', None)
    minimap_scale = game_state.get('minimap_scale', 1)
    minimap_offset_x = game_state.get('minimap_offset_x', 0)
    minimap_offset_y = game_state.get('minimap_offset_y', 0)
    minimap_min_iso_x = game_state.get('minimap_min_iso_x', 0)
    minimap_min_iso_y = game_state.get('minimap_min_iso_y', 0)

    # Flags
    player_selection_updated = game_state.get('player_selection_updated', False)
    player_info_updated = game_state.get('player_info_updated', False)

    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_y:
            fullscreen = not fullscreen
            if fullscreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                infoObject = pygame.display.Info()
                screen_width, screen_height = infoObject.current_w, infoObject.current_h
            else:
                screen_width, screen_height = 800, 600
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

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
            from Controller.drawing import create_minimap_background
            minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
            minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
                game_state['game_map'], minimap_width, minimap_height
            )
        elif event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.key == pygame.K_F11:
            game_state['game_map'].save_map()
        elif event.key == pygame.K_F12:
            root = Tk()
            root.withdraw()
            filename = filedialog.askopenfilename(
                initialdir=SAVE_DIRECTORY,
                title="Select save file",
                filetypes=(("Pickle files", "*.pkl"), ("All files", "*.*"))
            )
            if filename:
                game_state['game_map'].load_map(filename)
                players = game_state['game_map'].players
            root.destroy()
        elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
            camera.set_zoom(camera.zoom / 1.1)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos
        if event.button == 1:
            if minimap_rect.collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                # Sélection du joueur via la liste au-dessus de la minimap
                player_clicked = False
                for i, player in enumerate(players):
                    rect_y = minimap_rect.y - (i + 1) * (30 + 5)
                    rect = pygame.Rect(minimap_rect.x, rect_y, minimap_rect.width, 30)
                    if rect.collidepoint(mouse_x, mouse_y):
                        if game_state['selected_player'] != player:
                            game_state['selected_player'] = player
                            player_selection_updated = True
                            player_info_updated = True
                            # Centrer la caméra sur le TownCentre du joueur
                            for building in player.buildings:
                                if isinstance(building, TownCentre):
                                    iso_x, iso_y = to_isometric(building.x, building.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
                                    camera.offset_x = -iso_x
                                    camera.offset_y = -iso_y
                                    break
                        player_clicked = True
                        break

                # Si aucun joueur n'a été sélectionné par le clic,
                # on tente de sélectionner une entité sur la carte.
                if not player_clicked:
                    # Conversion de la position écran en tuile isométrique
                    tile_x, tile_y = screen_to_tile(mouse_x, mouse_y, screen_width, screen_height, camera, HALF_TILE_SIZE/2, HALF_TILE_SIZE/4)
                    game_map = game_state['game_map']
                    entities_on_tile = game_map.grid.get((tile_x, tile_y), None)
                    if entities_on_tile:
                        # On prend la première entité trouvée
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
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
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

        from Controller.drawing import create_minimap_background
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
