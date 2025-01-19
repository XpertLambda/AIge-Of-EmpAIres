from Models.Team import *
from Settings.setup import  RESOURCE_THRESHOLDS

#Priorty seven avoid ressources shortage 

def get_resource_shortage(current_resources, thresholds):
    # Access the specific resource attributes from the Resources object
    if current_resources.food < thresholds['food']:
        return 'food'
    if current_resources.wood < thresholds['wood']:
        return 'wood'
    if current_resources.gold < thresholds['gold']:
        return 'gold'
    return None
def find_resource_location(game_map, resource_acronym):
    for (x, y), cell_content in game_map.grid.items():
        if resource_acronym in cell_content:
            return (x, y)  


def reallocate_villagers(resource_in_shortage, villagers, game_map):
    for villager in villagers:
        if villager.isAvailable() and not villager.task:
            for x, y in game_map.grid:
                resource_nodes = game_map.grid[(x, y)]
                for resource_node in resource_nodes:
                    if resource_node.acronym.lower() == resource_in_shortage[0].lower():
                        villager.set_target(resource_node)
                        return


def check_and_address_resources(team, game_map, thresholds):
    resource_shortage = get_resource_shortage(team.resources, thresholds)
    if resource_shortage:
        reallocate_villagers(resource_shortage, team.units, game_map)
    
        
# AI resource management Logic

# 1. Monitor resource levels for shortages
# - Use the current resource levels and predefined thresholds.
# - Identify if any resource is below its threshold.

# 2. Reallocate villagers to address resource shortages
# - Find idle villagers or villagers collecting less critical resources.
# - Assign them to collect the resource in shortage.
# - Ensure villagers are directed to the closest available resource node.

# 3. Integrate into the game loop
# - Periodically check resource levels and act accordingly.
# - Address shortages by reallocating villagers.
