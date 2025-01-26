from Models.Team import *
from Settings.setup import RESOURCE_THRESHOLDS
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import Building
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap
from Controller.terminal_display_debug import debug_print

class Bot:
    def __init__(self, player_team, game_map):
        self.player_team = player_team
        self.game_map = game_map

    def get_military_units(self):
        """
        Retourne une liste des unités militaires (non villageois) de l'équipe.
        """
        return [unit for unit in self.player_team.units if not isinstance(unit, Villager)]

    def train_units(self, building, unit_type):
        """
        Entraîne une unité dans un bâtiment spécifique.
        :param building: Le bâtiment qui entraîne l'unité.
        :param unit_type: Le type d'unité à entraîner.
        """
        if hasattr(building, 'add_to_training_queue'):
            building.add_to_training_queue(unit_type)

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
                        self.train_units(building, Villager)
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

    def adjust_priorities(self, enemy_team):
        """
        Ajuste les priorités des unités en fonction des unités ennemies.
        """
        # Compter les unités ennemies
        enemy_horsemen = sum(1 for unit in enemy_team.units if isinstance(unit, Horseman))
        enemy_archers = sum(1 for unit in enemy_team.units if isinstance(unit, Archer))
        enemy_swordsmen = sum(1 for unit in enemy_team.units if isinstance(unit, Swordsman))

        # Seuils configurables pour ajuster les priorités
        HORSEMEN_THRESHOLD = 5  # Nombre de cavaliers ennemis pour augmenter la priorité des archers
        ARCHERS_THRESHOLD = 7   # Nombre d'archers ennemis pour augmenter la priorité des épéistes
        SWORDSMEN_THRESHOLD = 6 # Nombre d'épéistes ennemis pour augmenter la priorité des cavaliers

        # Ajuster les priorités en fonction des unités ennemies
        if enemy_horsemen > HORSEMEN_THRESHOLD:
            self.PRIORITY_UNITS['archer'] = 4  # Augmenter la priorité des archers
            debug_print(f"Enemy has many horsemen ({enemy_horsemen}). Increasing archer priority.")

        if enemy_archers > ARCHERS_THRESHOLD:
            self.PRIORITY_UNITS['swordsman'] = 3  # Augmenter la priorité des épéistes
            debug_print(f"Enemy has many archers ({enemy_archers}). Increasing swordsman priority.")

        if enemy_swordsmen > SWORDSMEN_THRESHOLD:
            self.PRIORITY_UNITS['horseman'] = 2  # Augmenter la priorité des cavaliers
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