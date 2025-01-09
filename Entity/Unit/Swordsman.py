from Entity.Unit import Unit
from Settings.setup import Resources

class Swordsman(Unit):
    def __init__(self, team=None, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="s",
            max_hp=40,
            cost=Resources(food=50, gold=20, wood=0),
            attack_power=4,
            attack_range=1,
            attack_speed=2.03,
            speed=0.9,
            training_time=20
        )
