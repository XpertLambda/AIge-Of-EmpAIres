import pygame
from Models.html import write_full_html

def update_game_state(game_state, delta_time):
    camera = game_state['camera']
    game_map = game_state['game_map']
    handle_camera(camera, delta_time)
    if not game_state.get('paused', False):
        game_map.patch(delta_time)

def handle_camera(camera, delta_time):
    keys = pygame.key.get_pressed()
    move_speed = 300 * delta_time
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

    if dx != 0 or dy != 0:
        camera.move(dx, dy)
