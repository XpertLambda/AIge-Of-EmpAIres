import random
from Controller.init_assets import sprite_config
from Entity.Resource.Resource import Resource
from Models.Resources import Resources
import math

class Gold(Resource):
    def __init__(self, 
        x, 
        y, 
        acronym = 'G', 
        storage = Resources(food=0, gold=800, wood=0),
        max_hp=800
        ):

        super().__init__(x=x, y=y, acronym=acronym, storage=storage, max_hp=max_hp, variant=random.randint(0, sprite_config['resources']['tree']['variant'] - 1))

    def get_variant(self, total_variants=sprite_config['resources']['gold']['variant']):
        ratio = (self.max_hp - self.hp) / float(self.max_hp)
        self.variant = int(math.floor(ratio * (total_variants - 1)))
        return min(self.variant, total_variants)