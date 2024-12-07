from Entity.Resource.Resource import *
class Food(Resource):
    def __init__(self, x, y, acronym = 'F', storage = 0):
        super().__init__(x, y, acronym, storage)
