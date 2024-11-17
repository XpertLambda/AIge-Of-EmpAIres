# Controller/init_map.py
import pygame
import sys
import math
from Models.Map import GameMap
from Controller.select_player import draw_player_selection, draw_player_info
from Controller.init_sprites import draw_terrain, fill_grass

from Settings.setup import (
    TILE_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MINIMAP_WIDTH,
    MINIMAP_HEIGHT,
    MINIMAP_MARGIN
)

# --- Fonctions Utilitaires Isométriques ---
def to_isometric(x, y, tile_width, tile_height):
    """
    Convertit les coordonnées cartésiennes en coordonnées isométriques.
    """
    iso_x = (x - y) * (tile_width / 2)
    iso_y = (x + y) * (tile_height / 2)
    return iso_x, iso_y

def get_color_for_terrain(terrain_type):
    """
    Retourne la couleur associée à un type de terrain.
    """
    terrain_colors = {
        'grass': (0, 255, 0),
        'mountain': (139, 137, 137),
        'gold': (255, 215, 0),
        'wood': (139, 69, 19),
        'food': (255, 0, 0)
    }
    return terrain_colors.get(terrain_type, (128, 128, 128))  # Gris neutre par défaut

# --- Classe Camera ---
class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 0.25
        self.width = width
        self.height = height
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

    def apply(self, x, y):
        x = (x + self.offset_x) * self.zoom + self.width / 2
        y = (y + self.offset_y) * self.zoom + self.height / 2
        return x, y

    def unapply(self, screen_x, screen_y):
        # Convert screen coordinates back to world coordinates
        world_x = (screen_x - self.width / 2) / self.zoom - self.offset_x
        world_y = (screen_y - self.height / 2) / self.zoom - self.offset_y
        return world_x, world_y

    def move(self, dx, dy):
        self.offset_x += dx / self.zoom
        self.offset_y += dy / self.zoom
        self.limit_camera()

    def set_zoom(self, zoom_factor):
        # Limiter le zoom entre un minimum et un maximum
        min_zoom = 0.1
        max_zoom = 3.0
        self.zoom = max(min_zoom, min(zoom_factor, max_zoom))
        self.limit_camera()

    def set_bounds(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.limit_camera()

    def limit_camera(self):
        if self.min_x is None or self.max_x is None:
            return

        half_screen_width = self.width / (2 * self.zoom)
        half_screen_height = self.height / (2 * self.zoom)

        min_offset_x = - (self.max_x - half_screen_width)
        max_offset_x = - (self.min_x + half_screen_width)
        min_offset_y = - (self.max_y - half_screen_height)
        max_offset_y = - (self.min_y + half_screen_height)

        self.offset_x = max(min_offset_x, min(self.offset_x, max_offset_x))
        self.offset_y = max(min_offset_y, min(self.offset_y, max_offset_y))


# Helper function to convert screen coordinates to world (isometric) coordinates
def screen_to_world(sx, sy, screen_width_half, screen_height_half, zoom, offset_x, offset_y):
    iso_x = (sx - screen_width_half) / zoom - offset_x
    iso_y = (sy - screen_height_half) / zoom - offset_y
    return iso_x, iso_y

# Helper function to convert isometric coordinates to tile indices
def iso_to_tile(iso_x, iso_y, a, b):
    x = ((iso_x / a) + (iso_y / b)) / 2
    y = ((iso_y / b) - (iso_x / a)) / 2
    return x, y

def draw_map(screen, game_map, camera):
    """
    Draws only the visible part of the isometric map on the screen, optimized for performance.
    """
    tile_width = TILE_SIZE
    tile_height = TILE_SIZE / 2
    half_tile_width = tile_width / 2
    half_tile_height = tile_height / 2

    screen_width = screen.get_width()
    screen_height = screen.get_height()
    screen_width_half = screen_width / 2
    screen_height_half = screen_height / 2
    zoom = camera.zoom

    # Precompute constants
    a = half_tile_width
    b = half_tile_height
    a_zoom = a * zoom
    b_zoom = b * zoom

    # Camera offsets
    offset_x = camera.offset_x
    offset_y = camera.offset_y

    # Screen corners
    corners_screen = [
        (0, 0),  # Top-left
        (screen_width, 0),  # Top-right
        (0, screen_height),  # Bottom-left
        (screen_width, screen_height)  # Bottom-right
    ]

    # Convert screen corners to world (isometric) coordinates
    corners_world = [
        screen_to_world(sx, sy, screen_width_half, screen_height_half, zoom, offset_x, offset_y)
        for sx, sy in corners_screen
    ]

    # Convert isometric coordinates to tile indices
    tile_indices = [
        iso_to_tile(iso_x, iso_y, a, b)
        for iso_x, iso_y in corners_world
    ]

    # Separate x and y indices
    x_indices = [tile_x for tile_x, _ in tile_indices]
    y_indices = [tile_y for _, tile_y in tile_indices]

    # Find min and max tile indices, adding a sufficient margin
    margin = 2  # Adjust as needed

    min_tile_x = max(0, int(math.floor(min(x_indices))) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, int(math.ceil(max(x_indices))) + margin)
    min_tile_y = max(0, int(math.floor(min(y_indices))) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, int(math.ceil(max(y_indices))) + margin)

    # Loop through the tiles within the extended visible range
    for y in range(min_tile_y, max_tile_y + 1):
        for x in range(min_tile_x, max_tile_x + 1):
            # Convert tile indices to isometric coordinates
            iso_x = (x - y) * a
            iso_y = (x + y) * b

            # Apply camera transformations to get screen coordinates
            screen_x = (iso_x + offset_x) * zoom + screen_width_half
            screen_y = (iso_y + offset_y) * zoom + screen_height_half

            # Quick check if the tile is outside the screen boundaries
            if (screen_x + a_zoom < 0 or screen_x - a_zoom > screen_width or
                screen_y + b_zoom < 0 or screen_y - b_zoom > screen_height):
                continue  # Skip tiles not visible on the screen

            # Retrieve the tile from the game map
            tile = game_map.grid[y][x]

            # Define the isometric tile polygon points
            points = [
                (screen_x, screen_y - b_zoom),    # Top
                (screen_x + a_zoom, screen_y),    # Right
                (screen_x, screen_y + b_zoom),    # Bottom
                (screen_x - a_zoom, screen_y)     # Left
            ]

            # Draw the isometric diamond representing the tile
            color = get_color_for_terrain(tile.terrain_type)
            pygame.draw.polygon(screen, color, points)

            # Draw additional details (grass, terrain features)
            fill_grass(screen, screen_x, screen_y, camera)
            draw_terrain(tile.terrain_type, screen, screen_x, screen_y, camera)


MAP_PADDING = 200

def compute_map_bounds(game_map):
    """
    Calcule les limites de la carte en coordonnées isométriques.
    """
    tile_width = TILE_SIZE
    tile_height = TILE_SIZE / 2

    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    corners = [
        (0, 0),
        (0, num_tiles_y - 1),
        (num_tiles_x - 1, 0),
        (num_tiles_x - 1, num_tiles_y - 1)
    ]

    iso_coords = [to_isometric(x, y, tile_width, tile_height) for x, y in corners]
    min_iso_x = min(coord[0] for coord in iso_coords) - MAP_PADDING
    max_iso_x = max(coord[0] for coord in iso_coords) + MAP_PADDING
    min_iso_y = min(coord[1] for coord in iso_coords) - MAP_PADDING
    max_iso_y = max(coord[1] for coord in iso_coords) + MAP_PADDING

    return min_iso_x, max_iso_x, min_iso_y, max_iso_y

def create_minimap_background(game_map, minimap_width, minimap_height, camera):
    """
    Crée la surface de la minimap représentant l'ensemble de la carte.
    """
    # Create a surface with per-pixel alpha
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((0, 0, 0))  # Fond noir de la minimap

    tile_width = TILE_SIZE
    tile_height = TILE_SIZE / 2

    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    # Calcul des limites isométriques de la carte
    iso_coords = [to_isometric(x, y, tile_width, tile_height) for x in [0, num_tiles_x -1] for y in [0, num_tiles_y -1]]
    iso_x_values = [coord[0] for coord in iso_coords]
    iso_y_values = [coord[1] for coord in iso_coords]
    min_iso_x = min(iso_x_values)
    max_iso_x = max(iso_x_values)
    min_iso_y = min(iso_y_values)
    max_iso_y = max(iso_y_values)

    iso_map_width = max_iso_x - min_iso_x
    iso_map_height = max_iso_y - min_iso_y

    # Calcul du facteur d'échelle pour adapter la carte à la minimap
    scale = min(minimap_width / iso_map_width, minimap_height / iso_map_height)

    # Calcul des décalages pour centrer la carte sur la minimap
    offset_x = (minimap_width - iso_map_width * scale) / 2
    offset_y = (minimap_height - iso_map_height * scale) / 2

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            tile = game_map.grid[y][x]
            color = get_color_for_terrain(tile.terrain_type)

            # Convertir en coordonnées isométriques
            iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)

            # Adapter les coordonnées à la minimap
            minimap_x = (iso_x - min_iso_x) * scale + offset_x
            minimap_y = (iso_y - min_iso_y) * scale + offset_y

            # Définir les dimensions des tuiles sur la minimap
            half_tile_width = (tile_width / 2) * scale
            half_tile_height = (tile_height / 2) * scale

            # Définir les points du losange isométrique sur la minimap
            points = [
                (minimap_x, minimap_y - half_tile_height),  # Haut
                (minimap_x + half_tile_width, minimap_y),   # Droite
                (minimap_x, minimap_y + half_tile_height),  # Bas
                (minimap_x - half_tile_width, minimap_y)    # Gauche
            ]

            # Dessiner le losange sur la minimap
            pygame.draw.polygon(minimap_surface, color, points)
    return minimap_surface

