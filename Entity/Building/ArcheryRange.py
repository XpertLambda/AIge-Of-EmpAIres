from Entity.Building import Building
from Entity.Unit.Archer import Archer
import time

class ArcheryRange(Building):
    def __init__(self, x=0, y=0, team=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='A',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size=3,
            spawnsUnits=True
        )
        self.max_hp = self.hp  # ajout
