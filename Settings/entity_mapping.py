from Entity.Unit import *
from Entity.Building import *
from Entity.Resource import *
# -------------------
# Mapping Entity Classess
# -------------------
unit_class_map = {
        'Villager': Villager,
        'Archer': Archer,
        'Horseman': Horseman,
        'Swordsman': Swordsman
    }

building_class_map = {
    'TownCenter': TownCentre,
    'Barracks': Barracks,
    'Stable': Stable,
    'ArcheryRange': ArcheryRange,
    'Farm': Farm,
    'Keep': Keep,
    'House': House,
    'Camp': Camp
}


resources_class_map = {
        'Gold': Gold,
        'Tree': Tree
    }