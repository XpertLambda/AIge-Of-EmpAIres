from Entity.Building import Building
from Entity.Unit.Swordsman import Swordsman
from Models.Resources import Resources

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

    def train(self, team, clock,map):
        swordsman = Swordsman(team.teamID)
        if(team.resources["food"] >= swordsman.cost.food and team.resources["gold"] >= swordsman.cost.gold and team.maximum_population>len(team.units)):
            team.resources["food"] -= swordsman.cost.food
            team.resources["gold"] -= swordsman.cost.gold
            team.en_cours[swordsman] = clock
        else:
            print("not enough resssources or maximum poulation reached")