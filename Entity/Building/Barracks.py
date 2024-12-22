from Entity.Building import Building
from Entity.Unit.Swordsman import Swordsman
from Settings.setup import Resources

class Barracks(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='B',
            size=3,
            max_hp=600,
            cost=Resources(food=0, gold=0, wood=175),
            buildTime=60,
            spawnsUnits=True
        )

    def build_time(self, num_villagers):
        return (3 * self.build_time) / (num_villagers + 2)

    def train(self, team, clock):
        swordsman = Swordsman(team)
        if(team.resources["food"] > swordsman.cost.food):
            team.en_cours[swordsman] = clock