import pygame
import os
import sys
import time
from collections import OrderedDict, Counter
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


pygame.init()
font = pygame.font.SysFont(None, 32)

user_choices = {
    "grid_size":     100,
    "num_bots":      1,
    "bot_level":     "lean",
    "gold_at_center":False,
    "load_game":     False,
    "chosen_save":   None,
    "validated":     False
}

VALID_GRID_SIZES = [i for i in range(100, 1000, 10)]
VALID_BOTS_COUNT = [i for i in range(1, 56)]
VALID_LEVELS = ["lean", "mean", "marines", "DEBUG"]

def ask_terminal_inputs():
    if user_choices["validated"]:
        # Skip immediately if GUI already validated
        print("GUI has validated, skipping terminal inputs.")
        return

    print("\n--- Menu Terminal ---")
    print("[1] Nouvelle partie / [2] Charger une sauvegarde ?")
    choice = input("Choix : ")
    if choice == '2':
        user_choices["load_game"] = True
        if os.path.isdir(SAVE_DIRECTORY):
            saves = [f for f in os.listdir(SAVE_DIRECTORY) if f.endswith('.pkl')]
            if saves:
                print("Saves disponibles :")
                for idx, sf in enumerate(saves):
                    print(f"{idx+1} - {sf}")
                sel = input("Sélection de la sauvegarde : ")
                try:
                    sel_idx = int(sel) - 1
                    if 0 <= sel_idx < len(saves):
                        user_choices["chosen_save"] = os.path.join(SAVE_DIRECTORY, saves[sel_idx])
                        user_choices["validated"] = True
                        return
                except:
                    pass
            print("Aucune sauvegarde valable, on repasse en mode 'nouvelle partie'")
            user_choices["load_game"] = False

    print("\n--- Paramètres de la nouvelle partie : ---")
    print("Tailles possibles : ", VALID_GRID_SIZES)
    g_str = input(f"Taille (défaut={user_choices['grid_size']}) : ")
    if g_str.isdigit():
        g_val = int(g_str)
        if g_val in VALID_GRID_SIZES:
            user_choices["grid_size"] = g_val

    print(f"Nb bots possibles : 1..55 (défaut={user_choices['num_bots']})")
    n_str = input("Nb bots : ")
    if n_str.isdigit():
        n_val = int(n_str)
        if 1 <= n_val <= 55:
            user_choices["num_bots"] = n_val

    print("Niveaux possibles :", VALID_LEVELS)
    lvl = input(f"Niveau bots (défaut={user_choices['bot_level']}) : ")
    if lvl in VALID_LEVELS:
        user_choices["bot_level"] = lvl

    o_str = input("Or au centre ? (oui/non, défaut=non) : ").lower()
    if o_str == "oui":
        user_choices["gold_at_center"] = True

    user_choices["validated"] = True

    # Remove any blocking loop here
    return

