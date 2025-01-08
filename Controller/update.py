import pygame
from Models.html import write_full_html

def update_game_state(game_state, delta_time):
    camera = game_state['camera']
    players = game_state['players']
    game_map = game_state['game_map']

    if not game_state.get('paused', False):
        handle_camera(camera, delta_time)

        for player in players:
            for unit in player.units:
                if unit.isAlive():
                    unit.setIdle()
                    if unit.path:
                        unit.move(game_map, delta_time)
                    else : 
                        unit.collisionTest(game_map)

                    if unit.target:
                        unit.attack(game_map, delta_time)

        
        for entities in list(game_map.grid.values()):
            if entities:
                for entity in list (entities):
                    if not entity.isAlive():
                         entity.kill(game_map)
                         
        for inactive_entities in list(game_map.inactive_matrix.values()):
            if inactive_entities:
                for entity in list(inactive_entities):
                    entity.death(game_map)  

        for player in players:
            for building in player.buildings:
                if building.spawnsUnits:
                    building.update_training(delta_time, game_map, player)

        for inactives in list(game_map.inactive_matrix.values()):
            if inactives:
                for entity in list(inactives):
                    entity.death(game_map)

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
