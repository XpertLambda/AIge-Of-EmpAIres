# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Bot.py
import math
import time
from Models.Team import *
from Settings.setup import RESOURCE_THRESHOLDS, TILE_SIZE
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import Building, Keep, Barracks, TownCentre, Camp, House, Farm, Stable, ArcheryRange
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Unit import *
from Entity.Resource import *
from Models.Map import GameMap
from random import *
from AiUtils.aStar import a_star
from Controller.Decisonnode import * # Import DecisionNode and trees

class Bot:
    def __init__(self, team, game_map, players, mode, difficulty='medium'):
        self.team = team
        self.game_map = game_map
        self.difficulty = difficulty
        self.mode = mode

        self.decision_tree = None
        self.enemies = [team for team in game_map.players if team.teamID != self.team.teamID]
        self.players_target = game_map.game_state.get('players_target') if game_map.game_state else [None] * len(players)

        self.attacking_enemies = None

        self.decision_tree = None
        self.priority = None
        self.ATTACK_RADIUS = 5  # Rayon d'attaque pour détecter les ennemis
        self.PRIORITY_UNITS = {
            'a': 3,  # Archers
            's': 2,  # Swordsmen
            'h': 1   # Horsemen
        }

    def update(self, game_map, dt):
        self.decision_tree = self.create_mode_decision_tree()
        self.decision_tree.evaluate()

    def set_priority(self, priority):
        self.priority = priority

    def get_resource_shortage(self):
        RESOURCE_MAPPING = {
            "food": Farm,
            "wood": Tree,
            "gold": Gold,
        }
        
        resources = self.team.resources  # Utilisation directe des ressources actuelles de l'équipe
        debug_print(f'Team resources: {resources}')
        
        # Vérifier s'il y a une pénurie en comparant avec RESOURCE_THRESHOLDS
        for resource in ["food", "wood", "gold"]:
            if getattr(resources, resource) < getattr(RESOURCE_THRESHOLDS, resource):
                return RESOURCE_MAPPING[resource]
        
        return None  # Aucune pénurie détectée



    def reallocate_villagers(self, Resource):
        available_villagers = [unit for unit in self.team.units
                               if isinstance(unit, Villager) and unit.isAvailable()]
        available_farms = [farm for farm in self.team.buildings
                           if isinstance(farm, Farm)]
        
        for villager in available_villagers:
            drop_points = [b for b in self.team.buildings if b.resourceDropPoint]
            if not drop_points:
                return
            nearest_drop_point = min(
                drop_points,
                key=lambda dp: math.dist((villager.x, villager.y), (dp.x, dp.y))
            )

            if issubclass(Resource, Farm):
                if not available_farms:
                    if not available_villagers:
                        closest_buildable_position = None
                        min_distance = float('inf')
                        # Try to find a 2x2 area for a farm
                        nx, ny = int(nearest_drop_point.x), int(nearest_drop_point.y)
                        search_range = 10  # Adjust as needed
                        closest_buildable_position = None
                        min_distance = float('inf')

                        for dx in range(-search_range, search_range + 1):
                            for dy in range(-search_range, search_range + 1):
                                x = nx + dx
                                y = ny + dy
                                # Check 2x2 area is buildable
                                if (self.game_map.buildable_position(x, y, size = 4)):
                                    distance = math.dist((nx, ny), (x, y))
                                    if distance < min_distance:
                                        min_distance = distance
                                        closest_buildable_position = (x, y)

                        if closest_buildable_position:
                            x, y = closest_buildable_position
                            # Attempt building at the discovered position
                            if self.team.build('Farm', x, y, 1, self.game_map, True):
                                return
                    else:
                        closest_buildable_position = None
                        min_distance = float('inf')
                        for x, y in self.team.zone.get_zone():
                            if (self.game_map.buildable_position(x, y, size = 4)):
                                distance = math.dist((nearest_drop_point.x, nearest_drop_point.y), (x, y))
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_buildable_position = (x, y)
                        if closest_buildable_position:
                            x, y = closest_buildable_position
                            if self.team.build('Farm', x, y, 1, self.game_map):
                                return

            resource_locations = []
            for pos, entities in self.game_map.resources.items():
                if entities:
                    for entity in entities:
                        if isinstance(entity, Resource):
                            resource_locations.append((pos, entity))
            
            if resource_locations:
                closest_resource = min(
                    resource_locations,
                    key=lambda pos_entity: math.dist(
                        (nearest_drop_point.x, nearest_drop_point.y),
                        pos_entity[0]
                    )
                )
                villager.set_target(closest_resource[1])
                break

    def priority7(self):
        resource_shortage = self.get_resource_shortage()
                
        debug_print(f'Reallocating villagers to {resource_shortage.__name__}')
        self.reallocate_villagers(resource_shortage)


    def search_for_target(self, unit, enemy_team, attack_mode=True):
        if enemy_team==None:
            return
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

        unit.set_target(closest_entity)
        return unit.attack_target is not None

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

    def priority_2(self, players, selected_player, players_target):
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

    def create_mode_decision_tree(self): 
        if self.mode == 'offensif':
            return create_economic_decision_tree(self)
            #return create_offensive_decision_tree(self, enemy_team, game_map, dt, players, players_target)
        elif self.mode == 'defensif':
            return create_economic_decision_tree(self)
            #return create_defensive_decision_tree(self, enemy_team)
        elif self.mode == 'economic':
            return create_economic_decision_tree(self)
        else:
            return create_default_decision_tree(self)

    def scout_map(self, game_map):
        town_centre = next((building for building in self.team.buildings if isinstance(building, TownCentre)), None)
        if not town_centre:
            return

        base_x, base_y = int(town_centre.x), int(town_centre.y)

        scout_radius = 10
        scout_area = [(x, y) for x in range(base_x - scout_radius, base_x + scout_radius)
                    for y in range(base_y - scout_radius, base_y + scout_radius)]

        for (x, y) in scout_area:
            resources_at_tile = game_map.resources.get((x, y))

            if resources_at_tile:
                for resource in resources_at_tile:
                    resource_type = resource.__class__.__name__.lower()
                    if resource_type in ['wood', 'gold']:
                        self.reallocate_villagers(resource_type)

            for enemy_team in game_map.players:
                if enemy_team.teamID != self.team.teamID:
                    for enemy in enemy_team.units:
                        if enemy.x == x and enemy.y == y:
                            if isinstance(enemy, Horseman):
                                self.PRIORITY_UNITS['archer'] = 4
                            elif isinstance(enemy, Archer):
                                self.PRIORITY_UNITS['swordsman'] = 3

        if self.team.resources.wood < 100:
            self.balance_units()
        if self.team.resources.gold < 50:
            self.balance_units()
    '''
    def easy_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            if random.random() < 0.5:
                self.balance_units()
            if random.random() < 0.3:
                self.build_structure()
            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                self.gather_units_for_defense(critical_points, enemy_team, game_map, dt)

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
                        target = self.find_target_for_unit(unit)
                        if target:
                            unit.set_target(target)

            if self.is_under_attack(enemy_team):
                self.defend_under_attack(enemy_team, game_map, dt)
    '''
    def get_military_units(self, player=None): # Modified to accept player, default to self
        player_to_check = player if player else self.team
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

            for building in self.team.buildings:
                if building.acronym == building_type[0]:
                    if hasattr(building, 'add_to_training_queue'):
                        building.add_to_training_queue(self.team)
                        return

    def is_under_attack(self):
        attacking_enemies = []  # Initialize an empty list to store attacking enemies
        zone = self.team.zone.get_zone()
        for tile in zone:
            entities = self.game_map.grid.get(tile, None)
            if entities:  # Check if entities is not None before iterating
                for entity in entities:
                    if isinstance(entity, Unit) and entity.team != self.team.teamID:
                        attacking_enemies.append(entity)
        return attacking_enemies
        
    def get_critical_points(self):
        if not self.team.buildings:
            return []
        critical_points = [building for building in self.team.buildings if building.hp / building.max_hp < 0.3]
        critical_points.sort(key=lambda b: b.hp / b.max_hp)
        return critical_points

    def build_defensive_structure(self, building_type,  num_builders):
     critical_points= self.get_critical_points()
     if critical_points:
        for point in critical_points:
             self.team.build(building_type, point.x, point.y ,num_builders,self.game_map)

    def gather_units_for_defense(self, units_per_target=2):
        # Dictionary to track the number of units assigned to each target
        target_counts = {}

        for unit in self.team.units:
            if not hasattr(unit, 'carry') and not unit.target:
                for target in self.targets:
                    if target not in target_counts:
                        target_counts[target] = 0

                    if target_counts[target] < units_per_target:
                        unit.set_target(target)
                        target_counts[target] += 1
                        break


    def defend_under_attack(self):
        #self.modify_target( None, players_target) # players_target is not used in defend_under_attack
        self.gather_units_for_defense()
        self.balance_units()
        self.build_defensive_structure("Keep", 3)
        #self.manage_battle(self.team,None,enemy_team,self.game_map, dt) # players_target is None here

    def priorty1(self):
        self.defend_under_attack()

    def balance_units(self):
        villager_count = sum(1 for unit in self.team.units if isinstance(unit, Villager))
        military_units = self.get_military_units()
        military_count = len(military_units)

        MAX_QUEUE_SIZE = 5
        PRIORITY_UNITS = self.PRIORITY_UNITS # Use self.PRIORITY_UNITS

        if self.team.resources.food < 100 and villager_count < 20: # Increased villager count condition
            for building in self.team.buildings:
                if building.acronym == 'T':
                    if len(building.training_queue) < MAX_QUEUE_SIZE:
                        self.train_units(Villager)
                        break

        elif military_count < 30: # Increased military count condition
            best_building = None
            best_priority = -1
            for building in self.team.buildings:
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
            available_units = [unit for unit in self.team.units if isinstance(unit, unit_type)]

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
                        target = self.find_target_for_unit(unit)
                        if target:
                            unit.set_target(target)
                    elif unit.target:
                        unit.attack()
                    else:
                        unit.setIdle()

    def check_building_needs(self):
        needed_buildings = []
        if not any(isinstance(building, Barracks) for building in self.team.buildings):
            needed_buildings.append("Barracks")
        if not any(isinstance(building, TownCentre) for building in self.team.buildings):
            needed_buildings.append("TownCentre")
        if not any(isinstance(building, Camp) for building in self.team.buildings):
            needed_buildings.append("Camp")
        if not any(isinstance(building, House) for building in self.team.buildings):
            needed_buildings.append("House")
        if not any(isinstance(building, Keep) for building in self.team.buildings):
            needed_buildings.append("Keep")
        if not any(isinstance(building, Farm) for building in self.team.buildings):
            needed_buildings.append("Farm")
        if not any(isinstance(building, Stable) for building in self.team.buildings):
            needed_buildings.append("Stable")
        if not any(isinstance(building, ArcheryRange) for building in self.team.buildings):
            needed_buildings.append("ArcheryRange")
        return needed_buildings

    def find_building_location(self, building_type):
        for x in range(10, self.game_map.width - 10):
            for y in range(10, self.game_map.height - 10):
                if self.game_map.walkable_position((x, y)): # Changed to walkable_position
                    enemy_nearby = False
                    for enemy_team in self.game_map.players:
                        if enemy_team.teamID != self.team.teamID:
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
        building_cost = building_class.cost
        return (self.team.resources["wood"] >= building_cost.wood and
                self.team.resources["gold"] >= building_cost.gold and
                self.team.resources["food"] >= building_cost.food)

    # def buildBuilding(self, building, clock, nb, game_map):
    #     """Build a building if resources are sufficient."""
    #     if not self.can_build_building(building.__class__):
    #         return False

    #     location = self.find_building_location(building.__class__.__name__)  # Find location based on building type name
    #     if location:
    #         x, y = location
    #         building.x, building.y = x, y # Set building position before adding to game map
    #         return self.team.buildBuilding(building, clock, nb, game_map) # Delegate to team's buildBuilding

    def build_structure(self):
        needed_buildings = self.check_building_needs()
        if not needed_buildings:
            return False
        for building_type in needed_buildings:
            if building_type in building_class_map:
                building_class = building_class_map[building_type]
                if not hasattr(building_class, 'cost'):
                    continue
                building_cost = building_class.cost
                if (self.team.resources["wood"] >= building_cost.wood and
                    self.team.resources["gold"] >= building_cost.gold and
                    self.team.resources["food"] >= building_cost.food):
                    location = self.find_building_location(building_type)
                    if location:
                        x, y = location
                        building = building_class(team=self.team.teamID, x=x, y=y)
                        if self.team.build(self.team, building, x, y, self.game_map, num_builders=1):
                            return True
        return False