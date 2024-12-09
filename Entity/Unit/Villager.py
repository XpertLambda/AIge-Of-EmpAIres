from Entity.Unit import *  # Unit already imports Map
from Entity.Building import *  # Import all from Building

class Villager(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="v", 
            cost_food=50, 
            cost_gold=0, 
            cost_wood=25, 
            hp=40, 
            attack=0, 
            speed=1, 
            training_time=20, 
        )
        self.max_hp = self.hp  # ajout
        self.resources = 0
        self.carry_capacity = 20
        self.resource_rate = 25 / 60

    def isAvailable(self):
        if self.task != "nothing":
            print(f"{self.acronym} is currently busy with {self.task}.")
            return False
        return True

    def collectResource(self, resource_tile, duration, map):
        valid_resources = {'G': 'gold', 'W': 'wood', 'F': 'food'}
        if not self.isAvailable() or resource_tile.terrain_type not in valid_resources:
            return
        self.task = "collecting resources"
        self.SeDeplacer(resource_tile.x, resource_tile.y, map)  # Using the method from Unit
        total_collectable = min(self.resource_rate * duration, self.carry_capacity - self.resources)
        self.resources += total_collectable
        print(f"{self.acronym}: Collected {total_collectable:.2f} units of {valid_resources[resource_tile.terrain_type]}.")
        self.task = "nothing"

    def stockerRessources(self, building, map):
        if not self.isAvailable() or not building.resourceDropPoint:
            return
        self.task = "storing resources"
        self.SeDeplacer(building.x, building.y, map)  # Using the method from Unit
        print(f"{self.acronym}: Storing {self.resources} resources in {building.acronym}.")
        building.addResources(self.resources)
        self.resources = 0
        self.task = "nothing"

    def buildBatiment(self, building, x, y, map, num_villagers):
        if not self.isAvailable():
            return
        self.task = "building"
        self.SeDeplacer(x, y, map)  # Using the method from Unit
        if not map.can_place_building(map.grid, x, y, building):
            print(f"{self.acronym}: Cannot place {building.acronym} at ({x}, {y}).")
            self.task = "nothing"
            return
        time_needed = self.buildTime(building, num_villagers)
        if self.resources >= building.woodCost:
            self.resources -= building.woodCost
            print(f"{self.acronym}: Building {building.acronym} at ({x}, {y}). This will take {time_needed:.2f} seconds.")
            map.place_building(x, y, building)
        else:
            print(f"{self.acronym}: Not enough resources to build {building.acronym}.")
        self.task = "nothing"

    def buildTime(self, building, num_villagers):
        if num_villagers <= 0:
            return building.buildTime
        return max(10, (3 * building.buildTime) / (num_villagers + 2))
