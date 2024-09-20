from Models.Unit.Unit import Unit  

class Horseman(Unit):
    def __init__(self):
        super().__init__(acronym="H", cost_food=80, cost_gold=20, cost_wood=0, hp=45, attack=4, speed=1.2, training_time=30)
