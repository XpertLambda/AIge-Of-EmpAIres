import random
from Controller.init_assets import sprite_config
from Entity.Resource.Resource import Resource
from Settings.setup import Resources

class Gold(Resource):
    def __init__(self, 
        x, 
        y, 
        acronym = 'G', 
        storage = Resources(food=0, gold=800, wood=0),
        max_hp=500
        ):

        super().__init__(x=x, y=y, acronym=acronym, storage=storage, max_hp=max_hp, variant=random.randint(0, sprite_config['resources']['tree']['variant'] - 1))
