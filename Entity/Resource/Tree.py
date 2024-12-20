from Entity.Resource.Resource import *
class Tree(Resource):
    def __init__(self, x, y, acronym = 'W', storage = 0):
        super().__init__(x, y, acronym, storage, variant=random.randint(0, sprite_config['resources']['tree']['variant'] - 1))
