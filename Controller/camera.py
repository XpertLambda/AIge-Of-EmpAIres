from Settings.setup import MAX_ZOOM
from Controller.utils import screen_to_tile, tile_to_screen

class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.min_zoom = 0.15  # Default value, will be adjusted based on map size
        self.zoom = self.min_zoom  # Initialize with default min_zoom
        self.width = width
        self.height = height
        self.min_x = None
        self.max_x = None
        self.min_y = None
        self.max_y = None

    def apply(self, x, y):
        # Apply camera transformations to coordinates
        x = (x + self.offset_x) * self.zoom + self.width / 2
        y = (y + self.offset_y) * self.zoom + self.height / 2
        return x, y

    def unapply(self, screen_x, screen_y):
        # Convert screen coordinates to world coordinates
        world_x = (screen_x - self.width / 2) / self.zoom - self.offset_x
        world_y = (screen_y - self.height / 2) / self.zoom - self.offset_y
        return world_x, world_y

    def move(self, dx, dy):
        # Move the camera by dx and dy
        self.offset_x += dx / self.zoom
        self.offset_y += dy / self.zoom
        self.limit_camera()

    def set_zoom(self, zoom_factor):
        # Set the zoom level within allowed limits using instance min_zoom
        self.zoom = max(self.min_zoom, min(zoom_factor, MAX_ZOOM))
        self.limit_camera()

    def set_bounds(self, min_x, max_x, min_y, max_y):
        # Set the camera bounds
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.limit_camera()

    def limit_camera(self):
        # Limit the camera to the set bounds
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

    def zoom_out_to_global(self):
        # Center the camera on the entire map and zoom out
        self.offset_x = - (self.min_x + self.max_x) / 2
        self.offset_y = - (self.min_y + self.max_y) / 2
        self.zoom = self.min_zoom  # Use the dynamic min_zoom directly
        self.limit_camera()