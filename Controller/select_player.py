import pygame
from collections import Counter
from Models.Team import *
# Supprimer l'importation de TEAM_COLORS
# from Controller.drawing import TEAM_COLORS

def create_player_selection_surface(players, selected_player, minimap_rect, team_colors):
    selection_height = 30
    padding = 5

    # Get screen height
    screen = pygame.display.get_surface()
    screen_height = screen.get_height()
    max_height = screen_height / 3  # Taille maximale de 1/3 de la fenêtre

    # Determine the optimal number of columns
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

    font = pygame.font.Font(None, 24)

    for index, player in enumerate(reversed(players)):
        col = index % columns
        row = index // columns
        rect_x = col * (button_width + padding)
        rect_y = row * (selection_height + padding)
        rect = pygame.Rect(rect_x, rect_y, button_width, selection_height)

        if player == selected_player:
            color = (255, 255, 255)
        else:
            color = team_colors[player.teamID % len(team_colors)]

        pygame.draw.rect(surface, color, rect)

        player_text = font.render(f'Player {player.teamID}', True, (0, 0, 0))
        text_rect = player_text.get_rect(center=rect.center)
        surface.blit(player_text, text_rect)

    return surface

def create_player_info_surface(selected_player, screen_width, team_colors):
    font = pygame.font.Font(None, 24)
    padding = 5
    info_height = 160
    surface = pygame.Surface((screen_width, info_height), pygame.SRCALPHA)

    team_color = team_colors[selected_player.teamID % len(team_colors)]
    player_name_surface = font.render(f"Player {selected_player.teamID}", True, team_color)
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

    print(f"select player - maximum population: {selected_player.maximum_population}")
    maximum_population_text = (f"Maximum population : {selected_player.maximum_population}")
    maximum_population = font.render(maximum_population_text, True, (255, 255, 255))
    surface.blit(maximum_population, (padding, 120))

    return surface
