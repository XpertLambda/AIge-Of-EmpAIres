import pygame
from Models.html import write_full_html
def update_game_state(game_state, dt):
    camera = game_state['camera']
    selected_player = game_state['selected_player']
    minimap_dragging = game_state['minimap_dragging']
    minimap_background_rect = game_state['minimap_background_rect']
    minimap_scale = game_state.get('minimap_scale', 1)
    minimap_offset_x = game_state.get('minimap_offset_x', 0)
    minimap_offset_y = game_state.get('minimap_offset_y', 0)
    minimap_min_iso_x = game_state.get('minimap_min_iso_x', 0)
    minimap_min_iso_y = game_state.get('minimap_min_iso_y', 0)
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']

    player_info_updated = game_state.get('player_info_updated', False)

    keys = pygame.key.get_pressed()
    move_speed = 300 * dt
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        move_speed *= 2.5

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
        if not game_state.get('tab_pressed', False):
            game_state['paused'] = not game_state.get('paused', False)
            if game_state['paused']:
                write_full_html(game_state['players'], game_state['game_map'])
            game_state['tab_pressed'] = True
    else:
        game_state['tab_pressed'] = False
    # If the game is paused, skip updating the game state
    if game_state.get('paused', False):
        return

    if dx != 0 or dy != 0:
        camera.move(dx, dy)

    # Syncing camera with minimap updates
    if minimap_dragging:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        minimap_click_x = mouse_x - minimap_background_rect.x
        minimap_click_y = mouse_y - minimap_background_rect.y

        iso_x = (minimap_click_x - minimap_offset_x) / minimap_scale + minimap_min_iso_x
        iso_y = (minimap_click_y - minimap_offset_y) / minimap_scale + minimap_min_iso_y

        camera.offset_x = -iso_x
        camera.offset_y = -iso_y
        camera.limit_camera()

    game_state['player_info_updated'] = player_info_updated
    game_state['camera'] = camera
