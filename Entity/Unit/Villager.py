from Settings.setup import RESOURCE_CAPACITY, RESOURCE_COLLECTION_RATE, Resources
from Entity.Resource.Resource import Resource
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
            attack_power=2,
            attack_range=1, 
            attack_speed=2.03,
            speed=1, 
            training_time=20, 

        )
        self.resources = Resources(food=0, gold=0, wood=0)
        self.carry_capacity = RESOURCE_CAPACITY
        self.resource_rate = RESOURCE_COLLECTION_RATE / 60

    def isAvailable(self):
        return not self.task

    def collectResource(self, resource_tile, duration, game_map):
        if not self.isAvailable():
            return
        if not isinstance(resource_tile, Resource):
            return
        self.task = True
        self.move(resource_tile.x, resource_tile.y, game_map)
        collected = min(
            self.resource_rate * duration,
            self.carry_capacity - getattr(self.resources, resource_tile.acronym.lower(), 0)
        )
        setattr(self.resources, resource_tile.acronym.lower(), getattr(self.resources, resource_tile.acronym.lower(), 0) + collected)
        resource_tile.storage = Resources(
            food=resource_tile.storage.food - (collected if resource_tile.acronym == "F" else 0),
            gold=resource_tile.storage.gold - (collected if resource_tile.acronym == "G" else 0),
            wood=resource_tile.storage.wood - (collected if resource_tile.acronym == "W" else 0),
        )
        if resource_tile.storage.food <= 0 and resource_tile.storage.gold <= 0 and resource_tile.storage.wood <= 0:
            game_map.remove_entity(resource_tile, resource_tile.x, resource_tile.y)
        self.task = False

    def stockResources(self, building, game_map, team):
        if not self.isAvailable() or not hasattr(building, 'resourceDropPoint') or not building.resourceDropPoint:
            return
        self.task = True
        self.move(building.x, building.y, game_map)
        team.resources = Resources(
            food=team.resources.food + self.resources.food,
            gold=team.resources.gold + self.resources.gold,
            wood=team.resources.wood + self.resources.wood,
        )
        self.resources = Resources(food=0, gold=0, wood=0)
        self.task = False

    def build(self, map,building):
        if not self.isAvailable():
            return
        self.task = True
        self.move((building.x, building.y), map)
        building.constructors.append(self)

    
    def buildTime(self, building, num_villagers):
        return max(10, (3 * building.buildTime) / (num_villagers + 2)) if num_villagers > 0 else building.buildTime