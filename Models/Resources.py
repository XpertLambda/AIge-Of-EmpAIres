class Resources:
    def __init__(self, food, wood, gold):
        self.food = food
        self.wood = wood
        self.gold = gold

    def copy(self):
        return Resources(self.food, self.wood, self.gold)

    def __eq__(self, other):
        if not isinstance(other, Resources):
            return NotImplemented
        return self.food == other.food and self.wood == other.wood and self.gold == other.gold