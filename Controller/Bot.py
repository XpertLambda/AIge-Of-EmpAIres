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

    def get_military_unit_count(self):
        return sum(1 for unit in self.player_team.units if not isinstance(unit, Villager))

    def train_units(self, unit_type):
        for building in self.player_team.buildings:
            if hasattr(building, 'add_to_training_queue'):
                building.add_to_training_queue(unit_type)

    def balance_units(self):
        """
        Vérifie pour chaque bâtiment si une unité peut être entraînée.
        Si c'est le cas, entraîne une unité de ce bâtiment.
        Gère les files d'attente pleines, priorise les unités et vérifie les ressources.
        """
        # Nombre de villageois et d'unités militaires
        villager_count = sum(1 for unit in self.player_team.units if isinstance(unit, Villager))
        military_count = self.get_military_unit_count()

        # Constantes pour la gestion des files d'attente et des priorités
        MAX_QUEUE_SIZE = 5  # Taille maximale de la file d'attente pour un bâtiment
        PRIORITY_UNITS = {
            'archer': 3,    # Priorité élevée pour les archers
            'swordsman': 2, # Priorité moyenne pour les épéistes
            'horseman': 1   # Priorité faible pour les cavaliers
        }

        # Priorité 1 : Entraîner des villageois si nécessaire
        if self.player_team.resources.food < 100 and villager_count < 10:
            for building in self.player_team.buildings:
                if building.acronym == 'T':  # TownCentre entraîne des villageois
                    if len(building.training_queue) < MAX_QUEUE_SIZE:  # Vérifie si la file d'attente n'est pas pleine
                        if building.add_to_training_queue(self.player_team):
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
                    unit_name = UNIT_TRAINING_MAP.get(building.acronym, None)
                    if unit_name and unit_name in PRIORITY_UNITS:
                        priority = PRIORITY_UNITS[unit_name]
                        if priority > best_priority:
                            best_building = building
                            best_priority = priority
            if best_building:
                if best_building.add_to_training_queue(self.player_team):
                    debug_print(f"Added {UNIT_TRAINING_MAP[best_building.acronym]} to training queue in {best_building.acronym}.")

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
        archers = [unit for unit in self.player_team.units if isinstance(unit, Archer)]
        swordsmen = [unit for unit in self.player_team.units if isinstance(unit, Swordsman)]
        horsemen = [unit for unit in self.player_team.units if isinstance(unit, Horseman)]

        if len(archers) >= 3 and len(swordsmen) >= 1 and len(horsemen) >= 1:
            return archers[:3] + swordsmen[:1] + horsemen[:1]
        elif len(archers) >= 3 and len(swordsmen) >= 1:
            return archers[:3] + swordsmen[:1]
        elif len(archers) >= 3:
            return archers[:3]
        elif len(swordsmen) >= 1:
            return swordsmen[:1]
        elif len(horsemen) >= 1:
            return horsemen[:1]
        else:
            return []

    def maintain_army(self):
        military_count = self.get_military_unit_count()
        if military_count < 20:
            self.balance_units()
        else:
            attack_composition = self.choose_attack_composition()
            for unit in attack_composition:
                if not isinstance(unit, Villager):
                    if unit.idle:
                        unit.seek_attack()
                    elif unit.target:
                        unit.kill()
                    else:
                        unit.setIdle()

    def get_resource_shortage(self, thresholds=RESOURCE_THRESHOLDS):
        if self.player_team.resources["food"] < thresholds['food']:
            return 'food'
        if self.player_team.resources["wood"] < thresholds['wood']:
            return 'wood'
        if self.player_team.resources["gold"] < thresholds['gold']:
            return 'gold'
        return None

    def find_resource_location(self, resource_acronym):
        for (x, y), cell_content in self.game_map.grid.items():
            if resource_acronym in cell_content:
                return (x, y)

    def reallocate_villagers(self, resource_in_shortage):
        for villager in self.player_team.units:
            if isinstance(villager, Villager) and villager.isAvailable() and not villager.task:
                resource_location = self.find_resource_location(resource_in_shortage)
                if resource_location:
                    villager.set_target(resource_location)
                    return

    def check_and_address_resources(self, thresholds=RESOURCE_THRESHOLDS):
        resource_shortage = self.get_resource_shortage(thresholds)
        if resource_shortage:
            self.reallocate_villagers(resource_shortage)

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