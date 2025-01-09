from Entity.Unit import Unit
from Settings.setup import Resources

class Archer(Unit):
    def __init__(self, team=None, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="a",
            max_hp=30,
            cost=Resources(food=0, gold=45, wood=25),
            attack_power=4,
            attack_range=4,
            attack_speed=2.03,
            speed=1,
            training_time=35
        )
