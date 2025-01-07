import time
import pygame
import sys
import random
from Models.Map import *
from Entity.Building import *
from Entity.Unit import *
from Models.Team import Team
from Controller.camera import Camera
from Controller.drawing import (
    draw_map,
    compute_map_bounds,
    create_minimap_background,
    display_fps,
    update_minimap_entities,
    draw_minimap_viewport,
    generate_team_colors,
    draw_pointer
)
import copy
from Controller.event_handler import handle_events
from Controller.update import update_game_state
from Controller.isometric_utils import tile_to_screen
from Controller.gui import create_player_selection_surface, create_player_info_surface, get_scaled_gui, draw_gui_elements
from Settings.setup import HALF_TILE_SIZE, MINIMAP_MARGIN, UPDATE_EVERY_N_MILLISECOND, user_choices

PANEL_RATIO = 0.25
BG_RATIO    = 0.20
draw_call_time = 0



'''
#Priorité 1

def can_train_unit(player_team, unit_cost, population_limit):
    return (
        player_team.resources["gold"] >= unit_cost["gold"] and
        player_team.resources["food"] >= unit_cost["food"] and
        len(player_team.units) < population_limit
    )


#Priorité 5

def get_military_unit_count(player_team):
    return sum(1 for unit in player_team.units if isinstance(unit, MilitaryUnit))


def train_units(player_team, unit_type, unit_cost):
    if can_train_unit(player_team, unit_cost, player_team.maximum_population):
        player_team.resources["gold"] -= unit_cost["gold"]
        player_team.resources["food"] -= unit_cost["food"]
        player_team.units.append(unit_type())
        print(f"Unité {unit_type.__name__} formée.")

def balance_units(player_team):
    villager_count = sum(1 for unit in player_team.units if isinstance(unit, Villager))
    military_count = get_military_unit_count(player_team)
    if player_team.resources["food"] < 100 and villager_count < 10:
        train_units(player_team, Villager, {"gold": 0, "food": 50})
    elif military_count < 20:
        train_units(player_team, MilitaryUnit, {"gold": 50, "food": 50})

def maintain_army(player_team):
    military_count = get_military_unit_count(player_team)
    if military_count < 20:
        balance_units(player_team)

#Priorité 6

def get_damaged_buildings(player_team, critical_threshold=0.5):
    return [
        building for building in player_team.buildings
        if building.hp / building.max_hp < critical_threshold
    ]

def can_repair_building(player_team, repair_cost):
    return player_team.resources["wood"] >= repair_cost["wood"]

def assign_villager_to_repair(player_team, building):
    for villager in player_team.units:
        if isinstance(villager, Villager) and not villager.task:
            villager.repair(building)
            print(f"Villageois assigné à la réparation de {building}.")
            return True
    print("Aucun villageois disponible pour réparer.")
    return False

def repair_critical_buildings(player_team):
    damaged_buildings = get_damaged_buildings(player_team)
    for building in damaged_buildings:
        repair_cost = {"wood": 50} # Exemple de coût de réparation
        if can_repair_building(player_team, repair_cost):
            if not assign_villager_to_repair(player_team, building):
                print("Réparation différée faute de ressources ou de main-d'œuvre.")

'''

def get_centered_rect_in_bottom_right(width, height, screen_width, screen_height, margin=10):
    rect = pygame.Rect(0, 0, width, height)
    center_x = screen_width - margin - (width // 2)
    center_y = screen_height - margin - (height // 2)
    rect.center = (center_x, center_y)
    return rect
#def game_loop(screen, game_map, screen_width, screen_height, players):
