from Entity.Building import Building
from Models.Resources import Resources

class TownCentre(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='T',
            size=4,
            max_hp=1200,
            cost=Resources(food=0, gold=0, wood=350),
            buildTime=100,
            population=5,
            resourceDropPoint=True,
            spawnsUnits=True
        )