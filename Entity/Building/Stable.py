from Entity.Building import Building
from Entity.Unit.Horseman import Horseman
import time

class Stable(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='S',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size=3,
            spawnsUnits=True
        )
        self.max_hp = self.hp  # ajout
