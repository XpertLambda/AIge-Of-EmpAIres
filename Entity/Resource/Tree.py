from Entity.Resource.Resource import Resource
from Models.Resources import Resources
from Controller.init_assets import sprite_config
import random

class Tree(Resource):
    def __init__(self, 
        x, 
        y, 
        acronym = 'W', 
        storage = Resources(food=0, gold=0, wood=100),
        max_hp=100
        ):

        super().__init__(x=x, y=y, acronym=acronym, storage=storage, max_hp=max_hp, variant=random.randint(0, sprite_config['resources']['tree']['variant'] - 1))

    def get_variant(self):
        return self.variant