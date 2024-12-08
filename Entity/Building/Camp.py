from Entity.Building import Building

class Camp(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='C',
            woodCost=100,
            goldCost=0,
            buildTime=25,
            hp=200,
            size=2,
            resourceDropPoint=True
        )
        self.max_hp = self.hp  # ajout
