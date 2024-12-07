from Entity.Building import Building


class House(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='H',
            woodCost=25,
            goldCost=0,
            buildTime=25,
            hp=200,
            size=2,
            population=5
        )
