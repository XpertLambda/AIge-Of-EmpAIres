from Models.Unit.Unit import Unit  
from Settings.setup import BUILDING_TIME_REDUCTION, RESOURCE_COLLECTION_RATE, RESOURCE_CAPACITY

class Villager(Unit):
    def __init__(self):
        super().__init__(acronym="V", cost_food=50, cost_gold=0, cost_wood=0, hp=25, attack=2, speed=0.8, training_time=25)
        self.building_time_reduction = BUILDING_TIME_REDUCTION  # Facteur de réduction du temps de construction
        self.resource_collection_rate = RESOURCE_COLLECTION_RATE  # Taux de collecte de ressources (unités par minute)
        self.resource_capacity = RESOURCE_CAPACITY  # Capacité de transport des ressources
        
  
	# Calcule le temps de construction en fonction du nombre de villageois
    def build_time(self, remaining_time, num_villagers):
        return (3 * remaining_time) / (num_villagers + 2)