from Entity.Building import Building

class Farm(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='F',
            woodCost=60,
            goldCost=0,
            buildTime=10,
            hp=100,
            size=2,
            containsFood=True,
            walkable=True  
        )
