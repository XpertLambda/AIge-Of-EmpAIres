from Models.Unit.Unit import Unit  

class Swordsman(Unit):
    def __init__(self):
        super().__init__(acronym="S", cost_food=50, cost_gold=20, cost_wood=0, hp=40, attack=4, speed=0.9, training_time=20,x=0,y=0)
