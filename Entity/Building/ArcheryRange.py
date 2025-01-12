from Entity.Building import Building
from Models.Resources import Resources
from Entity.Unit import Archer

class ArcheryRange(Building):
    def __init__(self, x=0, y=0, team=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='A',
            size=3,
            max_hp=500,
            cost=Resources(food=0, gold=0, wood=175),
            buildTime=50,
            spawnsUnits=True
        )
