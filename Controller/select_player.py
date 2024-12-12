# 5) Controller/select_player.py
# La couleur du bouton reflète maintenant la couleur d'équipe définie dans drawing.py

import pygame
from collections import Counter
from Settings.setup import NUMBER_OF_PLAYERS
from Controller.drawing import TEAM_COLORS

def create_player_selection_surface(players, selected_player, minimap_rect):
    selection_height = 30
    padding = 5

    # Obtenir la hauteur de l'écran
    screen = pygame.display.get_surface()
    screen_height = screen.get_height()
    max_height = screen_height / 3  # Taille maximale de 1/3 de la fenêtre

    # Déterminer le nombre optimal de colonnes
    columns = 1
    while columns <= 4:
        rows = (len(players) + columns - 1) // columns
        total_height = selection_height * rows + padding * (rows - 1)
        if total_height <= max_height or columns == 4:
            break
        columns += 1

    button_width = (minimap_rect.width - padding * (columns - 1)) // columns
    rows = (len(players) + columns - 1) // columns
    total_height = selection_height * rows + padding * (rows - 1)

    surface = pygame.Surface((minimap_rect.width, total_height), pygame.SRCALPHA)

    for index, player in enumerate(reversed(players)):
        col = index % columns
        row = index // columns
        rect_x = col * (button_width + padding)
        rect_y = row * (selection_height + padding)
        rect = pygame.Rect(rect_x, rect_y, button_width, selection_height)
        player_color = TEAM_COLORS[player.teamID % len(TEAM_COLORS)]

        # Si c'est le joueur sélectionné, on accentue la couleur, sinon on l'assombrit
        if player == selected_player:
            color = player_color
        else:
            color = tuple(min(255, c+50) for c in player_color)

        pygame.draw.rect(surface, color, rect)

        font = pygame.font.Font(None, 24)
        text = font.render(f"Player {player.teamID}", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)

    return surface

def create_player_info_surface(selected_player, screen_width):
    font = pygame.font.Font(None, 24)
    padding = 5
    info_height = 130
    surface = pygame.Surface((screen_width, info_height), pygame.SRCALPHA)

    player_name_surface = font.render(f"Player {selected_player.teamID}", True, (255, 255, 255))
    surface.blit(player_name_surface, (padding, 0))

    resources_text = f"Resources - Food: {selected_player.resources['food']}, Wood: {selected_player.resources['wood']}, Gold: {selected_player.resources['gold']}"
    resources_surface = font.render(resources_text, True, (255, 255, 255))
    surface.blit(resources_surface, (padding, 30))

    unit_counts = Counter(unit.acronym for unit in selected_player.units)
    units_text = "Units - " + ", ".join([f"{acronym}: {count}" for acronym, count in unit_counts.items()])
    units_surface = font.render(units_text, True, (255, 255, 255))
    surface.blit(units_surface, (padding, 60))

    building_counts = Counter(building.acronym for building in selected_player.buildings)
    buildings_text = "Buildings - " + ", ".join([f"{acronym}: {count}" for acronym, count in building_counts.items()])
    buildings_surface = font.render(buildings_text, True, (255, 255, 255))
    surface.blit(buildings_surface, (padding, 90))

    return surface
