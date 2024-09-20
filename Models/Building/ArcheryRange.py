from Models.Building.Building import Building

class ArcheryRange(Building):
    def __init__(self):
        super().__init__(
            acronym='A',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size1=3,
            size2=3,
            spawnsUnits=True
        )
