import math
import time
from Models.Team import *
from Settings.setup import RESOURCE_THRESHOLDS, TILE_SIZE
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import Building, Keep, Barracks, TownCentre, Camp, House, Farm, Stable, ArcheryRange
from Entity.Building.Barracks import Barracks
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap
from Controller.terminal_display_debug import debug_print
from random import *
from AiUtils.aStar import a_star

class Bot:
    def __init__(self, player_team, game_map, clock, difficulty = 'medium'):
        self.clock= clock
        self.player_team = player_team
        self.game_map = game_map
        self.difficulty = difficulty
        self.PRIORITY_UNITS = {
            'a': 3,  # Archers
            's': 2,  # Swordsmen
            'h': 1   # Horsemen
        }
        self.ATTACK_RADIUS = TILE_SIZE * 5  # Rayon d'attaque pour détecter les ennemis

    def get_resource_shortage(self, current_resources, RESOURCE_THRESHOLDS=RESOURCE_THRESHOLDS):
        """
        Détermine quelle ressource est en pénurie.
        :param current_resources: Les ressources actuelles de l'équipe.
        :param RESOURCE_THRESHOLDS: Les seuils de ressources.
        :return: Le type de ressource en pénurie (food, wood, gold) ou None si tout va bien.
        """
        if current_resources.food < RESOURCE_THRESHOLDS['food']:
            return 'food'
        if current_resources.wood < RESOURCE_THRESHOLDS['wood']:
            return 'wood'
        if current_resources.gold < RESOURCE_THRESHOLDS['gold']:
            return 'gold'
        return None

    def find_resource_location(self, game_map, resource_acronym):
        """
        Trouve l'emplacement d'une ressource spécifique sur la carte.
        :param game_map: La carte du jeu.
        :param resource_acronym: L'acronyme de la ressource (par exemple, 'W' pour le bois).
        :return: Les coordonnées (x, y) de la ressource, ou None si non trouvée.
        """
        for (x, y), cell_content in game_map.grid.items():
            if resource_acronym in cell_content:
                return (x, y)
        return None

    def reallocate_villagers(self, resource_in_shortage, villagers, game_map):
        """
        Réaffecte les villageois disponibles pour collecter une ressource en pénurie.
        :param resource_in_shortage: Le type de ressource en pénurie (food, wood, gold).
        :param villagers: La liste des villageois de l'équipe.
        :param game_map: La carte du jeu.
        """
        for villager in villagers:
            if villager.isAvailable() and not villager.task:
                for x, y in game_map.grid:
                    resource_nodes = game_map.grid[(x, y)]
                    for resource_node in resource_nodes:
                        if resource_node.acronym.lower() == resource_in_shortage[0].lower():
                            villager.set_target(resource_node)
                            return

    def check_and_address_resources(self, team, game_map, thresholds):
        """
        Vérifie les ressources et réaffecte les villageois si nécessaire.
        :param team: L'équipe du joueur.
        :param game_map: La carte du jeu.
        :param thresholds: Les seuils de ressources.
        """
        resource_shortage = self.get_resource_shortage(team.resources, thresholds)
        if resource_shortage:
            self.reallocate_villagers(resource_shortage, team.units, game_map)

    def search_for_target(self, unit, enemy_team, attack_mode=True):
        """
        Searches for the closest enemy unit or building depending on the mode.
        vise en premier les keeps puis les units puis les villagers et buildings
        """
        if enemy_team == None:
            return
        closest_distance = float("inf")
        closest_entity = None
        keeps = [keep for keep in enemy_team.buildings if isinstance(keep, Keep)]
        targets = [unit for unit in enemy_team.units if not isinstance(unit, Villager)]

        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if dist < closest_distance:
                closest_distance = dist
                closest_entity = enemy
        if attack_mode and closest_entity == None:
            targets = [unit for unit in enemy_team.units if isinstance(unit, Villager)]
            for enemy in targets:
                dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
                if attack_mode or not isinstance(enemy, Villager):
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
                if attack_mode or not isinstance(enemy, Villager):
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_entity = enemy
        if closest_entity != None:
            if keeps != [] and attack_mode:
                for keep in keeps:
                    dist = math.dist((keep.x, keep.y), (closest_entity.x, closest_entity.y))
                    if dist < keep.attack_range:
                        closest_entity = keep

        unit.set_target(closest_entity)
        return unit.attack_target is not None

    def priority_2(self, players, selected_player, players_target):
        """
        Lance l'attaque en essayant de choisir une cible.
        Si elle réussit, vise en premier les keeps ou les units.
        """
        if players_target[selected_player.teamID] != None:
            # Attaque déjà en cours
            return False
        return self.choose_target(players, selected_player, players_target)

    def modify_target(self, player, target, players_target):
        """
        Met à jour la cible de l'équipe (arrête toutes les attaques de la team)
        pour la remplacer par la nouvelle 'target'.
        """
        players_target[player.teamID] = target
        for unit in player.units:
            unit.set_target(None)

    def choose_target(self, players, selected_player, players_target):
        """
        Choisit une cible pour l'attaque en fonction du nombre d'unités et de bâtiments ennemis.
        """
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

    def manage_battle(self, selected_player, players_target, players, game_map, dt):
        """
        Réassigne une target à chaque unité d'un player lorsqu'il n'en a plus lors d'un combat attaque ou défense.
        Arrête les combats si nécessaire.
        """
        enemy = players_target[selected_player.teamID]
        attack_mode = True
        # Defense
        # if any([is_under_attack(selected_player, enemy_team) for enemy_team in players]):
        if True:
            # On cherche la team qui est en train de nous attaquer si les frontières ont été violées
            for i in range(0, len(players_target)):
                if players_target[i] == selected_player:
                    for team in players:
                        if team.teamID == i:
                            players_target[selected_player.teamID] = None
                            enemy = team
                            attack_mode = False
        if enemy != None and (len(enemy.units) != 0 or len(enemy.buildings) != 0):
            for unit in selected_player.units:
                if not isinstance(unit, Villager) or (len(selected_player.units) == 0 and not attack_mode):
                    if unit.attack_target == None or not unit.attack_target.isAlive():
                        self.search_for_target(unit, enemy, attack_mode)
        else:
            self.modify_target(selected_player, None, players_target)
        if self.get_military_unit_count(selected_player) == 0:
            self.modify_target(selected_player, None, players_target)

    def get_military_unit_count(self, player):
        """
        Retourne le nombre d'unités militaires disponibles pour un joueur.
        """
        return len(self.get_military_units(player))
    
    def update(self, game_map, dt):
        debug_print("Updating bot...")
        enemy_teams = [team for team in game_map.players if team.teamID != self.player_team.teamID]

        # Log des ressources et des unités
        debug_print(f"Resources: {self.player_team.resources}")
        debug_print(f"Villagers: {sum(1 for unit in self.player_team.units if isinstance(unit, Villager))}")
        debug_print(f"Military units: {len(self.get_military_units())}")

        # Appliquer la stratégie en fonction de la difficulté
        if self.difficulty == 'easy':
            self.easy_strategy(enemy_teams, game_map, dt)
        elif self.difficulty == 'medium':
            self.medium_strategy(enemy_teams, game_map, dt)
        elif self.difficulty == 'hard':
            self.hard_strategy(enemy_teams, game_map, dt)

        # Scouter la carte pour trouver des ressources ou des ennemis
        self.scout_map(game_map)

        # Vérifier et gérer les ressources
        self.check_and_address_resources(self.player_team, game_map, RESOURCE_THRESHOLDS)

        # Équilibrer les unités
        self.balance_units()

        # Construire des structures si nécessaire
        self.build_structure(self.clock)
    def scout_map(self, game_map):
        """
        Explore la carte pour localiser les ressources et les unités ennemies.
        :param game_map: La carte du jeu.
        """
        # Trouver la position du TownCentre
        town_centre = next((building for building in self.player_team.buildings if isinstance(building, TownCentre)), None)
        if not town_centre:
            debug_print("No TownCentre found. Cannot scout map.")
            return

        # Convertir les coordonnées en entiers
        base_x, base_y = int(town_centre.x), int(town_centre.y)

        # Définir une zone à explorer (par exemple, un carré de 10x10 tuiles autour de la base)
        scout_radius = 10
        scout_area = [(x, y) for x in range(base_x - scout_radius, base_x + scout_radius)
                    for y in range(base_y - scout_radius, base_y + scout_radius)]

        # Parcourir la zone pour trouver des ressources ou des ennemis
        for (x, y) in scout_area:
            # Vérifier si la tuile contient des ressources en utilisant le dictionnaire resources
            resources_at_tile = game_map.resources.get((x, y))  # Accéder aux ressources à la position (x, y)

            if resources_at_tile:
                for resource in resources_at_tile:
                    # Utiliser le nom de la classe comme type de ressource
                    resource_type = resource.__class__.__name__.lower()  # "Gold" -> "gold", "Wood" -> "wood"
                    debug_print(f"Found {resource_type} at ({x}, {y}).")
                    if resource_type == "wood":
                        self.reallocate_villagers('wood', [unit for unit in self.player_team.units if isinstance(unit, Villager)], game_map)
                    elif resource_type == "gold":
                        self.reallocate_villagers('gold', [unit for unit in self.player_team.units if isinstance(unit, Villager)], game_map)

            # Vérifier si la tuile contient des unités ennemies
            for enemy_team in game_map.players:
                if enemy_team.teamID != self.player_team.teamID:
                    for enemy in enemy_team.units:
                        if enemy.x == x and enemy.y == y:
                            debug_print(f"Found enemy {enemy.__class__.__name__} at ({x}, {y}).")
                            # Adapter la stratégie en fonction des unités ennemies trouvées
                            if isinstance(enemy, Horseman):
                                self.PRIORITY_UNITS['archer'] = 4  # Augmenter la priorité des archers
                            elif isinstance(enemy, Archer):
                                self.PRIORITY_UNITS['swordsman'] = 3  # Augmenter la priorité des épéistes

        # Si des ressources ou des ennemis sont trouvés, ajuster la stratégie
        if self.player_team.resources.wood < 100:
            debug_print("Low on wood. Prioritizing wood collection.")
            self.balance_units()
        if self.player_team.resources.gold < 50:
            debug_print("Low on gold. Prioritizing gold collection.")
            self.balance_units()

    def easy_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            # Collecte des ressources de manière aléatoire
            if random.random() < 0.5:
                self.balance_units()

            # Construit des bâtiments de manière aléatoire
            if random.random() < 0.3:
                self.build_structure()

            # Réagit aux attaques ennemies
            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                self.gather_units_for_defense(critical_points, enemy_team, game_map, dt)

    def medium_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            # Gestion des ressources et des unités
            self.balance_units()
            self.adjust_priorities(enemy_team)

            # Construction de bâtiments en fonction des besoins
            if self.check_building_needs():
                self.build_structure(self.clock)

            # Construit des tours défensives près des points critiques
            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                if critical_points and self.can_build_building(Keep):
                    critical_location = (critical_points[0].x, critical_points[0].y)
                    self.build_defensive_structure(Keep, critical_location, 3, game_map)

            # Attaque avec une composition d'unités équilibrée
            if len(self.get_military_units()) > 10:
                self.manage_battle(enemy_team, game_map, dt)

    def hard_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            # Gestion optimisée des ressources et des unités
            self.balance_units()
            self.adjust_priorities(enemy_team)

            # Construction de bâtiments stratégiques
            if self.check_building_needs():
                self.build_structure(self.clock)

            # Scoute la carte pour trouver des ressources ou des unités ennemies
            self.scout_map(game_map)

            # Attaque avec une composition d'unités adaptée
            if len(self.get_military_units()) > 15:
                attack_composition = self.choose_attack_composition()
                for unit in attack_composition:
                    if unit.idle:
                        target = self.find_target_for_unit(unit)
                        if target:
                            unit.set_target(target)

            # Défense proactive
            if self.is_under_attack(enemy_team):
                self.defend_under_attack(enemy_team, game_map, dt)
    def get_military_units(self):
        """
        Retourne une liste des unités militaires (non villageois) de l'équipe.
        """
        return [unit for unit in self.player_team.units if not isinstance(unit, Villager)]

    def train_units(self, unit_type):
        """
        Entraîne une unité en sélectionnant automatiquement le bon bâtiment.
        :param unit_type: Le type d'unité à entraîner (par exemple, Villager, Archer, etc.).
        """
        # Dictionnaire qui associe chaque type d'unité à son bâtiment correspondant
        UNIT_TO_BUILDING_MAP = {
            'v': 'TownCentre',  # Villageois
            'a': 'ArcheryRange',  # Archer
            's': 'Barracks',  # Swordsman
            'h': 'Stable'  # Horseman
        }

        # Récupérer l'acronyme de l'unité (par exemple, 'v' pour Villager)
        unit_acronym = unit_type.acronym if hasattr(unit_type, 'acronym') else None

        if unit_acronym and unit_acronym in UNIT_TO_BUILDING_MAP:
            # Récupérer le type de bâtiment correspondant
            building_type = UNIT_TO_BUILDING_MAP[unit_acronym]

            # Trouver le premier bâtiment correspondant dans l'équipe du joueur
            for building in self.player_team.buildings:
                if building.acronym == building_type[0]:  # On compare avec le premier caractère de l'acronyme
                    if hasattr(building, 'add_to_training_queue'):
                        # Entraîner l'unité dans ce bâtiment
                        success = building.add_to_training_queue(self.player_team)
                        if success:
                            debug_print(f"Added {unit_type.__name__} to training queue in {building.acronym}.")
                        else:
                            debug_print(f"Failed to add {unit_type.__name__} to training queue in {building.acronym}.")
                        return
            debug_print(f"No available {building_type} found to train {unit_type.__name__}.")
        else:
            debug_print(f"No building mapping found for unit type: {unit_type.__name__}.")


    def easy_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            # Collecte des ressources de manière aléatoire
            if random.random() < 0.5:
                self.balance_units()

            # Construit des bâtiments de manière aléatoire
            if random.random() < 0.3:
                self.build_structure()

            # Réagit aux attaques ennemies
            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                self.gather_units_for_defense(critical_points, enemy_team, game_map, dt)

    def medium_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            # Gestion des ressources et des unités
            self.balance_units()
            self.adjust_priorities(enemy_team)

            # Construction de bâtiments en fonction des besoins
            if self.check_building_needs():
                self.build_structure(self.clock)

            # Construit des tours défensives près des points critiques
            if self.is_under_attack(enemy_team):
                critical_points = self.get_critical_points()
                if critical_points and self.can_build_building(Keep):
                    critical_location = (critical_points[0].x, critical_points[0].y)
                    self.build_defensive_structure(Keep, critical_location, 3, game_map)

            # Attaque avec une composition d'unités équilibrée
            if len(self.get_military_units()) > 10:
                self.manage_battle(enemy_team, game_map, dt)

    def hard_strategy(self, enemy_teams, game_map, dt):
        for enemy_team in enemy_teams:
            # Gestion optimisée des ressources et des unités
            self.balance_units()
            self.adjust_priorities(enemy_team)

            # Construction de bâtiments stratégiques
            if self.check_building_needs():
                self.build_structure(self.clock)

            # Scoute la carte pour trouver des ressources ou des unités ennemies
            self.scout_map(game_map)

            # Attaque avec une composition d'unités adaptée
            if len(self.get_military_units()) > 15:
                attack_composition = self.choose_attack_composition()
                for unit in attack_composition:
                    if unit.idle:
                        target = self.find_target_for_unit(unit)
                        if target:
                            unit.set_target(target)

            # Défense proactive
            if self.is_under_attack(enemy_team):
                self.defend_under_attack(enemy_team, game_map, dt)
    def get_military_units(self):
        """
        Retourne une liste des unités militaires (non villageois) de l'équipe.
        """
        return [unit for unit in self.player_team.units if not isinstance(unit, Villager)]

    def train_units(self, unit_type):
        """
        Entraîne une unité en sélectionnant automatiquement le bon bâtiment.
        :param unit_type: Le type d'unité à entraîner (par exemple, Villager, Archer, etc.).
        """
        # Dictionnaire qui associe chaque type d'unité à son bâtiment correspondant
        UNIT_TO_BUILDING_MAP = {
            'v': 'TownCentre',  # Villageois
            'a': 'ArcheryRange',  # Archer
            's': 'Barracks',  # Swordsman
            'h': 'Stable'  # Horseman
        }

        # Récupérer l'acronyme de l'unité (par exemple, 'v' pour Villager)
        unit_acronym = unit_type.acronym if hasattr(unit_type, 'acronym') else None

        if unit_acronym and unit_acronym in UNIT_TO_BUILDING_MAP:
            # Récupérer le type de bâtiment correspondant
            building_type = UNIT_TO_BUILDING_MAP[unit_acronym]

            # Trouver le premier bâtiment correspondant dans l'équipe du joueur
            for building in self.player_team.buildings:
                if building.acronym == building_type[0]:  # On compare avec le premier caractère de l'acronyme
                    if hasattr(building, 'add_to_training_queue'):
                        # Entraîner l'unité dans ce bâtiment
                        success = building.add_to_training_queue(self.player_team)
                        if success:
                            debug_print(f"Added {unit_type.__name__} to training queue in {building.acronym}.")
                        else:
                            debug_print(f"Failed to add {unit_type.__name__} to training queue in {building.acronym}.")
                        return
            debug_print(f"No available {building_type} found to train {unit_type.__name__}.")
        else:
            debug_print(f"No building mapping found for unit type: {unit_type.__name__}.")

    def is_under_attack(self, enemy_team):
        """
        Vérifie si l'équipe du joueur est sous attaque.
        :param enemy_team: L'équipe ennemie.
        :return: True si sous attaque, False sinon.
        """
        for building in self.player_team.buildings:
            if building.hp < building.max_hp:  # Bâtiment endommagé
                return True
            for enemy in enemy_team.units:
                if not isinstance(enemy, Villager):
                    if math.dist((building.x, building.y), (enemy.x, enemy.y)) < self.ATTACK_RADIUS:
                        return True
        return False
    
    def get_critical_points(self):
       
       
        if not self.player_team.buildings:
            return []
        critical_points = [building for building in self.player_team.buildings if building.hp / building.max_hp < 0.3]
        critical_points.sort(key=lambda b: b.hp / b.max_hp)
        return critical_points
    
    def build_defensive_structure(self, building_type,  num_builders):
     critical_points= self.get_critical_points()
     if critical_points:
        for point in critical_points:
             self.player_team.build(building_type, point.x, point.y ,num_builders,self.game_map)
   
    
    def gather_units_for_defense(self,  enemy_team):
     critical_points = self.get_critical_points()
     for point in critical_points:
        for unit in self.units:
            if not hasattr(unit, 'carry') and not unit.target:
                target = self.search_for_target(unit, enemy_team, attack_mode=False)
                if target:
                    unit.set_target(target)
                else:
                    unit.set_destination((point.x, point.y))
    
    def defend_under_attack(self, enemy_team, players_target,  dt):
     if self.is_under_attack( enemy_team):
        critical_points = sorted(self.get_damaged_buildings(critical_threshold=0.7))
        self.modify_target( None, players_target)
        self.gather_units_for_defense(  enemy_team)
        
        self.balance_units()
        
        self.build_defensive_structure( "Keep", 3)
        self.manage_battle(self.player_team,None,enemy_team,self.game_map,dt)
    
    def manage_battle(self, enemy_team, game_map, dt):
       
        if self.is_under_attack(enemy_team):
            self.defend_under_attack(enemy_team, game_map, dt)
    
    def search_for_target(self, unit, enemy_team, attack_mode=True):
        """
        Recherche une cible pour une unité donnée.
        :param unit: L'unité qui cherche une cible.
        :param enemy_team: L'équipe ennemie.
        :param attack_mode: True pour attaquer, False pour défendre.
        :return: True si une cible est trouvée, False sinon.
        """
        for enemy in enemy_team.units:
            if not isinstance(enemy, Villager):
                if math.dist((unit.x, unit.y), (enemy.x, enemy.y)) < self.ATTACK_RADIUS:
                    unit.set_target(enemy)
                    return True
        return False
    
    def balance_units(self):
        """
        Équilibre les unités en entraînant des villageois ou des unités militaires selon les besoins.
        """
        # Nombre de villageois et d'unités militaires
        villager_count = sum(1 for unit in self.player_team.units if isinstance(unit, Villager))
        military_units = self.get_military_units()
        military_count = len(military_units)

        # Constantes pour la gestion des files d'attente et des priorités
        MAX_QUEUE_SIZE = 5  # Taille maximale de la file d'attente pour un bâtiment
        PRIORITY_UNITS = {
            'a': 3,  # Priorité élevée pour les archers
            's': 2,  # Priorité moyenne pour les épéistes
            'h': 1   # Priorité faible pour les cavaliers
        }

        # Priorité 1 : Entraîner des villageois si nécessaire
        if self.player_team.resources.food < 100 and villager_count < 10:
            for building in self.player_team.buildings:
                if building.acronym == 'T':  # TownCentre entraîne des villageois
                    if len(building.training_queue) < MAX_QUEUE_SIZE:
                        self.train_units(Villager)
                        debug_print(f"Added Villager to training queue in {building.acronym}.")
                        break  # On entraîne un seul villageois à la fois

        # Priorité 2 : Entraîner des unités militaires si nécessaire
        elif military_count < 20:
            # Trouver le bâtiment avec la priorité la plus élevée pour entraîner une unité
            best_building = None
            best_priority = -1
            for building in self.player_team.buildings:
                if building.spawnsUnits and len(building.training_queue) < MAX_QUEUE_SIZE:
                    # Déterminer la priorité de ce bâtiment
                    unit_acronym = building.acronym
                    if unit_acronym in PRIORITY_UNITS:
                        priority = PRIORITY_UNITS[unit_acronym]
                        if priority > best_priority:
                            best_building = building
                            best_priority = priority

            if best_building:
                unit_type = Building.UNIT_TRAINING_MAP.get(best_building.acronym)
                if unit_type:
                    self.train_units(best_building, unit_type)
                    debug_print(f"Added {unit_type} to training queue in {best_building.acronym}.")

    def adjust_priorities(self, enemy_teams):
        """
        Ajuste les priorités des unités en fonction des unités ennemies.
        :param enemy_teams: Une équipe ennemie ou une liste d'équipes ennemies.
        """
        # Si enemy_teams n'est pas une liste, on le transforme en liste
        if not isinstance(enemy_teams, list):
            enemy_teams = [enemy_teams]

        # Initialiser les compteurs pour les unités ennemies
        enemy_horsemen = 0
        enemy_archers = 0
        enemy_swordsmen = 0

        # Parcourir chaque équipe ennemie
        for enemy_team in enemy_teams:
            # Compter les unités ennemies pour chaque type
            enemy_horsemen += sum(1 for unit in enemy_team.units if isinstance(unit, Horseman))
            enemy_archers += sum(1 for unit in enemy_team.units if isinstance(unit, Archer))
            enemy_swordsmen += sum(1 for unit in enemy_team.units if isinstance(unit, Swordsman))

        # Seuils configurables pour ajuster les priorités
        HORSEMEN_THRESHOLD = 5  # Nombre de cavaliers ennemis pour augmenter la priorité des archers
        ARCHERS_THRESHOLD = 7   # Nombre d'archers ennemis pour augmenter la priorité des épéistes
        SWORDSMEN_THRESHOLD = 6 # Nombre d'épéistes ennemis pour augmenter la priorité des cavaliers

        # Ajuster les priorités en fonction des unités ennemies
        if enemy_horsemen > HORSEMEN_THRESHOLD:
            self.PRIORITY_UNITS['a'] = 4  # Augmenter la priorité des archers
            debug_print(f"Enemy has many horsemen ({enemy_horsemen}). Increasing archer priority.")

        if enemy_archers > ARCHERS_THRESHOLD:
            self.PRIORITY_UNITS['s'] = 3  # Augmenter la priorité des épéistes
            debug_print(f"Enemy has many archers ({enemy_archers}). Increasing swordsman priority.")

        if enemy_swordsmen > SWORDSMEN_THRESHOLD:
            self.PRIORITY_UNITS['h'] = 2  # Augmenter la priorité des cavaliers
            debug_print(f"Enemy has many swordsmen ({enemy_swordsmen}). Increasing horseman priority.")
    
    def choose_attack_composition(self):
        """
        Choisit une composition d'attaque optimale en fonction des unités disponibles.
        :return: Une liste d'unités sélectionnées pour l'attaque.
        """
        # Définir la composition souhaitée (type d'unité : nombre souhaité)
        units_by_type = {
            Archer: 3,    # 3 archers
            Swordsman: 1, # 1 épéiste
            Horseman: 1   # 1 cavalier
        }

        selected_units = []  # Liste pour stocker les unités sélectionnées

        # Parcourir chaque type d'unité et sélectionner les unités disponibles
        for unit_type, limit in units_by_type.items():
            # Filtrer les unités disponibles du type actuel
            available_units = [unit for unit in self.player_team.units if isinstance(unit, unit_type)]
            
            # Ajouter jusqu'à `limit` unités à la liste sélectionnée
            selected_units.extend(available_units[:limit])

            # Si on a atteint le nombre total d'unités souhaité, on arrête
            if len(selected_units) >= sum(units_by_type.values()):
                break

        return selected_units
    
    def maintain_army(self):
        """
        Gère l'armée en équilibrant les unités et en lançant des attaques.
        """
        military_count = len(self.get_military_units())

        # Si l'armée est trop petite, on équilibre les unités
        if military_count < 20:
            self.balance_units()
        else:
            # Sinon, on choisit une composition d'attaque
            attack_composition = self.choose_attack_composition()

            # Pour chaque unité dans la composition d'attaque
            for unit in attack_composition:
                if not isinstance(unit, Villager):  # On ignore les villageois
                    if unit.idle:
                        # Trouver une cible pour l'unité (supposons que cette logique est déjà implémentée ailleurs)
                        target = self.find_target_for_unit(unit)
                        if target:
                            unit.set_target(target)  # Définir la cible de l'unité
                            debug_print(f"Unit {unit.__class__.__name__} targeting {target.__class__.__name__}.")
                    elif unit.target:
                        # Si l'unité a déjà une cible, on lui ordonne d'attaquer
                        unit.attack()
                    else:
                        # Si aucune cible n'est trouvée, on met l'unité en état idle
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
        for x in range(10, self.game_map.width - 10):
            for y in range(10, self.game_map.height - 10):
                if self.game_map.is_tile_empty(x, y):
                    enemy_nearby = False
                    for enemy_team in self.game_map.teams:
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

    def build_structure(self, clock):
        needed_buildings = self.check_building_needs()
        if not needed_buildings:
            debug_print("No buildings needed.")
            return False
        for building_type in needed_buildings:
            if building_type in building_class_map:
                building_class = building_class_map[building_type]
                if not hasattr(building_class, 'cost'):
                    debug_print(f"Building class {building_type} has no attribute 'cost'.")
                    continue
                building_cost = building_class.cost
                if (self.player_team.resources["wood"] >= building_cost.wood and
                    self.player_team.resources["gold"] >= building_cost.gold and
                    self.player_team.resources["food"] >= building_cost.food):
                    location = self.find_building_location(building_type)
                    if location:
                        x, y = location
                        building = building_class(team=self.player_team.teamID, x=x, y=y)
                        if self.player_team.buildBuilding(building, clock, nb=3, game_map=self.game_map):
                            debug_print(f"Started building {building_type} at ({x}, {y}).")
                            return True
        return False