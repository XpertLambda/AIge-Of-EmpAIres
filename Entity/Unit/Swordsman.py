from Entity.Unit import Unit  

class Swordsman(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="s", 
            cost_food=50, 
            cost_gold=20, 
            cost_wood=0, 
            hp=40, 
            attack=4, 
            speed=0.9, 
            training_time=20
        )
