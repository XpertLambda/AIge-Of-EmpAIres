from Models.Building.Building import Building  

class House(Building):
    def __init__(self):
        super().__init__('H', 25, 25, 200, 2, 2, 5)