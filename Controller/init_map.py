# Controller/init_map.py
import pygame
import sys
import math
from Models.Map import GameMap
from Controller.select_player import draw_player_selection, draw_player_info
from Controller.init_sprites import draw_terrain, fill_grass, draw_building
from Models.Team import Team
from Models.Building import TownCentre
from Settings.setup import WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE

from Settings.setup import (
    HALF_TILE_SIZE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MINIMAP_MARGIN
)

# --- Redéfinition des dimensions de la minimap ---
MINIMAP_WIDTH = 550  # Agrandir la largeur de la minimap
MINIMAP_HEIGHT = 280  # Agrandir la hauteur de la minimap
MINIMAP_MARGIN = 20   # Ajuster la marge si nécessaire

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
    if terrain_type == 'gold':
        return (255, 215, 0)  # Couleur pour 'gold'
    else:
        return (34, 139, 34)  # Couleur de l'herbe pour tous les autres terrains

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
        # Convertit les coordonnées de l'écran en coordonnées du monde
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

def screen_to_tile(sx, sy, screen_width, screen_height, camera, a, b):
    # Convert screen coordinates to world (isometric) coordinates
    iso_x = (sx - screen_width / 2) / camera.zoom - camera.offset_x
    iso_y = (sy - screen_height / 2) / camera.zoom - camera.offset_y
    
    # Convert isometric coordinates to tile indices
    x = ((iso_x / a) + (iso_y / b)) / 2
    y = ((iso_y / b) - (iso_x / a)) / 2
    
    return x, y

def tile_to_screen(x, y, width, height, camera, screen_width, screen_height):
    # Convert Cartesian coordinates to isometric coordinates
    iso_x = (x - y) * (width / 2)
    iso_y = (x + y) * (height / 2)
    
    # Convert isometric coordinates to screen coordinates with camera adjustments
    screen_x = (iso_x + camera.offset_x) * camera.zoom + screen_width / 2
    screen_y = (iso_y + camera.offset_y) * camera.zoom + screen_height / 2

    return screen_x, screen_y

def draw_map(screen, screen_width, screen_height, game_map, camera, players):
    """
    Dessine uniquement les sprites sur la carte isométrique visible à l'écran.
    """
    # Coins de l'écran
    corners_screen = [
        (0, 0),  # Haut-gauche
        (screen_width, 0),  # Haut-droit
        (0, screen_height),  # Bas-gauche
        (screen_width, screen_height)  # Bas-droit
    ]

    # Convertir les coins de l'écran directement en indices de tuiles
    tile_indices = [
    screen_to_tile(sx, sy, screen_width, screen_height, camera, HALF_TILE_SIZE / 2, HALF_TILE_SIZE / 4)
    for sx, sy in corners_screen
    ]

    # Séparer les indices x et y
    x_indices = [tile_x for tile_x, _ in tile_indices]
    y_indices = [tile_y for _, tile_y in tile_indices]

    # Trouver les indices minimaux et maximaux des tuiles, en ajoutant une marge suffisante
    margin = 0  # Ajuster si nécessaire

    min_tile_x = max(0, int(math.floor(min(x_indices))) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, int(math.ceil(max(x_indices))) + margin)
    min_tile_y = max(0, int(math.floor(min(y_indices))) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, int(math.ceil(max(y_indices))) + margin)

    print_set = []
    # Boucler à travers les tuiles dans la plage visible étendue
    for y in range(min_tile_y, max_tile_y):
        for x in range(min_tile_x, max_tile_x + 1):
            # Convert tile indices directly to screen coordinates
            screen_x, screen_y = tile_to_screen(x, y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height)

            # Récupérer la tuile de la carte du jeu
            tile = game_map.grid[y][x]

            # Dessiner les sprites (herbe, terrains)
            fill_grass(screen, screen_x, screen_y, camera)
            if tile.building is not None  and tile.building.x == x and tile.building.y == y:
                print_set.append((tile, screen_x, screen_y))
            if tile.terrain_type != 'grass' and tile.building is None:  
                print_set.append((tile, screen_x, screen_y))
            if tile.building is not None:
                pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 20)
    for (tile, screen_x, screen_y) in print_set:
        building = tile.building
        if building is None:
            draw_terrain(tile.terrain_type, screen, screen_x, screen_y, camera)
        else:
            center_x = building.x + (building.size1 - 1) / 2
            center_y = building.y + (building.size2 - 1) / 2
            screen_x, screen_y = tile_to_screen(center_x,center_y, HALF_TILE_SIZE, HALF_TILE_SIZE/2, camera, screen_width, screen_height)
            draw_building(building, screen, screen_x, screen_y, camera, tile.player.nb)
    
