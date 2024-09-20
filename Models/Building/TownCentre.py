from Models.Building.Building import Building

class TownCentre(Building):
    def __init__(self):
        super().__init__(
            acronym='T',
            woodCost=350,
            goldCost=0,
            buildTime=150,
            hp=1000,
            size1=4,
            size2=4,
            population=5,
            resourceDropPoint=True,
            spawnsUnits=True
        )
