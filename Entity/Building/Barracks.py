from Entity.Building import Building
from Entity.Unit.Swordsman import Swordsman
import time

class Barracks(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='B',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size=3,
            spawnsUnits=True
        )
        self.max_hp = self.hp  # ajout

    def build_time(self, num_villagers):
        return (3 * Barracks.build_time) / (num_villagers + 2)
    def entraine(self,t,clock):
        s=Swordsman(t)
        if(t.resources["food"]>s.cost_food):
            t.en_cours[s]=clock