# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\game_loop.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\game_loop.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\game_loop.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\game_loop.py
import time
import pygame
import sys
import random
from Controller.Bot import *
from Models.Map import GameMap
from Entity.Building import *
from Entity.Unit import *
from Models.Team import Team
from Controller.camera import Camera
from Controller.terminal_display_debug import debug_print
from Controller.drawing import (
    draw_map,
    compute_map_bounds,
    create_minimap_background,
    display_fps,
    generate_team_colors,
    draw_pointer,
    draw_gui_elements,
    draw_minimap_viewport
)
import copy
from Controller.event_handler import handle_events
from Controller.update import update_game_state, handle_camera
from Controller.gui import (
    create_player_selection_surface,
    create_player_info_surface,
    get_scaled_gui,
    get_centered_rect_in_bottom_right,
    update_minimap_elements,
    draw_pause_menu
)
from Controller.utils import tile_to_screen
from Controller.Bot import *
from Settings.setup import (
    HALF_TILE_SIZE,
    MINIMAP_MARGIN,
    UPDATE_EVERY_N_MILLISECOND,
    user_choices,
    GAME_SPEED,
    PANEL_RATIO,
    BG_RATIO,
    ONE_SECOND,
    FPS_DRAW_LIMITER,
    SAVE_DIRECTORY  # Import SAVE_DIRECTORY
)

from Controller.Bot import manage_battle
import os # Import os for path operations
from Settings.sync import TEMP_SAVE_PATH, TEMP_SAVE_FILENAME
from Controller.sync_manager import check_and_load_sync

# TEMP_SAVE_FILENAME = "temp_save.pkl" # Define temporary save file name # Moved to sync.py
# TEMP_SAVE_PATH = os.path.join(SAVE_DIRECTORY, TEMP_SAVE_FILENAME) # Define the full path to the temp save # Moved to sync.py

def is_player_dead(player):
    if not player.units and not player.buildings:
        if (player.resources.food <= 50 and
            player.resources.gold <= 225):
            return True
    return False

