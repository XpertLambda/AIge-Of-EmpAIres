from Models.Building.Building import Building

class Stable(Building):
    def __init__(self):
        super().__init__(
            acronym='S',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size1=3,
            size2=3,
            spawnsUnits=True
        )