def draw_minimap(screen, minimap_background, camera, game_map):
    """
    Dessine la minimap à l'écran, avec le rectangle représentant la zone visible par le joueur.
    """
    minimap_width = MINIMAP_WIDTH
    minimap_height = MINIMAP_HEIGHT
    minimap_margin = MINIMAP_MARGIN

    # Positionner la minimap en bas à droite de l'écran
    minimap_x = screen.get_width() - minimap_width - minimap_margin
    minimap_y = screen.get_height() - minimap_height - minimap_margin

    # Dessiner le fond de la minimap
    screen.blit(minimap_background, (minimap_x, minimap_y))

    # Calculer le rectangle de la zone visible
    tile_width = TILE_SIZE
    tile_height = TILE_SIZE / 2

    # Calcul des limites isométriques de la carte
    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    iso_coords = [to_isometric(x, y, tile_width, tile_height) for x in [0, num_tiles_x -1] for y in [0, num_tiles_y -1]]
    iso_x_values = [coord[0] for coord in iso_coords]
    iso_y_values = [coord[1] for coord in iso_coords]
    min_iso_x = min(iso_x_values)
    max_iso_x = max(iso_x_values)
    min_iso_y = min(iso_y_values)
    max_iso_y = max(iso_y_values)

    iso_map_width = max_iso_x - min_iso_x
    iso_map_height = max_iso_y - min_iso_y

    # Calcul du facteur d'échelle (doit être le même que pour le fond de la minimap)
    scale = min(minimap_width / iso_map_width, minimap_height / iso_map_height)

    # Calcul des décalages pour centrer la carte sur la minimap
    offset_x = minimap_x + (minimap_width - iso_map_width * scale) / 2
    offset_y = minimap_y + (minimap_height - iso_map_height * scale) / 2

    # Calcul des dimensions de la vue de la caméra en coordonnées isométriques
    half_screen_width = camera.width / (2 * camera.zoom)
    half_screen_height = camera.height / (2 * camera.zoom)

    # Centre de la caméra en coordonnées isométriques
    center_iso_x = -camera.offset_x
    center_iso_y = -camera.offset_y

    # Coins de la vue de la caméra en coordonnées isométriques
    top_left_iso_x = center_iso_x - half_screen_width
    top_left_iso_y = center_iso_y - half_screen_height
    bottom_right_iso_x = center_iso_x + half_screen_width
    bottom_right_iso_y = center_iso_y + half_screen_height

    # Adapter les coordonnées à la minimap
    rect_left = (top_left_iso_x - min_iso_x) * scale + offset_x
    rect_top = (top_left_iso_y - min_iso_y) * scale + offset_y
    rect_right = (bottom_right_iso_x - min_iso_x) * scale + offset_x
    rect_bottom = (bottom_right_iso_y - min_iso_y) * scale + offset_y

    # Créer le rectangle
    rect_x = rect_left
    rect_y = rect_top
    rect_width = rect_right - rect_left
    rect_height = rect_bottom - rect_top

    # Dessiner le rectangle blanc sur la minimap
    pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), 2)