def run_gui_menu(screen, sw, sh):
    clock = pygame.time.Clock()
    show_main_menu   = True
    show_config_menu = False
    show_load_menu   = False

    main_buttons = [
        {"text": "Nouvelle Partie", "rect": pygame.Rect(0,0,200,50)},
        {"text": "Charger Partie",  "rect": pygame.Rect(0,0,200,50)},
        {"text": "Quitter",         "rect": pygame.Rect(0,0,200,50)},
    ]

    save_files = []
    if os.path.isdir(SAVE_DIRECTORY):
        save_files = [f for f in os.listdir(SAVE_DIRECTORY) if f.endswith('.pkl')]

    if user_choices["grid_size"] not in VALID_GRID_SIZES:
        user_choices["grid_size"] = VALID_GRID_SIZES[0]
    idx_grid = VALID_GRID_SIZES.index(user_choices["grid_size"])
    idx_nbot = VALID_BOTS_COUNT.index(user_choices["num_bots"])
    idx_lvl  = VALID_LEVELS.index(user_choices["bot_level"])

    gold_checked = user_choices["gold_at_center"]
    combo_open = None

    running = True
    while running:
        clock.tick(60)
        screen.fill((30,30,30))

        if user_choices["validated"]:
            running = False

        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_main_menu:
                    for i, btn in enumerate(main_buttons):
                        if btn["rect"].collidepoint(mx,my):
                            if i == 0:
                                user_choices["load_game"] = False
                                show_main_menu   = False
                                show_config_menu = True
                            elif i == 1:
                                user_choices["load_game"] = True
                                show_main_menu   = False
                                show_load_menu   = True
                            else:
                                pygame.quit()
                                sys.exit()

                elif show_config_menu:
                    # 1) If a combo is open, check combo items first
                    if combo_open=="grid":
                        item_height = 25
                        for idx_item, val in enumerate(VALID_GRID_SIZES):
                            combo_item_rect = pygame.Rect(sw//2 - 100, 100 + (idx_item+1)*item_height, 200, item_height)
                            if combo_item_rect.collidepoint(mx,my):
                                idx_grid = idx_item
                                user_choices["grid_size"] = VALID_GRID_SIZES[idx_grid]
                                combo_open = None
                                break

                    elif combo_open=="nbot":
                        item_height = 25
                        max_items = 10
                        for idx_item, val in enumerate(VALID_BOTS_COUNT):
                            if idx_item<max_items:
                                combo_item_rect = pygame.Rect(sw//2 - 100, 160 + (idx_item+1)*item_height, 200, item_height)
                                if combo_item_rect.collidepoint(mx,my):
                                    idx_nbot = idx_item
                                    user_choices["num_bots"] = VALID_BOTS_COUNT[idx_nbot]
                                    combo_open = None
                                    break

                    elif combo_open=="lvl":
                        item_height = 25
                        for idx_item, val in enumerate(VALID_LEVELS):
                            combo_item_rect = pygame.Rect(sw//2 - 100, 220 + (idx_item+1)*item_height, 200, item_height)
                            if combo_item_rect.collidepoint(mx,my):
                                idx_lvl = idx_item
                                user_choices["bot_level"] = VALID_LEVELS[idx_lvl]
                                combo_open = None
                                break

                    # 2) If we didn't click an item in an open combo, check whether we toggle combos or click buttons
                    combo_rect = pygame.Rect(sw//2 - 100, 100, 200, 30)
                    if combo_rect.collidepoint(mx,my):
                        combo_open = ("grid" if combo_open!="grid" else None)

                    combo_rect2 = pygame.Rect(sw//2 - 100, 160, 200, 30)
                    if combo_rect2.collidepoint(mx,my):
                        combo_open = ("nbot" if combo_open!="nbot" else None)

                    combo_rect3 = pygame.Rect(sw//2 - 100, 220, 200, 30)
                    if combo_rect3.collidepoint(mx,my):
                        combo_open = ("lvl" if combo_open!="lvl" else None)

                    # Checkbox
                    chk_rect = pygame.Rect(sw//2 - 100, 280, 30, 30)
                    if chk_rect.collidepoint(mx,my):
                        gold_checked = not gold_checked
                        user_choices["gold_at_center"] = gold_checked

                    # Validate
                    valid_rect = pygame.Rect(sw//2 - 50, 340, 100, 40)
                    if valid_rect.collidepoint(mx,my):
                        user_choices["validated"] = True
                        running = False

                elif show_load_menu:
                    start_y = 100
                    gap = 5
                    block_h = 30
                    for i, sf in enumerate(save_files):
                        rect = pygame.Rect(sw//2 - 150, start_y + i*(block_h+gap), 300, block_h)
                        if rect.collidepoint(mx,my):
                            user_choices["chosen_save"] = os.path.join(SAVE_DIRECTORY, sf)
                            user_choices["load_game"] = True
                            user_choices["validated"] = True
                            running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    combo_open = None

        if show_main_menu:
            draw_main_menu(screen, sw, sh, main_buttons)
        elif show_config_menu:
            draw_config_menu(screen, sw, sh, idx_grid, idx_nbot, idx_lvl, gold_checked, combo_open)
        elif show_load_menu:
            draw_load_menu(screen, sw, sh, save_files)

        pygame.display.flip()

def draw_main_menu(screen, sw, sh, buttons):
    gap = 20
    start_y = (sh - (len(buttons)*50 + gap*(len(buttons)-1))) // 2
    for i, btn in enumerate(buttons):
        btn["rect"].centerx = sw//2
        btn["rect"].y = start_y + i*(50+gap)
        pygame.draw.rect(screen, (100, 100, 200), btn["rect"])
        txt = font.render(btn["text"], True, (255,255,255))
        screen.blit(txt, txt.get_rect(center=btn["rect"].center))

def draw_config_menu(screen, sw, sh, idx_grid, idx_nbot, idx_lvl, gold_checked, combo_open):
    # Draw fixed UI first
    # ...existing code up to combo drawing...

    # Draw closed combos
    if combo_open!="grid":
        draw_combo_box(screen, sw//2 - 100, 100, 200, 30, f"Taille: {VALID_GRID_SIZES[idx_grid]}", None, idx_grid)
    if combo_open!="nbot":
        draw_combo_box(screen, sw//2 - 100, 160, 200, 30, f"Bots: {VALID_BOTS_COUNT[idx_nbot]}", None, idx_nbot)
    if combo_open!="lvl":
        draw_combo_box(screen, sw//2 - 100, 220, 200, 30, f"Niveau: {VALID_LEVELS[idx_lvl]}", None, idx_lvl)

    # Draw rest (checkbox, valider)
    chk_rect = pygame.Rect(sw//2 - 100, 280, 30, 30)
    pygame.draw.rect(screen, (200,200,200), chk_rect)
    if gold_checked:
        pygame.draw.line(screen, (0,0,0), (chk_rect.x+5, chk_rect.centery), (chk_rect.right-5, chk_rect.centery), 3)
    txt = font.render("Or au centre ?", True, (255,255,255))
    screen.blit(txt, (chk_rect.right+10, chk_rect.y))

    valid_rect = pygame.Rect(sw//2 - 50, 340, 100, 40)
    pygame.draw.rect(screen, (80,200,80), valid_rect)
    vtxt = font.render("Valider", True, (255,255,255))
    screen.blit(vtxt, vtxt.get_rect(center=valid_rect.center))

    # Finally draw any opened combo on top
    if combo_open=="grid":
        draw_combo_box(screen, sw//2 - 100, 100, 200, 30, f"Taille: {VALID_GRID_SIZES[idx_grid]}", VALID_GRID_SIZES, idx_grid)
    elif combo_open=="nbot":
        draw_combo_box(screen, sw//2 - 100, 160, 200, 30, f"Bots: {VALID_BOTS_COUNT[idx_nbot]}", VALID_BOTS_COUNT[:10], idx_nbot)
    elif combo_open=="lvl":
        draw_combo_box(screen, sw//2 - 100, 220, 200, 30, f"Niveau: {VALID_LEVELS[idx_lvl]}", VALID_LEVELS, idx_lvl)

def draw_combo_box(screen, x, y, w, h, text, items_list, selected_idx):
    box_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (60,60,160), box_rect)
    screen.blit(font.render(text, True, (255,255,255)), (x+5, y+3))
    if items_list:
        total_height = len(items_list)*25
        shadow_surf = pygame.Surface((w, total_height))
        shadow_surf.set_alpha(160)
        shadow_surf.fill((0,0,0))
        screen.blit(shadow_surf, (x, y+h))
        item_height = 25
        for i, val in enumerate(items_list):
            rect = pygame.Rect(x, y+(i+1)*item_height, w, item_height)
            pygame.draw.rect(screen, (60,60,120), rect)
            screen.blit(font.render(str(val), True, (255,255,255)), (rect.x+5, rect.y+3))

def draw_load_menu(screen, sw, sh, save_files):
    start_y = 100
    gap = 5
    block_h = 30
    txt = font.render("Choisissez la sauvegarde :", True, (255,255,255))
    screen.blit(txt, (sw//2 - txt.get_width()//2, 50))

    for i, sf in enumerate(save_files):
        rect = pygame.Rect(sw//2 - 150, start_y + i*(block_h+gap), 300, block_h)
        pygame.draw.rect(screen, (180,80,80), rect)
        txt2 = font.render(sf, True, (255,255,255))
        screen.blit(txt2, txt2.get_rect(center=rect.center))


def create_player_selection_surface(players, selected_player, minimap_rect, team_colors):
    selection_height = 30
    padding = 5

    # Get screen height
    screen = pygame.display.get_surface()
    screen_height = screen.get_height()
    max_height = screen_height / 3  # Taille maximale de 1/3 de la fenêtre

    # Determine the optimal number of columns
    columns = 1
    while columns <= 4:
        rows = (len(players) + columns - 1) // columns
        total_height = selection_height * rows + padding * (rows - 1)
        if total_height <= max_height or columns == 4:
            break
        columns += 1

    button_width = (minimap_rect.width - padding * (columns - 1)) // columns
    rows = (len(players) + columns - 1) // columns
    total_height = selection_height * rows + padding * (rows - 1)

    surface = pygame.Surface((minimap_rect.width, total_height), pygame.SRCALPHA)

    font = pygame.font.Font(None, 24)

    for index, player in enumerate(reversed(players)):
        col = index % columns
        row = index // columns
        rect_x = col * (button_width + padding)
        rect_y = row * (selection_height + padding)
        rect = pygame.Rect(rect_x, rect_y, button_width, selection_height)

        if player == selected_player:
            color = (255, 255, 255)
        else:
            color = team_colors[player.teamID % len(team_colors)]

        pygame.draw.rect(surface, color, rect)

        player_text = font.render(f'Player {player.teamID}', True, (0, 0, 0))
        text_rect = player_text.get_rect(center=rect.center)
        surface.blit(player_text, text_rect)

    return surface

def create_player_info_surface(selected_player, screen_width, team_colors):
    font = pygame.font.Font(None, 24)
    padding = 5
    info_height = 160
    surface = pygame.Surface((screen_width, info_height), pygame.SRCALPHA)

    team_color = team_colors[selected_player.teamID % len(team_colors)]
    player_name_surface = font.render(f"Player {selected_player.teamID}", True, team_color)
    surface.blit(player_name_surface, (padding, 0))

    resources_text = f"Resources - Food: {selected_player.resources['food']}, Wood: {selected_player.resources['wood']}, Gold: {selected_player.resources['gold']}"
    resources_surface = font.render(resources_text, True, (255, 255, 255))
    surface.blit(resources_surface, (padding, 30))

    unit_counts = Counter(unit.acronym for unit in selected_player.units)
    units_text = "Units - " + ", ".join([f"{acronym}: {count}" for acronym, count in unit_counts.items()])
    units_surface = font.render(units_text, True, (255, 255, 255))
    surface.blit(units_surface, (padding, 60))

    building_counts = Counter(building.acronym for building in selected_player.buildings)
    buildings_text = "Buildings - " + ", ".join([f"{acronym}: {count}" for acronym, count in building_counts.items()])
    buildings_surface = font.render(buildings_text, True, (255, 255, 255))
    surface.blit(buildings_surface, (padding, 90))

    maximum_population_text = (f"Maximum population : {selected_player.maximum_population}")
    maximum_population = font.render(maximum_population_text, True, (255, 255, 255))
    surface.blit(maximum_population, (padding, 120))

    return surface
