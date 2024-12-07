# Controller/camera.py

from Settings.setup import *
from Controller.isometric_utils import *

class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 0.25
        self.width = width
        self.height = height
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

    def apply(self, x, y):
        x = (x + self.offset_x) * self.zoom + self.width / 2
        y = (y + self.offset_y) * self.zoom + self.height / 2
        return x, y

    def unapply(self, screen_x, screen_y):
        # Convertit les coordonnées de l'écran en coordonnées du monde
        world_x = (screen_x - self.width / 2) / self.zoom - self.offset_x
        world_y = (screen_y - self.height / 2) / self.zoom - self.offset_y
        return world_x, world_y

    def move(self, dx, dy):
        self.offset_x += dx / self.zoom
        self.offset_y += dy / self.zoom
        self.limit_camera()

    def set_zoom(self, zoom_factor):
        # Limiter le zoom entre un minimum et un maximum
        self.zoom = max(MIN_ZOOM, min(zoom_factor, MAX_ZOOM))
        self.limit_camera()

    def set_bounds(self, min_x, max_x, min_y, max_y):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.limit_camera()

    def limit_camera(self):
        if self.min_x is None or self.max_x is None:
            return

        half_screen_width = self.width / (2 * self.zoom)
        half_screen_height = self.height / (2 * self.zoom)

        min_offset_x = - (self.max_x - half_screen_width)
        max_offset_x = - (self.min_x + half_screen_width)
        min_offset_y = - (self.max_y - half_screen_height)
        max_offset_y = - (self.min_y + half_screen_height)

        self.offset_x = max(min_offset_x, min(self.offset_x, max_offset_x))
        self.offset_y = max(min_offset_y, min(self.offset_y, max_offset_y))

