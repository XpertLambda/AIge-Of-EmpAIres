from Controller.terminal_display_debug import debug_print

class Zone:
    def __init__(self):
        self.zone = set() 

    def reset(self):
        self.zone.clear()

    def set_zone(self, start, end):
        self.zone.clear()
        x1, y1 = start
        x2, y2 = end
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.zone.add((x, y))

    def add_zone(self, start, end):
        x1, y1 = start
        x2, y2 = end
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.zone.add((x, y))

    def remove_zone(self, start, end):
        x1, y1 = start
        x2, y2 = end
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.zone.discard((x, y))

    def add_tile(self, position):
        self.zone.add(position)

    def remove_tile(self, position):
        self.zone.discard(position)

    def inZone(self, zone=None, tile=None):
        if tile is not None:
            return tile in self.zone
        if zone is not None and isinstance(zone, Zone):
            return not self.zone.isdisjoint(zone.zone)
        return False

    def get_zone(self):
        return self.zone

    def __eq__(self, other):
        return isinstance(other, Zone) and self.zone == other.zone

    def __repr__(self):
        return f"Zone({sorted(self.zone)})"
