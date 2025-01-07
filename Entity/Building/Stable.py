from Entity.Building import Building
from Settings.setup import Resources
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

    def train(self, team, clock,map):
        horseman = Horseman(team)
        if(team.resources["food"] >= horseman.cost.food and team.resources["gold"] >= horseman.cost.gold and team.maximum_population>len(team.units)):
            team.resources["food"] -= horseman.cost.food
            team.resources["gold"] -= horseman.cost.gold
            team.en_cours[horseman] = clock
           
        else:
            print("not enough resssources or maximum poulation reached")