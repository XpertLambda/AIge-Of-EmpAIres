import pygame
import sys
from Models.Map import GameMap
from Settings.setup import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
from Controller.map_2_5d import draw_map, to_isometric

class Camera:
    def __init__(self):
        self.camera = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.zoom = 1.0

    def apply_zoom(self, pos):
        return (pos[0] * self.zoom, pos[1] * self.zoom)

    def zoom_in(self):
        self.zoom *= 1.1

    def zoom_out(self):
        self.zoom /= 1.1

    def move(self, dx, dy):
        self.camera.x += dx
        self.camera.y += dy

def init_pygame():
    pygame.init()
    # Mode plein écran
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Age of Empires - Version Python")
    return screen

def load_textures():
    return {}  # Retourne un dictionnaire vide car nous n'utilisons pas de textures

def game_loop(screen, game_map, textures):
    clock = pygame.time.Clock()
    camera = Camera()

    num_tiles_x = game_map.width // TILE_SIZE
    num_tiles_y = game_map.height // TILE_SIZE

    # Calculer le centre isométrique de la carte
    map_center_x = num_tiles_x // 2
    map_center_y = num_tiles_y // 2
    iso_center_x, iso_center_y = to_isometric(map_center_x, map_center_y, TILE_SIZE)
    iso_center_x, iso_center_y = camera.apply_zoom((iso_center_x, iso_center_y))

    # Centrer la caméra
    camera.camera.x = iso_center_x - WINDOW_WIDTH // 2
    camera.camera.y = iso_center_y - WINDOW_HEIGHT // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Molette vers le haut
                    camera.zoom_in()
                elif event.button == 5:  # Molette vers le bas
                    camera.zoom_out()

        keys = pygame.key.get_pressed()
        move_speed = 10 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 5

        dx, dy = 0, 0
        if keys[pygame.K_z]:
            dy -= move_speed
        if keys[pygame.K_s]:
            dy += move_speed
        if keys[pygame.K_q]:
            dx -= move_speed
        if keys[pygame.K_d]:
            dx += move_speed

        camera.move(dx, dy)

        draw_map(screen, game_map, textures, camera)
        clock.tick(120)

    pygame.quit()
    sys.exit()
