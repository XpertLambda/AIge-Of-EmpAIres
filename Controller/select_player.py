import pygame
from collections import Counter
from Models import Unit

def draw_player_selection(screen, players, selected_player, minimap_rect):
    """
    Dessine les zones de sélection des joueurs au-dessus de la minimap.
    """
    selection_height = 30  # Hauteur de chaque zone de sélection
    padding = 5            # Espacement entre les zones
    for i, player in enumerate(players):
        # Calcul des coordonnées de chaque zone de sélection
        rect_x = minimap_rect.x
        rect_y = minimap_rect.y - (i + 1) * (selection_height + padding)
        rect_width = minimap_rect.width
        rect = pygame.Rect(rect_x, rect_y, rect_width, selection_height)
        
        # Couleur de sélection ou de fond
        color = (0, 100, 255) if player == selected_player else (150, 150, 150)
        pygame.draw.rect(screen, color, rect)
        
        # Texte du joueur (utilisez pygame.font pour le rendu du texte)
        font = pygame.font.Font(None, 24)
        text = font.render(f"Bot {i+1}", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    return selection_height * len(players) + padding * (len(players) - 1)


def draw_player_info(screen, selected_player, screen_width, screen_height):
    """
    Affiche les informations du joueur sélectionné en bas de l'écran :
    - Types et nombre d'unités
    - Nombre de ressources
    - Types de bâtiments et leur nombre
    """
    font = pygame.font.Font(None, 24)
    padding = 5
    info_y = screen_height - 100  # Position de départ en bas de l'écran

    # Afficher les ressources
    resources_text = f"Resources - Food: {selected_player.resources.food}, Wood: {selected_player.resources.wood}, Gold: {selected_player.resources.gold}"
    resources_surface = font.render(resources_text, True, (255, 255, 255))
    screen.blit(resources_surface, (padding, info_y))

    # Afficher les unités (types et nombre)
    unit_counts = Counter(Unit.acronym for unit in selected_player.units)
    units_text = "Units - " + ", ".join([f"{acronym}: {count}" for acronym, count in unit_counts.items()])
    units_surface = font.render(units_text, True, (255, 255, 255))
    screen.blit(units_surface, (padding, info_y + 30))

    # Afficher les bâtiments (types et nombre)
    building_counts = Counter(building.acronym for building in selected_player.buildings)
    buildings_text = "Buildings - " + ", ".join([f"{acronym}: {count}" for acronym, count in building_counts.items()])
    buildings_surface = font.render(buildings_text, True, (255, 255, 255))
    screen.blit(buildings_surface, (padding, info_y + 60))
    
    