from Models.Building.Building import Building  

class TownCentre(Building):
    def __init__(self):
        super().__init__('T', 350, 150, 1000, 4, 4)
        self.spawns_villagers = True
        self.drop_point_for_resources = True
        self.population_bonus = 5
        