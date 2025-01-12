from Entity.Building import Building
from Models.Resources import Resources
from Entity.Unit.Horseman import Horseman

class Stable(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='S',
            size=3,
            max_hp=550,
            cost=Resources(food=0, gold=0, wood=175),
            buildTime=70,
            spawnsUnits=True
        )
