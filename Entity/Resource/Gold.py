from Entity.Resource.Resource import *
class Gold(Resource):
    def __init__(self, x, y, acronym = 'G', storage = 0):
        super().__init__(x, y, acronym, storage)
