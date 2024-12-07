from Entity.Building import Building

class Keep(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='K',
            woodCost=35,
            goldCost=125,
            buildTime=80,
            hp=800,
            size=1,
            attack=5,
            range=8
        )
