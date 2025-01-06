
from Settings.setup import RESOURCE_CAPACITY, RESOURCE_COLLECTION_RATE , Resources
from Entity.Unit.Unit import Unit
class Villager(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="v",
            max_hp=40,
            cost=Resources(food=50, gold=0, wood=25),
            attack_power=0,
            attack_range=1,
            speed=1,
            training_time=20,
        )
        self.resources = 0
        self.carry_capacity = RESOURCE_CAPACITY
        self.resource_rate = RESOURCE_COLLECTION_RATE / 60
        self.resource_type = None

    def isAvailable(self):
        return not self.task

    def collectResource(self, resource_tile, duration, game_map):
        if not self.isAvailable():
            return
        if not resource_tile or resource_tile.terrain_type not in ["gold", "wood", "food"]:
            return
        self.task = True
        self.move(resource_tile.x, resource_tile.y, game_map)
        collected = min(self.resource_rate * duration, self.carry_capacity - self.resources)
        resource_tile.amount -= collected
        self.resources += collected
        self.resource_type = resource_tile.terrain_type
        if resource_tile.amount <= 0:
            game_map.remove_entity(resource_tile, resource_tile.x, resource_tile.y)
        self.task = False

    def stockResources(self, building, game_map, team):
        if not self.isAvailable() or not hasattr(building, 'resourceDropPoint') or not building.resourceDropPoint:
            return
        self.task = True
        self.move(building.x, building.y, game_map)
        if self.resource_type and self.resources > 0:
            team.resources[self.resource_type] += self.resources
        self.resources = 0
        self.resource_type = None
        self.task = False
