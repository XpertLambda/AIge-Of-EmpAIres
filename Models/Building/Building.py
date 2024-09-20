class Building:
    def __init__(self, acronym, woodCost, buildingTime, hp, size1, size2, goldCost = 0, population=0, resourceDropPoint=False, spawnsUnits=False, containsFood=False, walkable=False):
        self.acronym = acronym
        self.woodCost = woodCost
        self.buildingTime = buildingTime
        self.hp = hp
        self.size1 = size1
        self.size2 = size2
        self.population = population
        self.resourceDropPoint = resourceDropPoint
        self.spawnsUnits = spawnsUnits
        self.containsFood = containsFood
        self.walkable = walkable

