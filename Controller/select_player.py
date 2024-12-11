import pygame
from collections import Counter
# [Controller/select_player.py](Controller/select_player.py)


def create_player_selection_surface(players, selected_player, minimap_rect):
    """
    Crée une surface contenant les zones de sélection des joueurs.
    """
    selection_height = 30  # Hauteur de chaque zone de sélection
    padding = 5            # Espacement entre les zones
    total_height = selection_height * len(players) + padding * (len(players) - 1)

    surface = pygame.Surface((minimap_rect.width, total_height), pygame.SRCALPHA)

    for i, player in enumerate(reversed(players)):
        # Calcul des coordonnées de chaque zone de sélection
        rect_y = i * (selection_height + padding)
        rect = pygame.Rect(0, rect_y, minimap_rect.width, selection_height)

        # Couleur de sélection ou de fond
        color = (0, 100, 255) if player == selected_player else (150, 150, 150)
        pygame.draw.rect(surface, color, rect)

        # Texte du joueur
        font = pygame.font.Font(None, 24)
        text = font.render(f"Player {players.index(player)}", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    return surface

def create_player_info_surface(selected_player, screen_width):
    """
    Crée une surface contenant les informations du joueur sélectionné.
    """
    font = pygame.font.Font(None, 24)
    padding = 5
    info_height = 130  # Increased height to accommodate the player's name/ID
    surface = pygame.Surface((screen_width, info_height), pygame.SRCALPHA)

    # Render the player's name/ID
    player_name_surface = font.render(f"Player {selected_player.teamID}", True, (255, 255, 255))
    surface.blit(player_name_surface, (padding, 0))

    # Afficher les ressources
    resources_text = f"Resources - Food: {selected_player.resources['food']}, Wood: {selected_player.resources['wood']}, Gold: {selected_player.resources['gold']}"
    resources_surface = font.render(resources_text, True, (255, 255, 255))
    surface.blit(resources_surface, (padding, 30))

    # Afficher les unités (types et nombre)
    unit_counts = Counter(unit.acronym for unit in selected_player.units)
    units_text = "Units - " + ", ".join([f"{acronym}: {count}" for acronym, count in unit_counts.items()])
    units_surface = font.render(units_text, True, (255, 255, 255))
    surface.blit(units_surface, (padding, 60))

    # Afficher les bâtiments (types et nombre)
    building_counts = Counter(building.acronym for building in selected_player.buildings)
    buildings_text = "Buildings - " + ", ".join([f"{acronym}: {count}" for acronym, count in building_counts.items()])
    buildings_surface = font.render(buildings_text, True, (255, 255, 255))
    surface.blit(buildings_surface, (padding, 90))

    return surface

