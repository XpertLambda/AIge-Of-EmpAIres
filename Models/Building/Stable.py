from Models.Building.Building import Building
from Models.Unit.Horseman import Horseman
import time

class Stable(Building):
    def __init__(self):
        super().__init__(
            acronym='S',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size1=3,
            size2=3,
            spawnsUnits=True
        )
    def entraine(self):
        h=Horseman()
        time.sleep(h.training_time)
        return h