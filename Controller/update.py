# Chemin de Controller/update.py

import pygame

def update_game_state(game_state, dt):
    """
    Met à jour l'état du jeu en fonction des entrées utilisateur.
    """
    camera = game_state['camera']
    selected_player = game_state['selected_player']  # Variable modifiée
    minimap_dragging = game_state['minimap_dragging']
    minimap_rect = game_state['minimap_rect']
    minimap_offset_x = game_state['minimap_offset_x']
    minimap_offset_y = game_state['minimap_offset_y']
    minimap_min_iso_x = game_state['minimap_min_iso_x']
    minimap_min_iso_y = game_state['minimap_min_iso_y']
    minimap_scale = game_state['minimap_scale']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']

    # Extract flags
    player_info_updated = game_state.get('player_info_updated', False)

    keys = pygame.key.get_pressed()
    move_speed = 300 * dt  # Vitesse en pixels par seconde
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        move_speed *= 2.5  # Accélération avec Shift

    dx, dy = 0, 0
    if keys[pygame.K_q] or keys[pygame.K_LEFT]:
        dx += move_speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx -= move_speed
    if keys[pygame.K_z] or keys[pygame.K_UP]:
        dy += move_speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy -= move_speed
    if keys[pygame.K_TAB]:
        selected_player = game_state['selected_player']
        selected_player.write_html()  # Variable modifiée

    if dx != 0 or dy != 0:
        camera.move(dx, dy)

    # Mettre à jour la position de la caméra lors du glissement sur la minimap
    if minimap_dragging:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Calculer la position correspondante sur la carte
        minimap_click_x = mouse_x - minimap_rect.x
        minimap_click_y = mouse_y - minimap_rect.y

        # Convertir les coordonnées de la minimap en coordonnées isométriques
        iso_x = (minimap_click_x - minimap_offset_x) / minimap_scale + minimap_min_iso_x
        iso_y = (minimap_click_y - minimap_offset_y) / minimap_scale + minimap_min_iso_y

        # Mettre à jour le décalage de la caméra pour centrer la vue sur la position cliquée
        camera.offset_x = -iso_x
        camera.offset_y = -iso_y
        camera.limit_camera()

    # Example: If resources have changed, set the flag
    # This requires tracking previous resource values
    selected_player = game_state['selected_player']
    if hasattr(selected_player, 'previous_resources'):
        if selected_player.resources != selected_player.previous_resources:
            player_info_updated = True
    else:
        selected_player.previous_resources = selected_player.resources.copy()
    selected_player.previous_resources = selected_player.resources.copy()

    # Update game_state flag
    game_state['player_info_updated'] = player_info_updated

    # Mettre à jour le game_state
    game_state['camera'] = camera
