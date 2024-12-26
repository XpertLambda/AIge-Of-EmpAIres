import pygame
import os
import time
from collections import OrderedDict
from Settings.setup import *
from Controller.init_assets import gui_elements

gui_cache = {}

def get_scaled_gui(ui_name, variant=0, target_width=None, target_height=None):
    global gui_cache
    key = (ui_name, variant, target_width, target_height)
    if key in gui_cache:
        return gui_cache[key]

    original = gui_elements[ui_name][variant]
    ow, oh = original.get_width(), original.get_height()
    if target_width and not target_height:
        ratio = target_width / ow
        target_height = int(oh * ratio)
    elif target_height and not target_width:
        ratio = target_height / oh
        target_width = int(ow * ratio)
    elif not target_width and not target_height:
        gui_cache[key] = original
        return original

    scaled = pygame.transform.smoothscale(original, (target_width, target_height))
    gui_cache[key] = scaled
    return scaled

def draw_gui_elements(screen, screen_width, screen_height):
    panel_img = get_scaled_gui('ResourcesPanel', 0, target_width=screen_width//2)
    screen.blit(panel_img, (0, 0))
    pw, ph = panel_img.get_width(), panel_img.get_height()

    icon_scale_width = pw // 22

    gold_img = get_scaled_gui('gold', 0, target_width=icon_scale_width)
    gold_x = 12
    screen.blit(gold_img, (gold_x, ph // 15))

    wood_img = get_scaled_gui('wood', 0, target_width=icon_scale_width)
    wood_x = gold_x + gold_img.get_width() + (2 * gold_img.get_width())
    screen.blit(wood_img, (wood_x, ph // 15))

    food_img = get_scaled_gui('food', 0, target_width=icon_scale_width)
    food_x = wood_x + wood_img.get_width() + (2 * wood_img.get_width())
    screen.blit(food_img, (food_x, ph // 15))

    minimap_img = get_scaled_gui('minimapPanel', 0, target_width=screen_width // 4)
    mpw, mph = minimap_img.get_width(), minimap_img.get_height()
    screen.blit(minimap_img, (screen_width - mpw, screen_height - mph))
