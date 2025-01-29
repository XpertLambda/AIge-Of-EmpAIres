from collections import Counter
from Settings.setup import *
from Settings.entity_mapping import *
from Entity.Entity import *
from Entity.Building import *
from Entity.Unit import *
from Entity.Resource import Resource
from Models.Map import GameMap
from Models.Zone import Zone
from Controller.terminal_display_debug import debug_print

class Team:
    def __init__(self, difficulty, teamID):
        self.resources = difficulty_config[difficulty]['Resources'].copy()

        self.zone = Zone()

        self.units = set()
        self.buildings = set()
        self.teamID = teamID

        self.population = 0
        self.maximum_population = 0
        self.en_cours = {}



        for building, amount in difficulty_config[difficulty]['Buildings'].items():
            for _ in range(amount):
                if building in building_class_map:
                    building_instance = building_class_map[building](team=teamID)
                    building_instance.processTime = building_instance.buildTime
                    self.add_member(building_instance)

        for unit, amount in difficulty_config[difficulty]['Units'].items():
            for _ in range(amount):
                if unit in unit_class_map:
                    unit_instance = unit_class_map[unit](team=teamID)
                    self.add_member(unit_instance)

    def add_member(self, entity):
        if entity.team == self.teamID :
            if entity in self.buildings or entity in self.units:
                return False

            if isinstance(entity, Building):
                if entity.population + self.maximum_population > MAXIMUM_POPULATION :
                    debug_print("Maximum population reached")
                    return False

                self.buildings.add(entity)
                self.maximum_population += entity.population
                return True

            elif isinstance(entity, Unit):
                if self.population + 1 > self.maximum_population:
                    debug_print("Failed to add entity : Not enough space")
                    return False

                self.units.add(entity)
                self.population += 1
                return True
        return False

    def remove_member(self, entity):
        if entity.team == self.teamID:
            if isinstance(entity, Building):
                if entity in self.buildings:
                    self.buildings.remove(entity)
                    self.maximum_population -= entity.population
                    return True
            elif isinstance(entity, Unit):
                if entity in self.units:
                    self.units.remove(entity)
                    self.population -= 1
                    return True
        return False

    def build(self, building_type, x, y, num_builders, game_map, force=False):
        # Add safety check for team ID
        if self.teamID >= len(game_map.players):
            print(f"Warning: Invalid team ID {self.teamID} for {len(game_map.players)} players")
            return False

        building_class = building_class_map[building_type]
        building = building_class(team=self.teamID)

        x, y = round(x), round(y)
        if not self.resources.has_enough(building.cost.get()):
            del building
            return False

        builders = set()
        for unit in self.units:
            if unit.acronym == "v" and (force or unit.isAvailable()):
                builders.add(unit)
                if len(builders) == num_builders:
                    break
        if not builders:
            del building
            return False

        for i in range(building.size):
            for j in range(building.size):
                pos = (x + i, y + j)
                if pos in game_map.grid:
                    del building
                    return False

        if not game_map.add_entity(building, x, y):
            del building
            return False

        self.resources.decrease_resources(building.cost.get())

        for villager in builders:
            villager.set_task('build', building)

        building.set_builders(builders)

        return True
