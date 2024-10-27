# Controller/init_map.py

import pygame
import sys
from Models.Map import GameMap
from Controller.select_player import draw_player_selection, draw_player_info
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
        self.zoom = 1.0
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

    def move(self, dx, dy):
        self.offset_x += dx / self.zoom
        self.offset_y += dy / self.zoom
        self.limit_camera()

    def set_zoom(self, zoom_factor):
        # Limiter le zoom entre un minimum et un maximum
        min_zoom = 1.0
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

# --- Fonctions de Dessin ---
def draw_map(screen, game_map, camera):
    """
    Dessine la carte principale en utilisant des coordonnées isométriques.
    """
    tile_width = TILE_SIZE
    tile_height = TILE_SIZE / 2  # Hauteur isométrique de la tuile

    num_tiles_x = game_map.num_tiles_x
    num_tiles_y = game_map.num_tiles_y

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            tile = game_map.grid[y][x]

            # Convertir en coordonnées isométriques
            iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)
            screen_x, screen_y = camera.apply(iso_x, iso_y)

            # Obtenir la couleur en fonction du type de terrain
            color = get_color_for_terrain(tile.terrain_type)

            # Définir les dimensions des tuiles
            half_tile_width = tile_width / 2 * camera.zoom
            half_tile_height = tile_height / 2 * camera.zoom

            # Définir les points du losange isométrique
            points = [
                (screen_x, screen_y - half_tile_height),  # Haut
                (screen_x + half_tile_width, screen_y),   # Droite
                (screen_x, screen_y + half_tile_height),  # Bas
                (screen_x - half_tile_width, screen_y)    # Gauche
            ]

            # Dessiner le losange isométrique représentant la tuile
            pygame.draw.polygon(screen, color, points)

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

    min_iso_x = min(coord[0] for coord in iso_coords)
    max_iso_x = max(coord[0] for coord in iso_coords)
    min_iso_y = min(coord[1] for coord in iso_coords)
    max_iso_y = max(coord[1] for coord in iso_coords)

    return min_iso_x, max_iso_x, min_iso_y, max_iso_y

def create_minimap_background(game_map, minimap_width, minimap_height):
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
    minimap_background = create_minimap_background(game_map, MINIMAP_WIDTH, MINIMAP_HEIGHT)
    
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
            move_speed *= 2  # Accélération avec Shift

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

        # Mettre à jour l'affichage
        pygame.display.flip()

    # Quitter Pygame proprement
    pygame.quit()
    sys.exit()
