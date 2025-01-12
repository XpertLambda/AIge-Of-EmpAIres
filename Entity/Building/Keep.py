from Entity.Building import Building
from Models.Resources import Resources

class Keep(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='K',
            size=1,
            max_hp=800,
            cost=Resources(food=0, gold=125, wood=35),
            buildTime=80,
            attack_power=5,
            attack_range=8
        )
