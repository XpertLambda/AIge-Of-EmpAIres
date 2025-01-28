from Entity.Building import Building
from Models.Resources import Resources

class Farm(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='F',
            size=2,
            max_hp=100,
            cost=Resources(food=0, gold=0, wood=60),
            buildTime=10,
            hasResources = True,
            walkable=True,
        )
        self.storage = Resources(food=300, gold=0, wood=0)
