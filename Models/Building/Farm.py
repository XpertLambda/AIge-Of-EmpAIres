from Models.Building.Building import Building

class Farm(Building):
    def __init__(self):
        super().__init__(
            acronym='F',
            woodCost=60,
            goldCost=0,
            buildTime=10,
            hp=100,
            size1=2,
            size2=2,
            containsFood=True,
            walkable=True  
        )
