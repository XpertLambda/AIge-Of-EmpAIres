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

def point_inside_diamond(x, y, diamond_points):
    # Vérifier si un point est à l'intérieur d'un polygone (losange)
    n = len(diamond_points)
    inside = False
    px, py = x, y

    x1, y1 = diamond_points[0]
    for i in range(n + 1):
        x2, y2 = diamond_points[i % n]
        if min(y1, y2) < py <= max(y1, y2) and px <= max(x1, x2):
            if y1 != y2:
                xinters = (py - y1) * (x2 - x1) / (y2 - y1 + 0.000001) + x1
            if x1 == x2 or px <= xinters:
                inside = not inside
        x1, y1 = x2, y2
    return inside

def calculate_diamond_bounds(num_tiles_x, num_tiles_y, tile_size, camera):
    # Calculer les coordonnées isométriques des coins de la carte
    half_tiles_x = num_tiles_x // 2
    half_tiles_y = num_tiles_y // 2

    # Coins de la carte en coordonnées de tuile
    top_tile = (half_tiles_x, 0)
    right_tile = (num_tiles_x, half_tiles_y)
    bottom_tile = (half_tiles_x, num_tiles_y)
    left_tile = (0, half_tiles_y)

    # Convertir en coordonnées isométriques
    iso_top = camera.apply_zoom(to_isometric(*top_tile, tile_size))
    iso_right = camera.apply_zoom(to_isometric(*right_tile, tile_size))
    iso_bottom = camera.apply_zoom(to_isometric(*bottom_tile, tile_size))
    iso_left = camera.apply_zoom(to_isometric(*left_tile, tile_size))

    return [iso_top, iso_right, iso_bottom, iso_left]

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

    # Calculer les points du losange de la carte
    diamond_points = calculate_diamond_bounds(num_tiles_x, num_tiles_y, TILE_SIZE, camera)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Molette vers le haut
                    camera.zoom_in()
                    # Recalculer les points du losange après le zoom
                    diamond_points = calculate_diamond_bounds(num_tiles_x, num_tiles_y, TILE_SIZE, camera)
                elif event.button == 5:  # Molette vers le bas
                    camera.zoom_out()
                    # Recalculer les points du losange après le zoom
                    diamond_points = calculate_diamond_bounds(num_tiles_x, num_tiles_y, TILE_SIZE, camera)

        keys = pygame.key.get_pressed()
        move_speed = 20 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 10

        dx, dy = 0, 0
        if keys[pygame.K_z] or keys[pygame.K_UP]:
            dy -= move_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += move_speed
        if keys[pygame.K_q] or keys[pygame.K_LEFT]:
            dx -= move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += move_speed

        # Sauvegarder l'ancienne position de la caméra
        old_x, old_y = camera.camera.x, camera.camera.y

        camera.move(dx, dy)

        # Vérifier si les quatre coins de l'écran sont toujours à l'intérieur du losange
        screen_corners = [
            (camera.camera.x, camera.camera.y),
            (camera.camera.x + WINDOW_WIDTH, camera.camera.y),
            (camera.camera.x + WINDOW_WIDTH, camera.camera.y + WINDOW_HEIGHT),
            (camera.camera.x, camera.camera.y + WINDOW_HEIGHT)
        ]

        # Si tous les coins sont en dehors du losange, revenir à l'ancienne position
        outside = True
        for corner in screen_corners:
            if point_inside_diamond(*corner, diamond_points):
                outside = False
                break

        if outside:
            camera.camera.x, camera.camera.y = old_x, old_y

        draw_map(screen, game_map, textures, camera)
        clock.tick(120)

    pygame.quit()
    sys.exit()
