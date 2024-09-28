from Settings.setup import LEAN_NUMBER_OF_TOWER_CENTRE, LEAN_STARTING_FOOD, LEAN_STARTING_GOLD, LEAN_STARTING_VILLAGERS, LEAN_STARTING_WOOD
from Settings.setup import MEAN_NUMBER_OF_TOWER_CENTRE, MEAN_STARTING_FOOD, MEAN_STARTING_GOLD, MEAN_STARTING_VILLAGERS, MEAN_STARTING_WOOD
from Settings.setup import MARINES_NUMBER_OF_TOWER_CENTRE, MARINES_STARTING_FOOD, MARINES_STARTING_GOLD, MARINES_STARTING_VILLAGERS, MARINES_NUMBER_OF_ARCHERY_RANGES, MARINES_NUMBER_OF_BARRACKS, MARINES_NUMBER_OF_STABLES, MARINES_STARTING_WOOD

class Team:
    def __init__(self, difficulty):
        if difficulty == 'lean':
            self.resources = {'food': LEAN_STARTING_FOOD, 'wood': LEAN_STARTING_WOOD, 'gold': LEAN_STARTING_GOLD}
            self.units = {'villagers': LEAN_STARTING_VILLAGERS}
            self.buildings = {'town_centres': LEAN_NUMBER_OF_TOWER_CENTRE}

        elif difficulty == 'mean':
            self.resources = {'food': MEAN_STARTING_FOOD, 'wood': MEAN_STARTING_WOOD, 'gold': MEAN_STARTING_GOLD}
            self.units = {'villagers': MEAN_STARTING_VILLAGERS}
            self.buildings = {'town_centres': MEAN_NUMBER_OF_TOWER_CENTRE}

        elif difficulty == 'marines':
            self.resources = {'food': MARINES_STARTING_FOOD, 'wood': MARINES_STARTING_WOOD, 'gold': MARINES_STARTING_GOLD}
            self.units = {'villagers': MARINES_STARTING_VILLAGERS}
            self.buildings = {
                'town_centres': MARINES_NUMBER_OF_TOWER_CENTRE,
                'barracks': MARINES_NUMBER_OF_BARRACKS,
                'stables': MARINES_NUMBER_OF_STABLES,
                'archery_ranges': MARINES_NUMBER_OF_ARCHERY_RANGES
            }
        else:
            raise ValueError("Invalid difficulty level.")
        
        