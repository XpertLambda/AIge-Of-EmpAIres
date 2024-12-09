from Entity.Resource.Resource import *
class Wood(Resource):
    def __init__(self, x, y, acronym = 'W', storage = 0):
        super().__init__(x, y, acronym, storage)
