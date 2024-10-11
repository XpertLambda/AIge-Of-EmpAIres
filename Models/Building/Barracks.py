from Models.Building.Building import Building
from Models.Unit.Swordsman import Swordsman
import time

class Barracks(Building):
    def __init__(self):
        super().__init__(
            acronym='B',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size1=3,
            size2=3,
            spawnsUnits=True
        )
    def entraine(self):
        s=Swordsman()
        time.sleep(s.training_time)
        return s
