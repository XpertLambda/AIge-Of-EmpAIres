from Entity.Unit import Unit  

class Horseman(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="h", 
            cost_food=80, 
            cost_gold=20, 
            cost_wood=0, 
            hp=45, 
            attack=4, 
            speed=1.2, 
            training_time=30
        )
