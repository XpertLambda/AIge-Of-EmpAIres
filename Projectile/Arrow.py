import time
import math
from Settings.setup import *
from Controller.utils import tile_to_screen, get_angle, get_snapped_angle, get_direction, normalize
from Controller.drawing import draw_sprite, draw_healthBar, draw_hitbox
import pygame
from pygame.locals import *
from collections import deque
#import numpy as np

class Arrow:
    id = 0
    def __init__(self, launcher, target):
        # Attack attributes
        self.launcher = launcher
        self.target = target
        self.distance = math.dist((launcher.x, launcher.y), (target.x ,target.y))
        self.attack_power = launcher.attack_power
        self.speed = 5
        self.cooldown_frame = None
        self.impact = False
        self.impact_timer = 0
        
        # Animation attributes
        self.frames = FRAMES_PER_PROJECTILE
        self.current_frame = 0
        self.frame_step = self.distance / self.frames
        self.cooldown_frame = None
        self.state = 'motion'

        # Positional attributes
        self.start = None
        self.end = None
        self.peak = None
        self.x = None
        self.y = None
        self.z = None
        self.angle = None
        self.direction = 0
        self.progress = 0

        # Identification attributes
        self.acronym = 'a'
        self.id = Arrow.id
        Arrow.id += 1

    def update(self, game_map, dt):
        self.seekMotion(dt)
        self.animator(dt)
        self.seekImpact(dt)

    def animator(self, dt):
        if self.state:
            frame_id = math.dist((self.x, self.y, self.z), self.start) // self.frame_step
            self.current_frame = round(min(self.frames -1 , frame_id))

            if self.cooldown_frame:
                self.current_frame = self.cooldown_frame

    def launch(self, game_map, z_launch):
        self.start = (self.launcher.x, self.launcher.y, z_launch)
        self.end   = (self.target.x,   self.target.y, 1.5)
        self.x, self.y, self.z = self.start

        # Calculate a better peak z based on distance
        peak_z = max(self.start[2], self.end[2]) + self.distance * 0.3 + 2
        self.peak = ((self.start[0] + self.end[0]) / 2,
                     (self.start[1] + self.end[1]) / 2,
                     peak_z)

        self.angle = get_angle((self.x, self.y), (self.target.x, self.target.y))
        self.direction = get_direction(get_snapped_angle((self.x, self.y), (self.target.x, self.target.y)))
        game_map.add_projectile(self)

    def seekMotion(self, dt):
        if self.impact and self.target:
            self.x = self.target.x
            self.y = self.target.y
        elif self.start:
            self.progress += dt * (self.speed / self.distance)
            current_progress = min(self.progress, 1)

            self.x = self.start[0] + (self.end[0] - self.start[0]) * current_progress
            self.y = self.start[1] + (self.end[1] - self.start[1]) * current_progress
            self.z = (1 - current_progress)**2 * self.start[2] \
                   + 2*(1 - current_progress)*current_progress*self.peak[2] \
                   + current_progress**2 * self.end[2]

            if current_progress >= 1:
                self.impact = True

    def seekImpact(self, dt):
        if self.impact and self.target:
            if self.impact_timer == 0:
                self.target.hp -= self.attack_power
            self.impact_timer += dt

            if self.impact_timer >= 2:
                self.state = ''

    def display(self, screen, screen_width, screen_height, camera, dt):
        if self.state != '':
            sx, sy = tile_to_screen(self.x, self.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2, camera, screen_width, screen_height, self.z)
            draw_sprite(screen, self.acronym, 'projectiles', sx, sy, camera.zoom, state=self.state, frame=self.current_frame, direction=self.direction)