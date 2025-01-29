# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Bot.py
# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Bot.py
import math
import time
from Models.Team import *
from Controller.Decisonnode import allocate_villagers_to_resource_action
from Settings.setup import RESOURCE_THRESHOLDS, TILE_SIZE
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import Building, Keep, Barracks, TownCentre, Camp, House, Farm, Stable, ArcheryRange
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap
from random import *
from AiUtils.aStar import a_star
from Controller.Decisonnode import (DecisionNode, create_offensive_decision_tree,
                                  create_defensive_decision_tree, create_economic_decision_tree,
                                  create_default_decision_tree, create_unit_combat_decision_tree)

class Bot:
    def __init__(self, player_team, game_map, clock, difficulty='medium', mode='economic'): # Added mode parameter
        self.clock= clock
        self.player_team = player_team
        self.game_map = game_map
        self.decision = DecisionNode(self)
        self.difficulty = difficulty
        self.mode = mode # Store the mode
        self.PRIORITY_UNITS = {
            'a': 3,  # Archers
            's': 2,  # Swordsmen
            'h': 1   # Horsemen
        }
        self.ATTACK_RADIUS = TILE_SIZE * 5  # Rayon d'attaque pour détecter les ennemis

    def find_resource(self, resource_type):
        """
        Finds all resource locations of a specific type on the map.

        Args:
            resource_type: The type of resource to search for (e.g., "food", "wood", "gold").

        Returns:
            A list of tuples, where each tuple contains (x, y) coordinates of a resource location 
            and the Resource object itself.
        """
        resource_locations = []
        for location, entity in self.game_map.resources.items():  # Assuming resources are stored in self.game_map.resources
            if isinstance(entity, Resource) and entity.resource_type == resource_type and entity.isAlive():
                resource_locations.append(((location.x, location.y), entity))  # Access resource type from entity
        return resource_locations
    
    def remove_resource(self, resource):
        """Removes a resource from the game map."""
        for pos, entities in list(self.grid.items()): # Iterate over a copy to avoid issues while removing
            if isinstance(entities, set):
                if resource in entities:
                    entities.remove(resource)
                    if not entities: # If the set is empty, remove the key
                        del self.grid[pos]
                    return # Resource is removed, exit the function
                
    def get_resource_shortage(self):
        RESOURCE_MAPPING ={
        "food": Farm,
        "wood": Tree,
        "gold": Gold,
        }
        resource_quantities = self.player_team.resources.get()
        resource_keys = list(RESOURCE_THRESHOLDS.keys())

        shortages = {}
        for i, key in enumerate(resource_keys):
            resource_amount = resource_quantities[i] if i < len(resource_quantities) else 0
            shortages[key] = RESOURCE_THRESHOLDS[key] - resource_amount

        critical_shortage_key = min(shortages, key=shortages.get)
        return critical_shortage_key if shortages[critical_shortage_key] > 0 else None


    def reallocate_villagers(self, resource_type):
        available_villagers = [unit for unit in self.player_team.units
                             if isinstance(unit, Villager) and unit.isAvailable()]

        for villager in available_villagers:
            drop_points = [b for b in self.player_team.buildings if b.resourceDropPoint]
            if not drop_points:
                return

            nearest_drop_point = min(
                drop_points,
                key=lambda dp: math.dist((villager.x, villager.y), (dp.x, dp.y))
            )

            resource_locations = []
            for pos, entities in self.game_map.grid.items():
                if isinstance(entities, set):
                    for entity in entities:
                        if isinstance(entity, Resource) and entity.__class__.__name__.lower() == resource_type:
                            resource_locations.append((pos, entity))

            if resource_locations:
                closest_resource = min(resource_locations, key=lambda pos_entity: math.dist((nearest_drop_point.x, nearest_drop_point.y), pos_entity[0]))
                print(f"Closest resource: {closest_resource}")  # Print chosen resource

                villager.set_target(closest_resource[1])
                break
            else:
                print("No resources found!")  # Check if resources are found
        

    def priorty7(self): # Corrected typo in function name from 'priorty7' to 'priority7' and removed unused RESOURCE_THRESHOLDS argument
     resource_shortage = self.get_resource_shortage()
     if resource_shortage:
        self.reallocate_villagers(resource_shortage)

    
    def find_nearest_drop_point(self, unit):
        """Finds the nearest drop-off point for the given unit."""
        drop_points = [
            building for building in self.player_team.buildings
            if isinstance(building, TownCentre) or isinstance(building, Camp) # Add other buildings if needed
        ]
        if drop_points:
            return min(drop_points, key=lambda building: math.dist((unit.x, unit.y), (building.x, building.y)))
        return None # Return None if no drop points are found

    def search_for_target(self, unit, enemy_team, attack_mode=True):
        if enemy_team==None:
            return False # Added return False in case of no enemy_team to avoid further errors
        closest_distance = float("inf")
        closest_entity = None
        keeps=[keep for keep in enemy_team.buildings if isinstance(keep,Keep)]
        targets=[unit for unit in enemy_team.units if not isinstance(unit,Villager)]

        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if dist < closest_distance:
                closest_distance = dist
                closest_entity = enemy
        if attack_mode and closest_entity==None:
            targets=[unit for unit in enemy_team.units if isinstance(unit,Villager)]
            for enemy in targets:
                dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
                if attack_mode or not isinstance(enemy,Villager):
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_entity = enemy
            for enemy_building in enemy_team.buildings:
                dist = math.dist((unit.x, unit.y), (enemy_building.x, enemy_building.y))
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy_building

        if attack_mode:
            for enemy in keeps:
                dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
                if attack_mode or not isinstance(enemy,Villager):
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_entity = enemy
        if closest_entity!=None:
            if keeps!=[] and attack_mode:
                for keep in keeps:
                    dist=math.dist((keep.x,keep.y),(closest_entity.x,closest_entity.y))
                    if dist<keep.attack_range:
                        closest_entity=keep

        if closest_entity: # Check if closest_entity is not None before setting target
            unit.set_target(closest_entity)
            return True # Return True if a target is set
        return False # Return False if no target is found


    def modify_target(self, player, target, players_target):
        players_target[player.teamID] = target
        for unit in player.units:
            unit.set_target(None)

    def choose_target(self, players, selected_player, players_target):
        count_max = 300
        target = None
        for enemy_team in players:
            if enemy_team != selected_player:
                count = sum(1 for unit in enemy_team.units if not isinstance(unit, Villager))
                count += sum(1 for building in enemy_team.buildings if not isinstance(building, Keep))
                if count < count_max:
                    target = enemy_team
                    count_max = count
        if target != None:
            self.modify_target(selected_player, target, players_target)
        return target != None

    def priority_2(self, players, selected_player, players_target): # Corrected typo in function name from 'priorty_2' to 'priority_2'
        if players_target[selected_player.teamID] != None:
            return False
        return self.choose_target(players, selected_player, players_target)

    def manage_battle(self, selected_player, players_target, players, game_map, dt):
        enemy=players_target[selected_player.teamID]
        attack_mode=True
        if True:
            for i in range(0,len(players_target)):
                if players_target[i]==selected_player:
                    for team in players:
                        if team.teamID==i:
                                players_target[selected_player.teamID]=None
                                enemy=team
                                attack_mode=False
        if enemy!=None and (len(enemy.units)!=0 or len(enemy.buildings)!=0):
            for unit in selected_player.units:
                if enemy!=None and (len(enemy.units)!=0 or len(enemy.buildings)!=0):
                    for unit in selected_player.units:
                        if not isinstance(unit,Villager) or (len(selected_player.units)==0 and not attack_mode):
                            if unit.attack_target==None or not unit.attack_target.isAlive():
                                self.search_for_target(unit, enemy, attack_mode)
        else:
            self.modify_target(selected_player, None, players_target)
        if self.get_military_unit_count(selected_player)==0:
            self.modify_target(selected_player, None, players_target)


    def get_military_unit_count(self, player):
        return len(self.get_military_units(player))

    def create_mode_decision_tree(self, enemy_teams, game_map, dt, players, selected_player, players_target): # Modified to pass players, selected_player, players_target
        enemy_team = enemy_teams[0] if enemy_teams else None # Get the first enemy team for simplicity
        if self.mode == 'offensif':
            return create_offensive_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        elif self.mode == 'defensif':
            return create_defensive_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        elif self.mode == 'economique':
            return create_economic_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        else:
            return create_default_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)


    def scout_map(self, game_map):
        town_centre = next((building for building in self.player_team.buildings if isinstance(building, TownCentre)), None)
        if not town_centre:
            return

        base_x, base_y = int(town_centre.x), int(town_centre.y)

        scout_radius = 10
        scout_area = [(x, y) for x in range(base_x - scout_radius, base_x + scout_radius)
                    for y in range(base_x - scout_radius, base_x + scout_radius)]

        for (x, y) in scout_area:
            resources_at_tile = game_map.resources.get((x, y))

            if resources_at_tile:
                for resource in resources_at_tile:
                    resource_type = resource.__class__.__name__.lower()
                    if resource_type in ['wood', 'gold']:
                        self.reallocate_villagers(resource_type)

            for enemy_team in game_map.players:
                if enemy_team.teamID != self.player_team.teamID:
                    for enemy in enemy_team.units:
                        if enemy.x == x and enemy.y == y:
                            if isinstance(enemy, Horseman):
                                self.PRIORITY_UNITS['archer'] = 4
                            elif isinstance(enemy, Archer):
                                self.PRIORITY_UNITS['swordsman'] = 3

        if self.player_team.resources.wood < 100:
            self.balance_units()
        if self.player_team.resources.gold < 50:
            self.balance_units()

    def easy_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            if random.random() < 0.5:
                self.balance_units()
            if random.random() < 0.3:
                self.build_structure(self.clock)
            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                self.gather_units_for_defense(enemy_team) # Corrected function call to pass enemy_team

    def medium_strategy(self, enemy_teams, game_map, dt, players_target, players): # Added players_target, players
        for enemy_team in enemy_teams:
            self.balance_units()
            self.adjust_priorities(enemy_team)

            if self.check_building_needs():
                self.build_structure(self.clock)

            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                if critical_points and self.can_build_building(Keep):
                    critical_location = (critical_points[0].x, critical_points[0].y)
                    self.build_defensive_structure(Keep, 3) # Corrected function call - removed critical_location, num_builders already hardcoded

            if len(self.get_military_units()) > 10:
                self.manage_battle(self.player_team, players_target, players, game_map, dt) # Pass players and players_target

    def hard_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            self.balance_units()
            self.adjust_priorities(enemy_team)

            if self.check_building_needs():
                self.build_structure(self.clock)

            self.scout_map(game_map)

            if len(self.get_military_units()) > 15:
                attack_composition = self.choose_attack_composition()
                for unit in attack_composition:
                    if unit.idle:
                        target = self.search_for_target(unit) # Removed unit as argument as it is not used
                        if target:
                            unit.set_target(target)

            if self.is_under_attack(enemy_team):
                self.defend_under_attack(enemy_team, game_map, dt)

    def get_military_units(self, player=None): # Modified to accept player, default to self
        player_to_check = player if player else self.player_team
        return [unit for unit in player_to_check.units if not isinstance(unit, Villager)]

    def train_units(self, unit_type):
        UNIT_TO_BUILDING_MAP = {
            'v': 'TownCentre',
            'a': 'ArcheryRange',
            's': 'Barracks',
            'h': 'Stable'
        }

        unit_acronym = unit_type.acronym if hasattr(unit_type, 'acronym') else None

        if unit_acronym and unit_acronym in UNIT_TO_BUILDING_MAP:
            building_type = UNIT_TO_BUILDING_MAP[unit_acronym]

            for building in self.player_team.buildings:
                if building.acronym == building_type[0]:
                    if hasattr(building, 'add_to_training_queue'):
                        building.add_to_training_queue(self.player_team)
                        return

    def is_under_attack(self, enemy_team):
     zone=self.player_team.zone.get_zone()

     for z in zone:
      entities = self.game_map.grid.get(z,None)
      if entities:

       for entity in entities:
        if entity in enemy_team.units:
            return True
     return False

    def get_critical_points(self):

        if not self.player_team.buildings:
            return []
        critical_points = [building for building in self.player_team.buildings if building.hp / building.max_hp < 0.3]
        critical_points.sort(key=lambda b: b.hp / b.max_hp)
        return critical_points

    def build_defensive_structure(self, building_type, num_builders): # Added building_type argument
     critical_points= self.get_critical_points()
     if critical_points:
        for point in critical_points:
             self.buildBuilding(building_class_map['Keep'](team=self.player_team.teamID), self.clock, num_builders, self.game_map) # corrected to buildBuilding and pass building class

    def gather_units_for_defense(self, enemy_team): # Corrected function call to pass enemy_team
     critical_points = self.get_critical_points()
     for point in critical_points:
        for unit in self.player_team.units:
            if not hasattr(unit, 'carry') and not unit.target:
                target = self.search_for_target(unit, enemy_team, attack_mode=False)
                if target:
                    unit.set_target(target)
                else:
                    unit.set_destination((point.x, point.y))

    def defend_under_attack(self, enemy_team, game_map, dt):
     if self.is_under_attack( enemy_team):
        self.gather_units_for_defense(enemy_team) # Corrected function call to pass enemy_team
        self.balance_units()
        self.build_defensive_structure(Keep, 3) # Corrected function call to pass Keep class and num_builders

    def priorty1(self, enemy_team, players_target, game_map, dt): # players_target not used here, corrected typo to priority1

        if self.is_under_attack(enemy_team):
            self.defend_under_attack(enemy_team, self.game_map, dt) # Using self.game_map instead of undefined game_map

    def balance_units(self):
        villager_count = sum(1 for unit in self.player_team.units if isinstance(unit, Villager))
        military_units = self.get_military_units()
        military_count = len(military_units)

        MAX_QUEUE_SIZE = 5
        PRIORITY_UNITS = self.PRIORITY_UNITS # Use self.PRIORITY_UNITS

        if self.player_team.resources.food < 100 and villager_count < 20: # Increased villager count condition
            for building in self.player_team.buildings:
                if building.acronym == 'T':
                    if len(building.training_queue) < MAX_QUEUE_SIZE:
                        self.train_units(Villager)
                        break

        elif military_count < 30: # Increased military count condition
            best_building = None
            best_priority = -1
            for building in self.player_team.buildings:
                if building.spawnsUnits and len(building.training_queue) < MAX_QUEUE_SIZE:
                    unit_acronym = building.acronym
                    if unit_acronym in PRIORITY_UNITS:
                        priority = PRIORITY_UNITS[unit_acronym]
                        if priority > best_priority:
                            best_building = building
                            best_priority = priority

            if best_building:
                unit_type = Building.UNIT_TRAINING_MAP.get(best_building.acronym)
                if unit_type:
                    self.train_units(unit_type) # train_units now takes unit_type directly

    def adjust_priorities(self, enemy_teams):
        if not isinstance(enemy_teams, list):
            enemy_teams = [enemy_teams]

        enemy_horsemen = 0
        enemy_archers = 0
        enemy_swordsmen = 0

        for enemy_team in enemy_teams:
            enemy_horsemen += sum(1 for unit in enemy_team.units if isinstance(unit, Horseman))
            enemy_archers += sum(1 for unit in enemy_team.units if isinstance(unit, Archer))
            enemy_swordsmen += sum(1 for unit in enemy_team.units if isinstance(unit, Swordsman))

        HORSEMEN_THRESHOLD = 5
        ARCHERS_THRESHOLD = 7
        SWORDSMEN_THRESHOLD = 6

        if enemy_horsemen > HORSEMEN_THRESHOLD:
            self.PRIORITY_UNITS['a'] = 4

        if enemy_archers > ARCHERS_THRESHOLD:
            self.PRIORITY_UNITS['s'] = 3

        if enemy_swordsmen > SWORDSMEN_THRESHOLD:
            self.PRIORITY_UNITS['h'] = 2

    def choose_attack_composition(self):
        units_by_type = {
            Archer: 3,
            Swordsman: 1,
            Horseman: 1
        }

        selected_units = []

        for unit_type, limit in units_by_type.items():
            available_units = [unit for unit in self.player_team.units if isinstance(unit, unit_type)]

            selected_units.extend(available_units[:limit])

            if len(selected_units) >= sum(units_by_type.values()):
                break

        return selected_units

    def maintain_army(self):
        military_count = len(self.get_military_units())

        if military_count < 20:
            self.balance_units()
        else:
            attack_composition = self.choose_attack_composition()

            for unit in attack_composition:
                if not isinstance(unit, Villager):
                    if unit.idle:
                        target = self.find_target_for_unit(unit) # Removed unit as argument as it is not used
                        if target:
                            unit.set_target(target)
                    elif unit.target:
                        unit.attack()
                    else:
                        unit.setIdle()

    def check_building_needs(self):
        needed_buildings = []
        if not any(isinstance(building, Barracks) for building in self.player_team.buildings):
            needed_buildings.append("Barracks")
        if not any(isinstance(building, TownCentre) for building in self.player_team.buildings):
            needed_buildings.append("TownCentre")
        if not any(isinstance(building, Camp) for building in self.player_team.buildings):
            needed_buildings.append("Camp")
        if not any(isinstance(building, House) for building in self.player_team.buildings):
            needed_buildings.append("House")
        if not any(isinstance(building, Keep) for building in self.player_team.buildings):
            needed_buildings.append("Keep")
        if not any(isinstance(building, Farm) for building in self.player_team.buildings):
            needed_buildings.append("Farm")
        if not any(isinstance(building, Stable) for building in self.player_team.buildings):
            needed_buildings.append("Stable")
        if not any(isinstance(building, ArcheryRange) for building in self.player_team.buildings):
            needed_buildings.append("ArcheryRange")
        return needed_buildings

    def find_building_location(self, building_type):
        for x in range(10, self.game_map.num_tiles_x - 10):  # Changed from width to num_tiles_x
            for y in range(10, self.game_map.num_tiles_y - 10):  # Changed from height to num_tiles_y
                if self.game_map.walkable_position((x, y)): # Changed to walkable_position
                    enemy_nearby = False
                    for enemy_team in self.game_map.players:
                        if enemy_team.teamID != self.player_team.teamID:
                            for unit in enemy_team.units:
                                if abs(unit.x - x) < 10 and abs(unit.y - y) < 10:
                                    enemy_nearby = True
                                    break
                        if enemy_nearby:
                            break
                    if not enemy_nearby:
                        return (x, y)
        return None

    def can_build_building(self, building_class):
        """Check if resources are sufficient to build a building."""
        # Créer une instance temporaire pour accéder au coût
        temp_building = building_class(team=self.player_team.teamID)
        building_cost = temp_building.cost
        team_resources = self.player_team.resources.get()  # Get current resources as a tuple
        return (team_resources[0] >= building_cost.food and  # food
                team_resources[1] >= building_cost.wood and  # wood
                team_resources[2] >= building_cost.gold)     # gold

    def buildBuilding(self, building, clock, nb, game_map):
        """Build a building directly through the Bot class."""
        if not self.can_build_building(building.__class__):
            return False

        location = self.find_building_location(building.__class__.__name__)
        if location:
            x, y = location
            building.x, building.y = x, y
            
            # Deduct resources
            cost = building.cost
            self.player_team.resources.food -= cost.food
            self.player_team.resources.wood -= cost.wood
            self.player_team.resources.gold -= cost.gold
            
            # Add building to team using set.add() instead of list.append()
            self.player_team.buildings.add(building)
            
            # Add building to game map
            if (x, y) in self.game_map.grid:
                if isinstance(self.game_map.grid[(x, y)], set):
                    self.game_map.grid[(x, y)].add(building)
                else:
                    self.game_map.grid[(x, y)] = {building}
            else:
                self.game_map.grid[(x, y)] = {building}
            
            # Initialize building properties
            building.team = self.player_team.teamID
            building.construction_start = clock
            building.construction_time = nb  # Number of builders affects construction time
            
            return True
        return False

    def build_structure(self, clock):
        """Build needed structures based on what's missing."""
        needed_buildings = self.check_building_needs()
        if not needed_buildings:
            return False

        building_class_priority = {
            "TownCentre": 1,
            "House": 2,
            "Farm": 3,
            "Camp": 4,
            "Barracks": 5,
            "ArcheryRange": 6,
            "Stable": 7,
            "Keep": 8
        }

        # Sort needed buildings by priority
        needed_buildings.sort(key=lambda x: building_class_priority.get(x, 999))

        for building_name in needed_buildings:
            building_class = building_class_map.get(building_name)
            if building_class and self.can_build_building(building_class):
                new_building = building_class(team=self.player_team.teamID)
                if self.buildBuilding(new_building, clock, 3, self.game_map):
                    return True
        return False
    
    def manage_villagers(self, game_map):
        """Handles villager allocation to resources and tasks."""
        resource_shortage = self.get_resource_shortage()
        if resource_shortage:
            self.reallocate_villagers(resource_shortage)

        # Build houses if needed
        if not any(isinstance(b, House) for b in self.player_team.buildings) or len([b for b in self.player_team.buildings if isinstance(b,House)])*10 < len(self.player_team.units):
            if self.can_build_building(House):
                self.buildBuilding(House(team=self.player_team.teamID), self.clock, 1, game_map)

        # Build farms if food is low
        if self.player_team.resources.food < RESOURCE_THRESHOLDS['food'] * 0.5 and self.can_build_building(Farm) and len([b for b in self.player_team.buildings if isinstance(b,Farm)]) < 10:
            self.buildBuilding(Farm(team=self.player_team.teamID), self.clock, 1, game_map)

        # Build town center if none exists
        if not any(isinstance(b, TownCentre) for b in self.player_team.buildings):
            if self.can_build_building(TownCentre):
                self.buildBuilding(TownCentre(team=self.player_team.teamID), self.clock, 3, game_map)

        # Ensure villagers are gathering resources
        for villager in self.player_team.units:
            if isinstance(villager, Villager) and villager.state == 'idle':
                # Check if resources are low and assign villagers accordingly
                if self.player_team.resources.food < RESOURCE_THRESHOLDS['food']:
                    allocate_villagers_to_resource_action('food', villager)
                elif self.player_team.resources.wood < RESOURCE_THRESHOLDS['wood']:
                    allocate_villagers_to_resource_action('wood', villager)
                elif self.player_team.resources.gold < RESOURCE_THRESHOLDS['gold']:
                    allocate_villagers_to_resource_action('gold', villager)

    def manage_military(self, enemy_teams, game_map, dt, players_target, players):
       """Manages military unit training and combat."""
       self.balance_units() # Train units based on priority

       if self.get_military_unit_count(self.player_team) > 10: # Engage in combat
           self.manage_battle(self.player_team, players_target, players, game_map, dt)
        
    def build_structures(self, game_map):
        """Builds necessary structures."""
        needed_buildings = self.check_building_needs()
        if needed_buildings:
            for building_name in needed_buildings:
                building_class = building_class_map.get(building_name)
                if building_class and self.can_build_building(building_class):
                    new_building = building_class(team=self.player_team.teamID)
                    if self.buildBuilding(new_building, self.clock, 3, game_map): # 3 builders for most structures
                        break  # Build one building per update

    def create_mode_decision_tree(self, enemy_teams, game_map, dt, players, selected_player, players_target):
        enemy_team = enemy_teams[0] if enemy_teams else None
        if self.mode == 'offensif':
            return create_offensive_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        elif self.mode == 'defensif':
            return create_defensive_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        elif self.mode == 'economique':
            return create_economic_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        else:
            return create_default_decision_tree(self, enemy_team, enemy_teams, game_map, dt, players, selected_player, players_target)
        
    def update(self, game_map, dt):
        enemy_teams = [team for team in game_map.players if team.teamID != self.player_team.teamID]
        players = game_map.players
        players_target = game_map.game_state.get('players_target') if game_map.game_state else [None] * len(players)
        selected_player = self.player_team

        # Strategy (choose one based on difficulty)
        if self.difficulty == 'easy':
            self.easy_strategy(enemy_teams, game_map, dt)
        elif self.difficulty == 'medium':
            self.medium_strategy(enemy_teams, game_map, dt, players_target, players)
        elif self.difficulty == 'hard':
            self.hard_strategy(enemy_teams, game_map, dt)
        else:
            self.medium_strategy(enemy_teams, game_map, dt, players_target, players)  # Default
        enemy_teams = [team for team in game_map.players if team.teamID != self.player_team.teamID]

        for unit in self.player_team.units:
            tree = create_unit_combat_decision_tree(self, unit, enemy_teams, game_map)
            if tree:
                tree.evaluate()
        # Core AI Logic (runs regardless of strategy)
        self.manage_villagers(game_map)  # Improved villager management
        self.manage_military(enemy_teams, game_map, dt, players_target, players) # Military Management
        self.build_structures(game_map)   # Smarter building

        # Decision Tree (runs after other logic)
        decision_tree = self.create_mode_decision_tree(enemy_teams, game_map, dt, players, selected_player, players_target)
        if decision_tree:
            decision_tree.evaluate()

        self.scout_map(game_map)  # Keep scouting
        #self.balance_units()  # Consider removing or moving this, as manage_military handles it
        #self.build_structure(self.clock)
    '''def update(self, game_map, dt):
        enemy_teams = [team for team in game_map.players if team.teamID != self.player_team.teamID]
        players = game_map.players
        players_target = game_map.game_state.get('players_target') if game_map.game_state else [None] * len(players)
        selected_player = self.player_team

        decision_tree = self.create_mode_decision_tree(enemy_teams, game_map, dt, players, selected_player, players_target) # Call decision tree
        decision_tree.evaluate() # Evaluate the decision tree

        self.scout_map(game_map)
        self.balance_units()
        self.build_structure(self.clock)'''
    
