import pygame
from Models.html import write_full_html

def update_game_state(game_state, delta_time):
    camera = game_state['camera']
    game_map = game_state['game_map']
    handle_camera(camera, delta_time)
    if not game_state.get('paused', False):
        game_map.patch(delta_time)

def handle_camera(camera, dt, is_terminal_only=None):
    """
    Gère les mouvements de caméra selon les touches pressées.
    """
    from Settings.setup import user_choices
    if user_choices["index_terminal_display"] == 1:
        return  # Ne rien faire en mode terminal
        
    import pygame
    keys = pygame.key.get_pressed()
    move_speed = 500 * dt
    
    # Appliquer un multiplicateur de vitesse si Shift est pressé
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        move_speed *= 2

    # Déplacements caméra
    if keys[pygame.K_LEFT] or keys[pygame.K_q]:
        camera.offset_x += move_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        camera.offset_x -= move_speed
    if keys[pygame.K_UP] or keys[pygame.K_z]:
        camera.offset_y += move_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        camera.offset_y -= move_speed

    camera.limit_camera()