def init_pygame():
    pygame.init()
    pygame.display.set_caption("Age of Empires - Version Python")
    
    # Obtenir la résolution actuelle de l'écran
    infoObject = pygame.display.Info()
    screen_width = infoObject.current_w
    screen_height = infoObject.current_h
    
    # Initialiser la fenêtre en mode plein écran
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN | pygame.RESIZABLE)
    
    return screen, screen_width, screen_height

def display_fps(screen, clock):
    font = pygame.font.SysFont(None, 24)
    fps = int(clock.get_fps())
    fps_text = font.render(f'FPS: {fps}', True, pygame.Color('white'))
    screen.blit(fps_text, (10, 10))

# --- Fonction de la Boucle de Jeu ---
def game_loop(screen, game_map, screen_width, screen_height, players):
    """
    Boucle principale du jeu qui gère les événements, le déplacement et le zoom de la caméra,
    ainsi que le dessin de la carte.
    """
    clock = pygame.time.Clock()
    camera = Camera(screen_width, screen_height)
    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

    # Créer la minimap
    minimap_background = create_minimap_background(game_map, MINIMAP_WIDTH, MINIMAP_HEIGHT,camera)
    
    selected_player = players[0]  # Joueur par défaut
    minimap_rect = pygame.Rect(screen_width - MINIMAP_WIDTH - 10, screen_height - MINIMAP_HEIGHT - 30, MINIMAP_WIDTH, MINIMAP_HEIGHT)
    running = True
    while running:
        dt = clock.tick(60) / 1000  # Temps écoulé en secondes

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
                    camera.set_zoom(camera.zoom * 1.1)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    camera.set_zoom(camera.zoom / 1.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Molette vers le haut
                    camera.set_zoom(camera.zoom * 1.1)
                elif event.button == 5:  # Molette vers le bas
                    camera.set_zoom(camera.zoom / 1.1)
                else:
                    # Gérer la sélection du joueur avec clic
                    mouse_x, mouse_y = event.pos
                    for i, player in enumerate(players):
                        rect_y = minimap_rect.y - (i + 1) * (30 + 5)
                        rect = pygame.Rect(minimap_rect.x, rect_y, minimap_rect.width, 30)
                        if rect.collidepoint(mouse_x, mouse_y):
                            selected_player = player
                            break

        keys = pygame.key.get_pressed()
        move_speed = 300 * dt  # Vitesse en pixels par seconde
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            move_speed *= 2.5  # Acceleration with Shift

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

        screen.fill((0, 0, 0))
        draw_map(screen, game_map, camera)

        # Dessiner la minimap
        draw_minimap(screen, minimap_background, camera, game_map)

        # Dessiner la sélection des joueurs au-dessus de la minimap
        draw_player_selection(screen, players, selected_player, minimap_rect)
        
         # Afficher les informations du joueur sélectionné en bas de l'écran
        draw_player_info(screen, selected_player, screen_width, screen_height)

        display_fps(screen, clock)

        # Mettre à jour l'affichage
        pygame.display.flip()

    # Quitter Pygame proprement
    pygame.quit()
    sys.exit()
