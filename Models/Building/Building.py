class Building:
    def __init__(self, acronym, woodCost, goldCost, buildTime, hp, size1, size2, x = None, y = None, population=0, resourceDropPoint=False, spawnsUnits=False, containsFood=False, walkable=False, attack=0, range=0, state=0):
        self.acronym = acronym
        self.woodCost = woodCost
        self.goldCost = goldCost
        self.buildTime = buildTime
        self.hp = hp
        self.size1 = size1
        self.size2 = size2
        self.population = population
        self.resourceDropPoint = resourceDropPoint
        self.spawnsUnits = spawnsUnits
        self.containsFood = containsFood
        self.walkable = walkable
        self.attack = attack
        self.range = range
        self.x = x
        self.y = y
        self.state = state  # Current animation type
        #DEBUG : maybe we remove it if we don't want building animation
        self.current_frame = 0  # Current frame in the animation
        self.frame_counter = 0  # Counter to control animation speed
        self.frame_duration = 2  # Duration each frame is displayed