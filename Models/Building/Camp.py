from Models.Building.Building import Building

class Camp(Building):
    def __init__(self):
        super().__init__(
            acronym='C',
            woodCost=100,
            goldCost=0,
            buildTime=25,
            hp=200,
            size1=2,
            size2=2,
            resourceDropPoint=True
        )
