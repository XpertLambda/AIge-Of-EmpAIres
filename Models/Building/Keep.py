from Models.Building.Building import Building

class Keep(Building):
    def __init__(self):
        super().__init__(
            acronym='K',
            woodCost=35,
            goldCost=125,
            buildTime=80,
            hp=800,
            size1=1,
            size2=1,
            attack=5,
            range=8
        )