def draw_game_over_overlay(screen, game_state):
    font = pygame.font.SysFont(None, 48)
    text = font.render(f"Joueur {game_state['winner_id']} est gagnant!", True, (255, 255, 255))
    text_rect = text.get_rect(center=(game_state['screen_width'] // 2, game_state['screen_height'] // 2 - 50))
    screen.blit(text, text_rect)

    button_font = pygame.font.SysFont(None, 36)
    button_text = button_font.render("Quitter le jeu", True, (255, 255, 255))
    button_rect = button_text.get_rect(center=(game_state['screen_width'] // 2, game_state['screen_height'] // 2 + 50))
    pygame.draw.rect(screen, (0, 0, 0), button_rect.inflate(20, 10))
    screen.blit(button_text, button_rect)
    game_state['game_over_button_rect'] = button_rect

    main_menu_text = button_font.render("Menu Principal", True, (255, 255, 255))
    main_menu_rect = main_menu_text.get_rect(
        center=(game_state['screen_width'] // 2, game_state['screen_height'] // 2 + 100)
    )
    pygame.draw.rect(screen, (0, 0, 0), main_menu_rect.inflate(20, 10))
    screen.blit(main_menu_text, main_menu_rect)
    game_state['main_menu_button_rect'] = main_menu_rect

def game_loop(screen, game_map, screen_width, screen_height, players): # game_map is passed here
    # Protection contre les dimensions nulles
    if screen_width <= 0 or screen_height <= 0:
        screen_width = 800
        screen_height = 600

    # Si on est en mode terminal only, on n'initialise pas pygame
    from Settings.setup import user_choices
    is_terminal_only = user_choices["index_terminal_display"] == 1

    if not is_terminal_only:  # Si pas en mode Terminal only
        clock = pygame.time.Clock()
        pygame.key.set_repeat(0, 0)
        pygame.mouse.set_visible(False)
        fullscreen = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
    else:
        clock = None
        fullscreen = False

    camera = Camera(screen_width, screen_height)
    team_colors = generate_team_colors(len(players))
    font = pygame.font.SysFont(None, 24)

    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

    map_width = max_iso_x - min_iso_x
    map_height = max_iso_y - min_iso_y
    camera.min_zoom = min(
        screen_width / float(map_width),
        screen_height / float(map_height)
    )

    camera.zoom_out_to_global()

    panel_width  = int(screen_width * PANEL_RATIO)
    panel_height = int(screen_height * PANEL_RATIO)
    minimap_panel_sprite = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
    minimap_panel_rect   = get_centered_rect_in_bottom_right(
        panel_width, panel_height, screen_width, screen_height, MINIMAP_MARGIN
    )

    bg_width  = int(screen_width * BG_RATIO)
    bg_height = int(screen_height * BG_RATIO)
    (
        minimap_background_surface,
        minimap_scale,
        minimap_offset_x,
        minimap_offset_y,
        minimap_min_iso_x,
        minimap_min_iso_y
    ) = create_minimap_background(game_map, bg_width, bg_height)

    minimap_background_rect = minimap_background_surface.get_rect()
    minimap_background_rect.center = minimap_panel_rect.center
    minimap_background_rect.y -= panel_height / 50
    minimap_background_rect.x += panel_width / 18
    minimap_entities_surface = pygame.Surface(
        (minimap_background_rect.width, minimap_background_rect.height),
        pygame.SRCALPHA
    )
    minimap_entities_surface.fill((0, 0, 0, 0))

    selected_player = players[0] if players else None
    fullscreen = False

    game_state = {
        'camera': camera,
        'players': players,
        'selected_player': selected_player,
        'team_colors': team_colors,
        'game_map': game_map, # Pass the game_map object to game_state
        'minimap_panel_sprite': minimap_panel_sprite,
        'minimap_panel_rect': minimap_panel_rect,
        'minimap_background': minimap_background_surface,
        'minimap_background_rect': minimap_background_rect,
        'minimap_entities_surface': minimap_entities_surface,
        'minimap_scale': minimap_scale,
        'minimap_offset_x': minimap_offset_x,
        'minimap_offset_y': minimap_offset_y,
        'minimap_min_iso_x': minimap_min_iso_x,
        'minimap_min_iso_y': minimap_min_iso_y,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'screen': screen,
        'fullscreen': fullscreen,  # On utilise la variable locale
        'minimap_dragging': False,
        'player_selection_updated': True,
        'player_info_updated': True,
        'selected_entities': [],
        'selecting_entities': False,
        'selection_start': None,
        'selection_end': None,
        'rectangle_additive': False,
        'paused': False,
        'force_full_redraw': False,
        'show_all_health_bars': False,
        'show_player_info': True,
        'show_gui_elements': True,
        'return_to_menu': False,
        'pause_menu_active': False,
        'notification_message': "",
        'notification_start_time': 0.0,
        'players_target': [None for _ in range(len(players))],
        'old_resources': {p.teamID: p.resources.copy() for p in players},  # Initialize for all players

        # Nouveau bool pour déclencher un switch F9
        'switch_display': False,
        'force_sync': False,  # Add force_sync to game_state
    }

    game_map.set_game_state(game_state)

    player_selection_surface = None
    player_info_surface = None

    running = True
    update_counter = 0
    old_resources = {} # Retirer cette ligne (inutile, on va chercher dans game_state)
    game_state['old_resources'] = {} # AJOUTER CETTE LIGNE : initialiser dans game_state
    for p in players:
        game_state['old_resources'][p.teamID] = p.resources.copy() # Initialiser dans game_state


    draw_timer = 0
    decision_timer = 0
    players_target = [None for _ in range(len(players))]


    players_target=[None for _ in range(0,len(players))]

    last_time = time.time()  # Ajout pour le mode terminal

    # Check if temp save exists and load if so, only on initial game_loop start, not after mode switch
    if os.path.exists(TEMP_SAVE_PATH) and not game_state.get('switch_display'): # Check switch_display to prevent loading after switch
        print("Loading game state from temp save...") # MODIFIED DEBUG PRINT
        try:
            game_map.load_map(TEMP_SAVE_PATH)
            players = game_map.players # Reload players from loaded map
            game_state['players'] = players
            if players:
                game_state['selected_player'] = players[0]
            else:
                game_state['selected_player'] = None
            team_colors = generate_team_colors(len(players)) # Regenerate team colors based on loaded players
            game_state['team_colors'] = team_colors
            game_state['players_target'] = [None for _ in range(len(players))] # Reinitialize players_target
            game_state['old_resources'] = {p.teamID: p.resources.copy() for p in players} # Reinitialize old_resources

            os.remove(TEMP_SAVE_PATH) # Clean up temp save after loading
            print("Successfully loaded game state from temp save and deleted it.") # DEBUG
        except Exception as e:
            print(f"Error loading from temp save: {e}") # DEBUG
            if os.path.exists(TEMP_SAVE_PATH): # Ensure temp save is deleted even if loading fails
                os.remove(TEMP_SAVE_PATH)
                print("Deleted temp save file due to load error.") # DEBUG


    # Check for temp save at startup (this part is likely redundant now and can be removed or kept for initial load from save files)
    if os.path.exists(TEMP_SAVE_PATH):
            try:
                print("[GUI] Loading game state from temp save...") # MODIFIED DEBUG PRINT
                # Store current game_state
                old_game_state = game_map.game_state

                # Load the map
                game_map.load_map(TEMP_SAVE_PATH)

                # Restore and update game_state
                game_map.game_state = old_game_state

                # Update players and other state
                players = game_map.players
                game_state['players'] = players
                if players:
                    game_state['selected_player'] = players[0]
                else:
                    game_state['selected_player'] = None

                game_state['players_target'] = [None for _ in range(len(players))]
                game_state['team_colors'] = generate_team_colors(len(players))

                os.remove(TEMP_SAVE_PATH)
                print("[GUI] Successfully loaded temp save") # MODIFIED DEBUG PRINT

                # Force a redraw
                game_state['force_full_redraw'] = True
                game_state['player_selection_updated'] = True

            except Exception as e:
                debug_print(f"[GUI] Error loading temp save: {e}")
                if os.path.exists(TEMP_SAVE_PATH):
                    os.remove(TEMP_SAVE_PATH)

    # Quand on charge une sauvegarde depuis le terminal
    if os.path.exists(TEMP_SAVE_PATH):
            try:
                print("[GUI - GAME LOOP] Found temp save, reloading for sync...") # MODIFIED DEBUG PRINT
                game_map.load_map(TEMP_SAVE_PATH)

                players = game_map.players
                game_state['players'] = players
                game_state['selected_player'] = players[0] if players else None
                game_state['players_target'] = [None for _ in range(len(players))]
                game_state['team_colors'] = generate_team_colors(len(players))
                game_state['old_resources'] = {
                    p.teamID: p.resources.copy() for p in players
                }

                # --- GUI REFRESH EXPLICIT STEPS (in game loop) ---
                print("[GUI - GAME LOOP - LOOP LOAD] Before GUI refresh, player count:", len(game_state['players'])) # DEBUG
                min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map) # Recompute map bounds
                camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y) # Reset camera bounds
                camera.zoom_out_to_global() # Reset zoom
                game_state['force_full_redraw'] = True
                game_state['player_selection_updated'] = True
                player_selection_surface = create_player_selection_surface(
                    game_state['players'],
                    game_state['selected_player'],
                    game_state['minimap_background_rect'],
                    game_state['team_colors']
                )
                game_state['player_selection_surface'] = player_selection_surface
                game_state['player_info_updated'] = True # Ensure player info is also updated
                game_state['player_info_updated'] = True
                game_state['notification_start_time'] = time.time()
                print("[GUI - GAME LOOP - LOOP LOAD] After GUI refresh completed") # DEBUG
                # --- END GUI REFRESH ---


                os.remove(TEMP_SAVE_PATH)
                print("[GUI - GAME LOOP] Successfully loaded new game state") # MODIFIED DEBUG PRINT

            except Exception as e:
                debug_print(f"[GUI] Error loading temp save: {e}")
                if os.path.exists(TEMP_SAVE_PATH):
                    os.remove(TEMP_SAVE_PATH)

    while running:
        current_time = time.time()
        if not is_terminal_only:
            raw_dt = clock.tick(400) / ONE_SECOND
        else:
            raw_dt = current_time - last_time
            last_time = current_time
            time.sleep(0.01)  # Petit délai pour ne pas surcharger le CPU

        dt = 0 if game_state['paused'] else raw_dt
        dt = dt * GAME_SPEED

        # On ne gère la caméra que si on n'est pas en mode terminal
        if not is_terminal_only:
            handle_camera(camera, raw_dt * GAME_SPEED)
            # Gestion des événements pygame uniquement en mode non-terminal
            events = pygame.event.get()
            for event in events:
                handle_events(event, game_state)
                if event.type == pygame.QUIT:
                    running = False
                if game_state.get('game_over', False):
                    pygame.mouse.set_visible(True)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if 'game_over_button_rect' in game_state:
                            if game_state['game_over_button_rect'].collidepoint(mx, my):
                                user_choices["menu_result"] = "quit"
                                running = False
                        if 'main_menu_button_rect' in game_state:
                            if game_state['main_menu_button_rect'].collidepoint(mx, my):
                                user_choices["menu_result"] = "main_menu"
                                game_state['game_over'] = False
                                game_state['return_to_menu'] = True

        if game_state.get('return_to_menu'):
            break

        # SI on a reçu le signal "switch_display" => on arrête la boucle
        if game_state.get('switch_display'):
            debug_print("Saving game state before display switch...")
            game_map.save_map(TEMP_SAVE_PATH) # Save to temp file before switching
            running = False
            user_choices["menu_result"] = "switch_display"
            break

        screen = game_state['screen']
        screen_width = game_state['screen_width']
        screen_height = game_state['screen_height']
        selected_player = game_state['selected_player']
        players = game_state['players']
        team_colors = game_state['team_colors']
        game_map = game_state['game_map'] # Use the game_map from game_state
        camera = game_state['camera']

        if user_choices["index_terminal_display"] == 1:
            screen = None

        if not game_state.get('paused', False):
            if update_counter > 1:
                update_counter = 0
                update_minimap_elements(game_state)
            update_counter += dt

        # Simpliste manage battle
        if selected_player and selected_player.teamID >= len(players_target):
            # Redimensionner si nécessaire
            players_target.clear()
            players_target.extend([None] * len(players))
            game_state['players_target'] = players_target

        manage_battle(selected_player, players_target, players, game_map, dt)

        if not game_state.get('paused', False):
            if game_state.get('player_selection_updated', False):
                player_selection_surface = create_player_selection_surface(
                    players,
                    selected_player,
                    game_state['minimap_background_rect'],
                    team_colors
                )
                game_state['player_selection_surface'] = player_selection_surface # AJOUTER CETTE LIGNE
                game_state['player_selection_updated'] = False

            if game_state.get('player_info_updated', False):
                player_info_surface = create_player_info_surface(
                    selected_player,
                    screen_width,
                    screen_height,
                    team_colors
                )
                game_state['player_info_updated'] = False

            update_game_state(game_state, dt)

        for p in players[:]:
            if is_player_dead(p):
                debug_print(f"[GAME] Joueur {p.teamID} est éliminé.")
                if p.teamID in game_state['old_resources']: # On utilise game_state['old_resources']
                    del game_state['old_resources'][p.teamID] # SUPPRIMER D'ABORD DE game_state['old_resources']
                players.remove(p) # PUIS RETIRER DE players (ordre inversé ici)


        if len(players) == 1 and not game_state.get('game_over', False):
            debug_print(f"[GAME] Joueur {players[0].teamID} est gagnant.")
            game_state['winner_id'] = players[0].teamID
            game_state['game_over'] = True
            game_state['paused'] = True

        if selected_player is not None:
            if selected_player in players: # Double vérification (redondante mais sécuritaire)
                if selected_player.teamID in game_state['old_resources']: # UTILISER game_state['old_resources']
                    previous_res = game_state['old_resources'][selected_player.teamID] # UTILISER game_state['old_resources']
                else:
                    print(f"DEBUG WARNING: selected_player.teamID {selected_player.teamID} not in old_resources keys!")
                    continue # Passer à l'itération suivante
            else:
                print("DEBUG WARNING: selected_player not found in players list!")
                continue # Passer à l'itération suivante

            current_res = selected_player.resources
            previous_res = game_state['old_resources'][selected_player.teamID] # UTILISER game_state['old_resources']
            if current_res != previous_res:
                game_state['player_info_updated'] = True
                game_state['old_resources'][selected_player.teamID] = current_res.copy() # METTRE A JOUR game_state['old_resources']


        # N'effectuer le rendu que si on a un écran
        if screen is not None and draw_timer >= 1/FPS_DRAW_LIMITER:
            draw_timer = 0
            screen.fill((0, 0, 0))
            draw_map(
                screen,
                screen_width,
                screen_height,
                game_map, # Use the game_map object from game_state
                camera,
                players,
                team_colors,
                game_state,
                dt
            )

            if game_state['show_gui_elements']:
                draw_gui_elements(screen, screen_width, screen_height)
                screen.blit(game_state['minimap_background'], game_state['minimap_background_rect'].topleft)
                screen.blit(game_state['minimap_entities_surface'], game_state['minimap_background_rect'].topleft)
                draw_minimap_viewport(
                    screen,
                    camera,
                    game_state['minimap_background_rect'],
                    game_state['minimap_scale'],
                    game_state['minimap_offset_x'],
                    game_state['minimap_offset_y'],
                    game_state['minimap_min_iso_x'],
                    game_state['minimap_min_iso_y']
                )

                if player_selection_surface:
                    sel_h = player_selection_surface.get_height()
                    bg_rect = game_state['minimap_background_rect']
                    screen.blit(player_selection_surface, (bg_rect.x, bg_rect.y - sel_h - 20))

                if player_info_surface and game_state['show_player_info']:
                    x_offset = int(screen_width * 0.03)
                    screen.blit(player_info_surface, (x_offset, 0))

            draw_pointer(screen)

            for pl in game_map.players:
                for unit in pl.units:
                    if unit.path:
                        unit.display_path(
                            game_state['screen'],
                            game_state['screen_width'],
                            game_state['screen_height'],
                            game_state['camera']
                        )
            display_fps(screen,screen_width, clock, font)

            if game_state['notification_message']:
                if time.time() - game_state['notification_start_time'] < 3:
                    notif_font = pygame.font.SysFont(None, 28)
                    notif_surf = notif_font.render(game_state['notification_message'], True, (255,255,0))
                    fps_height = 30
                    margin = 10
                    notif_x = screen_width - notif_surf.get_width() - margin
                    notif_y = fps_height + margin
                    screen.blit(notif_surf, (notif_x, notif_y))
                else:
                    game_state['notification_message'] = ""

            if game_state.get('game_over', False):
                draw_game_over_overlay(screen, game_state)
            if game_state.get('pause_menu_active'):
                draw_pause_menu(screen, game_state)
                draw_pointer(screen)
                pygame.display.flip()
                continue

            if game_state.get('force_full_redraw', False):
                pygame.display.flip()
                game_state['force_full_redraw'] = False
            else:
                pygame.display.flip()

        draw_timer += raw_dt
        decision_timer += raw_dt

        # After handling events but before drawing
        # Check if terminal has created a temp save
        if os.path.exists(TEMP_SAVE_PATH):
            try:
                print("[GUI] Found temp save, reloading for sync...") # MODIFIED DEBUG PRINT

                # Charger directement la nouvelle map
                game_map.load_map(TEMP_SAVE_PATH)

                # Mettre à jour l'état avec les nouvelles données
                players = game_map.players
                game_state['players'] = players
                game_state['selected_player'] = players[0] if players else None
                game_state['players_target'] = [None for _ in range(len(players))]
                game_state['team_colors'] = generate_team_colors(len(players))
                game_state['old_resources'] = {
                    p.teamID: p.resources.copy() for p in players
                }

                # Forcer mise à jour visuelle
                game_state['force_full_redraw'] = True
                game_state['player_selection_updated'] = True
                game_state['player_info_updated'] = True

                os.remove(TEMP_SAVE_PATH)
                print("[GUI] Successfully loaded new game state") # MODIFIED DEBUG PRINT

            except Exception as e:
                debug_print(f"[GUI] Error loading temp save: {e}")
                if os.path.exists(TEMP_SAVE_PATH):
                    os.remove(TEMP_SAVE_PATH)

        # After updating everything, force sync if requested
        if game_state.get('force_sync'):
            print("[GAME_LOOP] Forcing game state sync across interfaces...") # MODIFIED DEBUG PRINT
            game_map.save_map(TEMP_SAVE_PATH)
            print("[GAME_LOOP] Reloading from temp save for sync.") # MODIFIED DEBUG PRINT
            game_map.load_map(TEMP_SAVE_PATH)
            players = game_map.players
            game_state['players'] = players
            game_state['selected_player'] = players[0] if players else None
            players_target[:] = players_target[:len(players)]  # Keep targets in sync
            team_colors = generate_team_colors(len(players))
            game_state['team_colors'] = team_colors
            os.remove(TEMP_SAVE_PATH)
            game_state['force_sync'] = False

        # Vérifier régulièrement les synchros
        if check_and_load_sync(game_map):
            print("[GUI] Sync state loaded")
            # Mettre à jour l'état complet
            players = game_map.players
            game_state['players'] = players
            game_state['selected_player'] = players[0] if players else None
            game_state['team_colors'] = generate_team_colors(len(players))
            game_state['force_full_redraw'] = True
            game_state['player_selection_updated'] = True

    return "done"