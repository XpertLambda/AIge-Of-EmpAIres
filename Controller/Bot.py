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
        
        # Add cooldown tracking to prevent infinite loops
        self.last_action_time = 0
        self.action_cooldown = 2.0  # 2 seconds between major actions
        self.resource_check_cooldown = 3.0  # 3 seconds between resource checks
        self.last_resource_check = 0
        self.last_detected_shortage = None  # Track what shortage was last detected

    def update(self, game_map, dt):
        import time
        current_time = time.time()
        
        # Prevent too frequent decision making
        if current_time - self.last_action_time < self.action_cooldown:
            return
            
        self.decision_tree = self.create_mode_decision_tree()
        result = self.decision_tree.evaluate()
        
        if result:  # Only update cooldown if an action was actually taken
            self.last_action_time = current_time

    def set_priority(self, priority):
        self.priority = priority

    def get_resource_shortage(self):
        import time
        current_time = time.time()
        
        # Rate limit resource checks to prevent spam
        if current_time - self.last_resource_check < self.resource_check_cooldown:
            return self.last_detected_shortage  # Return cached result
            
        self.last_resource_check = current_time
        
        RESOURCE_MAPPING = {
            "food": Farm,
            "wood": Tree,
            "gold": Gold,
        }
        
        resources = self.team.resources  # Utilisation directe des ressources actuelles de l'équipe
        print(f'Team {self.team.teamID} resources: {resources}')
        
        # Check for shortages with more reasonable thresholds for early game
        early_game_thresholds = {
            "food": 80,   # Reduced from 150
            "wood": 60,   # Reduced from 100  
            "gold": 100   # Reduced from 150
        }
        
        # Vérifier s'il y a une pénurie en comparant avec des seuils plus raisonnables
        for resource in ["food", "wood", "gold"]:
            if getattr(resources, resource) < early_game_thresholds[resource]:
                print(f'Team {self.team.teamID} shortage detected: {resource} ({getattr(resources, resource)} < {early_game_thresholds[resource]})')
                self.last_detected_shortage = RESOURCE_MAPPING[resource]
                return self.last_detected_shortage
        
        print(f'Team {self.team.teamID}: No resource shortage detected')
        self.last_detected_shortage = None
        return None  # Aucune pénurie détectée



    def reallocate_villagers(self, Resource):
        available_villagers = [unit for unit in self.team.units
                               if isinstance(unit, Villager) and unit.isAvailable()]
        available_farms = [farm for farm in self.team.buildings
                           if isinstance(farm, Farm)]
        
        for villager in available_villagers:
            drop_points = [b for b in self.team.buildings if b.resourceDropPoint]
            if not drop_points:
                return False
            nearest_drop_point = min(
                drop_points,
                key=lambda dp: math.dist((villager.x, villager.y), (dp.x, dp.y))
            )

            if issubclass(Resource, Farm):
                if not available_farms:
                    # Try to build a farm near the drop point
                    closest_buildable_position = None
                    min_distance = float('inf')
                    nx, ny = int(nearest_drop_point.x), int(nearest_drop_point.y)
                    search_range = 10  # Adjust as needed

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
                        if self.team.build('Farm', x, y, 1, self.game_map):
                            print(f"Successfully built farm at ({x}, {y})")
                            return True
                        
                    # If that fails, try building in team zone
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
                            print(f"Successfully built farm at ({x}, {y})")
                            return True
                
                # Assign available villagers to existing farms
                if available_villagers and available_farms:
                    for villager in available_villagers:
                        closest_farm = min(
                            available_farms,
                            key=lambda farm: math.dist((villager.x, villager.y), (farm.x, farm.y))
                        )
                        villager.set_target(closest_farm)
                        print(f"Assigned villager to farm at ({closest_farm.x}, {closest_farm.y})")
                        break
                    return True

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
                print(f"Assigned villager to resource at {closest_resource[0]}")
                return True
        
        print(f"Team {self.team.teamID}: Failed to reallocate villagers")
        return False

    def priority7(self):
        resource_shortage = self.get_resource_shortage()
        
        if resource_shortage is None:
            # Even if no shortage, try to be proactive about villager training
            villager_count = sum(1 for unit in self.team.units if isinstance(unit, Villager))
            if villager_count < 5:  # Ensure minimum villagers
                print(f'Team {self.team.teamID}: No shortage but training villagers (current: {villager_count})')
                return self.train_units(Villager)
            print(f'Team {self.team.teamID}: No resource shortage detected, economy stable')
            return True  # Return True to indicate successful action
            
        print(f'Team {self.team.teamID}: Reallocating villagers to {resource_shortage.__name__}')
        result = self.reallocate_villagers(resource_shortage)
        
        # If reallocation fails, try to train more villagers
        if not result:
            print(f'Team {self.team.teamID}: Reallocation failed, trying to train villagers')
            return self.train_units(Villager)
            
        return result


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
            return create_offensive_decision_tree(self)
        elif self.mode == 'defensif':
            return create_defensive_decision_tree(self)
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

    def can_train_unit(self, unit_type):
        """Vérifie si on peut former une unité (ressources et bâtiment disponible)"""
        unit_instance = unit_type(team=self.team.teamID)
        if not self.team.resources.has_enough(unit_instance.cost.get()):
            return False, "resources"
            
        BUILDING_FOR_UNIT = {
            Villager: 'T',    # TownCentre
            Archer: 'A',      # ArcheryRange
            Swordsman: 'B',   # Barracks
            Horseman: 'S'     # Stable
        }
        
        required_building = BUILDING_FOR_UNIT.get(unit_type)
        has_building = any(b.acronym == required_building for b in self.team.buildings)
        
        return has_building, "building"

    def needs_population_buildings(self):
        """Vérifie si on a besoin d'augmenter la population maximum"""
        # Si proche de la limite de population
        if self.team.population >= self.team.maximum_population - 5:
            # Si on n'a pas atteint la limite absolue
            if self.team.maximum_population < MAXIMUM_POPULATION:
                return True
        return False

    def train_units(self, unit_type):
        can_train, reason = self.can_train_unit(unit_type)
        
        # Vérifier si on est proche de la limite de population
        if self.needs_population_buildings():
            # Priorité aux bâtiments qui augmentent la population
            for building_type in ["House", "TownCentre"]:
                if building_type in self.check_building_needs():
                    self.build_structure(1)
                    return False

        if not can_train:
            if reason == "resources":
                # Allouer des villageois à la récolte des ressources manquantes
                unit_instance = unit_type(team=self.team.teamID)
                if unit_instance.cost.wood > self.team.resources.wood:
                    self.reallocate_villagers(Tree)
                elif unit_instance.cost.gold > self.team.resources.gold:
                    self.reallocate_villagers(Gold)
                elif unit_instance.cost.food > self.team.resources.food:
                    self.reallocate_villagers(Farm)
            elif reason == "building":
                # Ajouter le bâtiment requis aux besoins
                UNIT_TO_BUILDING = {
                    Villager: "TownCentre",
                    Archer: "ArcheryRange",
                    Swordsman: "Barracks",
                    Horseman: "Stable"
                }
                needed_building = UNIT_TO_BUILDING.get(unit_type)
                if needed_building:
                    if needed_building not in self.check_building_needs():
                        self.build_structure(1)  # Construire le bâtiment nécessaire
            return False

        # Si on peut former l'unité, on la forme
        UNIT_TO_BUILDING_MAP = {
            Villager: 'T',
            Archer: 'A', 
            Swordsman: 'B',
            Horseman: 'S'
        }
        
        building_acronym = UNIT_TO_BUILDING_MAP.get(unit_type)
        if building_acronym:
            for building in self.team.buildings:
                if building.acronym == building_acronym:
                    if hasattr(building, 'add_to_training_queue'):
                        return building.add_to_training_queue(self.team)
        return False

    def balance_units(self):
        villager_count = sum(1 for unit in self.team.units if isinstance(unit, Villager))
        military_units = self.get_military_units()
        military_count = len(military_units)

        # Priorité à la formation de villageois si peu nombreux
        if villager_count < 20:
            success = self.train_units(Villager)
            if success:
                return True

        # Formation d'unités militaires si ressources suffisantes
        if military_count < 30:
            unit_priorities = [
                (self.PRIORITY_UNITS.get('a', 0), Archer),
                (self.PRIORITY_UNITS.get('s', 0), Swordsman),
                (self.PRIORITY_UNITS.get('h', 0), Horseman)
            ]
            
            # Trier par priorité
            unit_priorities.sort(reverse=True)
            
            # Essayer de former l'unité avec la plus haute priorité
            for priority, unit_type in unit_priorities:
                if self.train_units(unit_type):
                    return True

        return False

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

    def build_defensive_structure(self, building_type, num_builders):
        point = self.find_building_location(building_type)  # Fix: Changed from find_build_location to find_building_location
        if point:  # Add check for None return value
            x, y = point
            return self.team.build(building_type, x, y, num_builders, self.game_map)
        return False  # Return False if no suitable location found

    def gather_units_for_defense(self, units_per_target=2):
        """Rassemble les unités militaires pour défendre contre les ennemis détectés"""
        # Obtenir la liste des ennemis qui attaquent
        attacking_enemies = self.is_under_attack()
        if not attacking_enemies:
            return

        # Dictionary to track the number of units assigned to each target
        target_counts = {}
        
        # Récupérer uniquement les unités militaires disponibles
        available_units = [unit for unit in self.team.units 
                         if not isinstance(unit, Villager) 
                         and (not unit.attack_target or not unit.attack_target.isAlive())]

        # Assigner les unités aux cibles
        for unit in available_units:
            # Trouver la cible la plus proche qui n'a pas assez d'unités assignées
            closest_enemy = None
            min_distance = float('inf')
            
            for enemy in attacking_enemies:
                if enemy not in target_counts:
                    target_counts[enemy] = 0
                
                if target_counts[enemy] < units_per_target:
                    dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
                    if dist < min_distance:
                        min_distance = dist
                        closest_enemy = enemy
            
            if closest_enemy:
                unit.set_target(closest_enemy)
                target_counts[closest_enemy] = target_counts.get(closest_enemy, 0) + 1

    def defend_under_attack(self):
        #self.modify_target( None, players_target) # players_target is not used in defend_under_attack
        self.gather_units_for_defense()
        result = self.balance_units()
        result2 = self.build_defensive_structure("Keep", 3)
        return result or result2
        #self.manage_battle(self.team,None,enemy_team,self.game_map, dt) # players_target is None here

    def priorty1(self):
        print(f"Team {self.team.teamID}: Defending under attack")
        return self.defend_under_attack()

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
        
        # Ajouter des bâtiments militaires si on se prépare à l'expansion
        if self.is_ready_to_expand():
            if not any(isinstance(building, ArcheryRange) for building in self.team.buildings):
                needed_buildings.append("ArcheryRange")
            if not any(isinstance(building, Barracks) for building in self.team.buildings):
                needed_buildings.append("Barracks")
            if not any(isinstance(building, Keep) for building in self.team.buildings):
                needed_buildings.append("Keep")
        
        # Donner la priorité aux bâtiments de population si nécessaire
        if self.needs_population_buildings():
            if self.team.maximum_population < MAXIMUM_POPULATION - 10:
                if not any(isinstance(building, TownCentre) for building in self.team.buildings):
                    needed_buildings.append("TownCentre")
                if not any(isinstance(building, House) for building in self.team.buildings):
                    needed_buildings.append("House")
        
        # Ajouter les autres bâtiments nécessaires
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
        
        # Ajouter des maisons supplémentaires si besoin de population
        if self.needs_population_buildings() and "House" not in needed_buildings:
            needed_buildings.append("House")
            
        return needed_buildings

    def find_building_location(self, building_type):
        # Get the building size
        building_class = building_class_map[building_type]
        building_instance = building_class(team=self.team.teamID)
        building_size = building_instance.size
        del building_instance

        # Get list of coordinates in team's zone
        zone_coords = list(self.team.zone.get_zone())
        if not zone_coords:
            return None

        # Try 10 random positions
        for _ in range(10):
            # Pick a random position in the zone
            pos = choice(zone_coords)
            x, y = pos

            # Check if area is buildable
            if self.game_map.buildable_position(x, y, building_size):
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

    def build_structure(self, num_builders=1):
        needed_buildings = self.check_building_needs()
        if not needed_buildings:
            return False

        for building_type in needed_buildings:
            if building_type in building_class_map:
                print(f"Building type: {building_type}")
                building_class = building_class_map[building_type]

                # Créer une instance temporaire pour accéder à `cost`
                building_instance = building_class(team=self.team.teamID)
                building_cost = building_instance.cost

                print(f"Cout building: {building_cost}")

                # Accès aux ressources via les attributs de l'instance `cost`
                if (self.team.resources.food >= building_cost.food and
                    self.team.resources.wood >= building_cost.wood and
                    self.team.resources.gold >= building_cost.gold):

                    location = self.find_building_location(building_type)
                    if location:
                        x, y = location

                        # Vérifier que self.game_map est un objet de type GameMap
                        if not isinstance(self.game_map, GameMap):
                            print(f"Erreur: self.game_map n'est pas un objet GameMap. Type actuel: {type(self.game_map)}")
                            return False

                        # Construire le bâtiment
                        building = building_class(team=self.team.teamID, x=x, y=y)
                        if self.team.build(building_type, x, y, num_builders, self.game_map):  # Passez le nom du type de bâtiment ici
                            return True
        return False

    def is_ready_to_expand(self):
        """Vérifie si le bot est prêt à s'étendre"""
        # Vérifier qu'on a une économie stable
        if self.get_resource_shortage():
            return False
            
        # Vérifier qu'on a une armée suffisante
        military_count = self.get_military_unit_count(self.team)
        if military_count < 15:  # Minimum d'unités pour attaquer
            return False
            
        # Vérifier qu'on a des bâtiments de base
        has_essential_buildings = all(
            any(isinstance(b, building_type) for b in self.team.buildings)
            for building_type in [TownCentre, Keep, Barracks]
        )
        if not has_essential_buildings:
            return False
            
        return True

    def manage_expansion(self):
        """Gère l'expansion du territoire via l'attaque"""
        # Trouver l'ennemi le plus faible
        weakest_enemy = None
        min_military = float('inf')
        
        for enemy in self.enemies:
            enemy_military = self.get_military_unit_count(enemy)
            if enemy_military < min_military:
                min_military = enemy_military
                weakest_enemy = enemy
                
        if weakest_enemy:
            # Organiser les troupes pour l'attaque
            military_units = self.get_military_units()
            # Envoyer 70% des unités militaires à l'attaque
            attack_force = military_units[:int(len(military_units) * 0.7)]
            
            for unit in attack_force:
                # Chercher en priorité les bâtiments qui augmentent la population
                target = None
                for building in weakest_enemy.buildings:
                    if isinstance(building, (TownCentre, House)):
                        target = building
                        break
                        
                if not target:  # Si pas de bâtiment prioritaire, prendre n'importe quelle cible
                    self.search_for_target(unit, weakest_enemy, True)
                else:
                    unit.set_target(target)
            
            return True
        return False