MAP_PADDING = 650

def compute_map_bounds(game_map):
    """
    Calcule les limites de la carte en coordonnées isométriques.
    """
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

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

def create_minimap_background(game_map, minimap_width, minimap_height):
    """
    Crée la surface de la minimap représentant l'ensemble de la carte.
    """
    # Créer une surface avec transparence par pixel
    minimap_surface = pygame.Surface((minimap_width, minimap_height))
    minimap_surface.fill((0, 0, 0))  # Fond noir de la minimap

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

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
    
    # Assurer que les tuiles ont une taille minimale sur la minimap
    min_HALF_TILE_SIZE = 4  # Taille minimale des tuiles en pixels
    min_scale = min_HALF_TILE_SIZE / tile_width
    scale = max(scale, min_scale)

    # Recalculer les dimensions de la minimap pour s'adapter à la nouvelle échelle
    scaled_iso_map_width = iso_map_width * scale
    scaled_iso_map_height = iso_map_height * scale

    # Calcul des décalages pour centrer la carte sur la minimap
    offset_x = (minimap_width - scaled_iso_map_width) / 2
    offset_y = (minimap_height - scaled_iso_map_height) / 2

    for y in range(num_tiles_y):
        for x in range(num_tiles_x):
            tile = game_map.grid[y][x]
            # Dessiner toutes les tuiles sans filtrage
            # Convert to isometric coordinates
            iso_x, iso_y = to_isometric(x, y, tile_width, tile_height)

            # Adjust coordinates to minimap
            minimap_x = (iso_x - min_iso_x) * scale + offset_x
            minimap_y = (iso_y - min_iso_y) * scale + offset_y

            # Define the size of the tiles on the minimap
            half_tile_width = (tile_width / 2) * scale
            half_tile_height = (tile_height / 2) * scale

            # Increase size for gold tiles
            if tile.terrain_type == 'gold':
                size_factor = 1.5  # Adjust as needed
                half_tile_width *= size_factor
                half_tile_height *= size_factor

            # Define the points of the isometric diamond on the minimap
            points = [
                (minimap_x, minimap_y - half_tile_height),  # Top
                (minimap_x + half_tile_width, minimap_y),   # Right
                (minimap_x, minimap_y + half_tile_height),  # Bottom
                (minimap_x - half_tile_width, minimap_y)    # Left
            ]

            # Draw the diamond on the minimap
            color = get_color_for_terrain(tile.terrain_type)
            pygame.draw.polygon(minimap_surface, color, points)
    return minimap_surface, scale, offset_x, offset_y, min_iso_x, min_iso_y

