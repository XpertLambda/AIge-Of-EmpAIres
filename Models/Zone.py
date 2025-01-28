from Controller.terminal_display_debug import debug_print

class Zone:
    def __init__(self):
        self.zone = []

    def reset(self):
        self.zone.clear()

    def set_zone(self, start, end):
        self.zone.clear()
        x1, y1 = start
        x2, y2 = end
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                tile = (x, y)
                self.zone.append(tile)

    def add_zone(self, start, end):
        x1, y1 = start
        x2, y2 = end
        to_add = []
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                tile = (x, y)
                to_add.append(tile)
        for tile in to_add:
            self.zone.append(tile)
        return to_add

    def remove_zone(self, start, end):
        x1, y1 = start
        x2, y2 = end
        to_remove = []
        for x in range(int(min(x1, x2)), int(max(x1, x2) + 1)):
            for y in range(int(min(y1, y2)), int(max(y1, y2) + 1)):
                tile = (x, y)
                if tile in self.zone:
                    to_remove.append(tile)
        for tile in to_remove:
            self.zone.remove(tile)
        return to_remove

    def add_tile(self, position):
        self.zone.append(position)

    def remove_tile(self, position):
        if position in self.zone:
            self.zone.remove(position)

    def inZone(self, zone=None, tile=None):
        if tile is not None:
            return tile in self.zone
        if zone is not None and isinstance(zone, Zone):
            return any(tile in self.zone for tile in zone.zone)
        return False

    def get_zone(self):
        return sorted(set(self.zone))

    def __eq__(self, other):
        return isinstance(other, Zone) and sorted(self.zone) == sorted(other.zone)

    def __repr__(self):
        return f"Zone({sorted(set(self.zone))})"