from Entity.Building import Building

class TownCentre(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='T',
            woodCost=350,
            goldCost=0,
            buildTime=150,
            hp=1000,
            size=4,
            population=5,
            resourceDropPoint=True,
            spawnsUnits=True
        )
        self.max_hp = self.hp  # ajout