def draw_minimap(screen, minimap_background, camera, game_map, scale, offset_x, offset_y, min_iso_x, min_iso_y, minimap_rect):
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
    screen.blit(minimap_background, minimap_rect.topleft)

    # Calculer le rectangle de la zone visible
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

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
    rect_left = (top_left_iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
    rect_top = (top_left_iso_y - min_iso_y) * scale + minimap_rect.y + offset_y
    rect_right = (bottom_right_iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
    rect_bottom = (bottom_right_iso_y - min_iso_y) * scale + minimap_rect.y + offset_y

    # Créer le rectangle
    rect_x = rect_left
    rect_y = rect_top
    rect_width = rect_right - rect_left
    rect_height = rect_bottom - rect_top

    # Dessiner le rectangle blanc sur la minimap
    pygame.draw.rect(screen, (255, 255, 255), (rect_x, rect_y, rect_width, rect_height), 2)

    # Overlay player-specific colors where players have buildings
    for y in range(game_map.num_tiles_y):
        for x in range(game_map.num_tiles_x):
            tile = game_map.grid[y][x]
            if tile.player is not None:
                # Get minimap coordinates of the tile
                iso_x, iso_y = to_isometric(x, y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
                minimap_x = (iso_x - min_iso_x) * scale + minimap_rect.x + offset_x
                minimap_y = (iso_y - min_iso_y) * scale + minimap_rect.y + offset_y

                # Define the size of the tiles on the minimap
                half_tile_width = (HALF_TILE_SIZE / 2) * scale
                half_tile_height = (HALF_TILE_SIZE / 4) * scale

                # Define the points of the isometric diamond on the minimap
                points = [
                    (minimap_x, minimap_y - half_tile_height),  # Top
                    (minimap_x + half_tile_width, minimap_y),   # Right
                    (minimap_x, minimap_y + half_tile_height),  # Bottom
                    (minimap_x - half_tile_width, minimap_y)    # Left
                ]

                # Set color based on player number
                player_colors = [
                    (255, 0, 0),   # Red for player 1
                    (0, 0, 255),   # Blue for player 2
                    # Add more colors for additional players if needed
                ]
                player_index = tile.player.nb - 1  # Assuming player numbers start from 1
                color = player_colors[player_index % len(player_colors)]

                # Draw semi-transparent overlay
                pygame.draw.polygon(screen, (*color, 100), points)

def init_pygame():
    pygame.init()
    pygame.display.set_caption("Age of Empires - Version Python")
    
    # Obtenir la résolution actuelle de l'écran
    infoObject = pygame.display.Info()
    screen_width = infoObject.current_w
    screen_height = infoObject.current_h
    
    # Initialiser la fenêtre en mode plein écran
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    
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

    # Initialize local minimap dimensions
    minimap_margin = MINIMAP_MARGIN
    minimap_width = int(screen_width * 0.25)  # 25% of screen width
    minimap_height = int(screen_height * 0.25)  # 25% of screen height
    minimap_rect = pygame.Rect(
        screen_width - minimap_width - minimap_margin,
        screen_height - minimap_height - minimap_margin,
        minimap_width,
        minimap_height
    )

    # Create the minimap background with initial dimensions
    minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
    minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
        game_map, minimap_width, minimap_height
    )

    selected_player = players[0]
    minimap_dragging = False
    running = True
    while running:
        dt = clock.tick(120) / 1000  # Time elapsed in seconds

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
                mouse_x, mouse_y = event.pos
                if event.button == 1:  # Bouton gauche de la souris
                    if minimap_rect.collidepoint(mouse_x, mouse_y):
                        minimap_dragging = True
                    else:
                        # Gérer la sélection du joueur avec clic
                        mouse_x, mouse_y = event.pos
                        for i, player in enumerate(reversed(players)):
                            rect_y = minimap_rect.y - (i + 1) * (30 + 5)
                            rect = pygame.Rect(minimap_rect.x, rect_y, minimap_rect.width, 30)
                            if rect.collidepoint(mouse_x, mouse_y):
                                selected_player = player
                                for building in selected_player.buildings:
                                    if isinstance(building, TownCentre):
                                        iso_x, iso_y = to_isometric(building.x, building.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
                                        
                                        camera.offset_x = -iso_x
                                        camera.offset_y = -iso_y
                                        break

                
                elif event.button == 4:  # Molette vers le haut
                    camera.set_zoom(camera.zoom * 1.1)
                elif event.button == 5:  # Molette vers le bas
                    camera.set_zoom(camera.zoom / 1.1)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    minimap_dragging = False
                if event.button == 4:  # Molette vers le haut
                    camera.set_zoom(camera.zoom * 1.1)
                elif event.button == 5:  # Molette vers le bas
                    camera.set_zoom(camera.zoom / 1.1)
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.size
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE )
                camera.width = screen_width
                camera.height = screen_height

                # Update minimap dimensions on window resize
                minimap_width = int(screen_width * 0.25)
                minimap_height = int(screen_height * 0.25)
                minimap_rect = pygame.Rect(
                    screen_width - minimap_width - minimap_margin,
                    screen_height - minimap_height - minimap_margin,
                    minimap_width,
                    minimap_height
                )

                # Recreate minimap background with new size
                minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
                minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
                    game_map, minimap_width, minimap_height
                )

        # Update the minimap dragging position calculations
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
            Team.write_html(selected_player)

        if dx != 0 or dy != 0:
            camera.move(dx, dy)

        screen.fill((0, 0, 0))
        draw_map(screen, screen_width, screen_height, game_map, camera, players)

        # Dessiner la minimap
        draw_minimap(screen, minimap_background, camera, game_map, minimap_scale, minimap_offset_x, minimap_offset_y, minimap_min_iso_x, minimap_min_iso_y, minimap_rect)

        # Dessiner la sélection des joueurs au-dessus de la minimap
        draw_player_selection(screen, players, selected_player, minimap_rect)

        # Afficher les informations du joueur sélectionné en bas de l'écran
        draw_player_info(screen, selected_player, screen_width, screen_height)

        display_fps(screen, clock)
        
        #!DEBUG
        #if int(clock.get_fps()) in [18,19,20,21,22] :
         #   running = False


        # Mettre à jour l'affichage
        pygame.display.flip()

    # Quitter Pygame proprement
    pygame.quit()
    sys.exit()


