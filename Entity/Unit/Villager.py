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
        if self.task:
            print(f"{self.acronym} is currently busy.")
            return False
        return True

    def collectResource(self, resource_tile, duration, map):
        valid_resources = {'G': 'gold', 'W': 'wood', 'F': 'food'}
        if not self.isAvailable() or resource_tile.terrain_type not in valid_resources:
            return
        self.task = True
        self.SeDeplacer(resource_tile.x, resource_tile.y, map)
        self.resources += min(self.resource_rate * duration, self.carry_capacity - self.resources)
        print(f"{self.acronym}: Collected resources.")
        self.task = False

    def stockerRessources(self, building, map):
        if not self.isAvailable() or not building.resourceDropPoint:
            return
        self.task = True
        self.SeDeplacer(building.x, building.y, map)
        print(f"{self.acronym}: Stored resources.")
        building.addResources(self.resources)
        self.resources = 0
        self.task = False

    

    def buildTime(self, building, num_villagers):
        return max(10, (3 * building.buildTime) / (num_villagers + 2)) if num_villagers > 0 else building.buildTime