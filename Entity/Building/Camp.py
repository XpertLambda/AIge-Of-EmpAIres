from Entity.Building import Building
from Models.Resources import Resources

class Camp(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='C',
            size=2,
            max_hp=200,
            cost=Resources(food=0, gold=0, wood=100),
            buildTime=25,
            resourceDropPoint=True
        )
