import pygame
import os
import sys
import time
from collections import OrderedDict, Counter
from Settings.setup import *
from Controller.init_assets import *

pygame.init()
font = pygame.font.SysFont(None, 32)

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
        # Pas de mise à l'échelle
        gui_cache[key] = original
        return original

    scaled = pygame.transform.smoothscale(original, (target_width, target_height))
    gui_cache[key] = scaled
    return scaled

def draw_gui_elements(screen, screen_width, screen_height):
    """
    Dessine le panneau de ressources (en haut) et autres éléments.
    """
    resources_panel_img = get_scaled_gui('ResourcesPanel', 0, target_width=screen_width // 2)
    screen.blit(resources_panel_img, (0, 0))

    pw, ph = resources_panel_img.get_width(), resources_panel_img.get_height()
    icon_scale_width = pw // 22

    # On place 3 icônes (gold, wood, food) alignées, petit offset vertical
    gold_img = get_scaled_gui('gold', 0, target_width=icon_scale_width)
    gold_x = 12
    screen.blit(gold_img, (gold_x, ph // 15))

    wood_img = get_scaled_gui('wood', 0, target_width=icon_scale_width)
    wood_x = gold_x + gold_img.get_width() + (2 * gold_img.get_width())
    screen.blit(wood_img, (wood_x, ph // 15))

    food_img = get_scaled_gui('food', 0, target_width=icon_scale_width)
    food_x = wood_x + wood_img.get_width() + (2 * wood_img.get_width())
    screen.blit(food_img, (food_x, ph // 15))

def run_gui_menu(screen, sw, sh):
    """
    Menu GUI bloquant : boucle Pygame jusqu'à ce que user_choices["validated"] == True
    ou fermeture de la fenêtre.
    """
    clock = pygame.time.Clock()
    show_main_menu   = True
    show_config_menu = False
    show_load_menu   = False

    main_buttons = [
        {"text": "Nouvelle Partie", "rect": pygame.Rect(0,0,200,50)},
        {"text": "Charger Partie",  "rect": pygame.Rect(0,0,200,50)},
        {"text": "Quitter",         "rect": pygame.Rect(0,0,200,50)},
    ]
    
    # Add back button
    back_button = {"text": "Retour", "rect": pygame.Rect(20, 20, 100, 40)}

    toggle_button = {
        "rect": pygame.Rect(sw // 2 - 200, 400, 400, 50),
        "texts": ["Gui ONLY", "Terminal Display ONLY", "Terminal and Gui Display"],
        "index": 0  # État actuel
    }

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

            elif event.type == pygame.MOUSEWHEEL:
                if combo_open == "grid":
                    if event.y < 0:
                        if combo_scroll_positions["grid"] < len(VALID_GRID_SIZES) - MAX_VISIBLE_ITEMS:
                            combo_scroll_positions["grid"] += 1
                    else:
                        if combo_scroll_positions["grid"] > 0:
                            combo_scroll_positions["grid"] -= 1

                elif combo_open == "nbot":
                    if event.y < 0:
                        if combo_scroll_positions["nbot"] < len(VALID_BOTS_COUNT) - MAX_VISIBLE_ITEMS:
                            combo_scroll_positions["nbot"] += 1
                    else:
                        if combo_scroll_positions["nbot"] > 0:
                            combo_scroll_positions["nbot"] -= 1

                elif combo_open == "lvl":
                    if event.y < 0:
                        if combo_scroll_positions["lvl"] < len(VALID_LEVELS) - MAX_VISIBLE_ITEMS:
                            combo_scroll_positions["lvl"] += 1
                    else:
                        if combo_scroll_positions["lvl"] > 0:
                            combo_scroll_positions["lvl"] -= 1

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Add back button handling at the start
                if (show_config_menu or show_load_menu) and back_button["rect"].collidepoint(mx, my):
                    show_main_menu = True
                    show_config_menu = False
                    show_load_menu = False
                    continue

                if toggle_button["rect"].collidepoint(mx, my):
                    toggle_button["index"] = (toggle_button["index"] + 1) % len(toggle_button["texts"])
                    
                if combo_open == "grid":
                    start_idx = combo_scroll_positions["grid"]
                    visible_items = VALID_GRID_SIZES[start_idx:start_idx + MAX_VISIBLE_ITEMS]
                    item_height = ITEM_HEIGHT

                    expanded_rect = pygame.Rect(sw//2 - 100, 100 + item_height, 200, item_height * len(visible_items))
                    if expanded_rect.collidepoint(mx,my):
                        relative_y = my - (100 + item_height)
                        item_index = relative_y // item_height
                        if 0 <= item_index < len(visible_items):
                            new_val = visible_items[item_index]
                            idx_grid = VALID_GRID_SIZES.index(new_val)
                            user_choices["grid_size"] = new_val
                        combo_open = None
                        continue
                elif combo_open == "nbot":
                    start_idx = combo_scroll_positions["nbot"]
                    visible_items = VALID_BOTS_COUNT[start_idx:start_idx + MAX_VISIBLE_ITEMS]
                    expanded_rect = pygame.Rect(sw//2 - 100, 160 + ITEM_HEIGHT, 200, ITEM_HEIGHT * len(visible_items))
                    if expanded_rect.collidepoint(mx,my):
                        relative_y = my - (160 + ITEM_HEIGHT)
                        item_index = relative_y // ITEM_HEIGHT
                        if 0 <= item_index < len(visible_items):
                            new_val = visible_items[item_index]
                            idx_nbot = VALID_BOTS_COUNT.index(new_val)
                            user_choices["num_bots"] = new_val
                        combo_open = None
                        continue
                elif combo_open == "lvl":
                    start_idx = combo_scroll_positions["lvl"]
                    visible_items = VALID_LEVELS[start_idx:start_idx + MAX_VISIBLE_ITEMS]
                    expanded_rect = pygame.Rect(sw//2 - 100, 220 + ITEM_HEIGHT, 200, ITEM_HEIGHT * len(visible_items))
                    if expanded_rect.collidepoint(mx,my):
                        relative_y = my - (220 + ITEM_HEIGHT)
                        item_index = relative_y // ITEM_HEIGHT
                        if 0 <= item_index < len(visible_items):
                            new_val = visible_items[item_index]
                            idx_lvl = VALID_LEVELS.index(new_val)
                            user_choices["bot_level"] = new_val
                        combo_open = None
                        continue

                if combo_open:
                    combo_rect_grid = pygame.Rect(sw//2 - 100, 100, 200, 30)
                    combo_rect_nbot = pygame.Rect(sw//2 - 100, 160, 200, 30)
                    combo_rect_lvl  = pygame.Rect(sw//2 - 100, 220, 200, 30)

                    if not (combo_rect_grid.collidepoint(mx,my) or 
                            combo_rect_nbot.collidepoint(mx,my) or 
                            combo_rect_lvl.collidepoint(mx,my)):
                        if combo_open not in ["", None]:
                            combo_open = None

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
                    combo_rect = pygame.Rect(sw//2 - 100, 100, 200, 30)
                    combo_rect2= pygame.Rect(sw//2 - 100, 160, 200, 30)
                    combo_rect3= pygame.Rect(sw//2 - 100, 220, 200, 30)
                    if combo_rect.collidepoint(mx,my):
                        combo_open = ("grid" if combo_open!="grid" else None)
                    elif combo_rect2.collidepoint(mx,my):
                        combo_open = ("nbot" if combo_open!="nbot" else None)
                    elif combo_rect3.collidepoint(mx,my):
                        combo_open = ("lvl" if combo_open!="lvl" else None)

                    chk_rect = pygame.Rect(sw//2 - 100, 280, 30, 30)
                    if chk_rect.collidepoint(mx,my):
                        gold_checked = not gold_checked
                        user_choices["gold_at_center"] = gold_checked

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
            draw_choose_display(screen, toggle_button)
            # Draw back button
            pygame.draw.rect(screen, (100, 100, 200), back_button["rect"])
            txt = font.render(back_button["text"], True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=back_button["rect"].center))
        elif show_load_menu:
            draw_load_menu(screen, sw, sh, save_files)
            # Draw back button
            pygame.draw.rect(screen, (100, 100, 200), back_button["rect"])
            txt = font.render(back_button["text"], True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=back_button["rect"].center))

        pygame.display.flip()
        
        user_choices["index_terminal_display"] = toggle_button["index"]

def draw_choose_display(screen, toggle_button):
    pygame.draw.rect(screen, (0, 122, 255), toggle_button["rect"])
    font = pygame.font.Font(None, 36)
    text_surface = font.render(toggle_button["texts"][toggle_button["index"]], True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=toggle_button["rect"].center)
    screen.blit(text_surface, text_rect)


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
    if combo_open!="grid":
        draw_combo_box(screen, sw//2 - 100, 100, 200, 30, f"Taille: {VALID_GRID_SIZES[idx_grid]}", None, idx_grid)
    if combo_open!="nbot":
        draw_combo_box(screen, sw//2 - 100, 160, 200, 30, f"Bots: {VALID_BOTS_COUNT[idx_nbot]}", None, idx_nbot)
    if combo_open!="lvl":
        draw_combo_box(screen, sw//2 - 100, 220, 200, 30, f"Niveau: {VALID_LEVELS[idx_lvl]}", None, idx_lvl)

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

    if combo_open == "grid":
        draw_combo_box(screen, sw//2 - 100, 100, 200, 30, f"Taille: {VALID_GRID_SIZES[idx_grid]}", 
                       VALID_GRID_SIZES, idx_grid, combo_type="grid")
    elif combo_open == "nbot":
        draw_combo_box(screen, sw//2 - 100, 160, 200, 30, f"Bots: {VALID_BOTS_COUNT[idx_nbot]}", 
                       VALID_BOTS_COUNT, idx_nbot, combo_type="nbot")
    elif combo_open == "lvl":
        draw_combo_box(screen, sw//2 - 100, 220, 200, 30, f"Niveau: {VALID_LEVELS[idx_lvl]}", 
                       VALID_LEVELS, idx_lvl, combo_type="lvl")

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

def draw_combo_box(screen, x, y, w, h, text, items_list, selected_idx, combo_type=None):
    """
    Dessine un combo box. Si items_list est None, c'est un combo fermé.
    Si items_list existe, on l'affiche sous forme d'une liste scrollable (max 5 items).
    """
    box_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, (60,60,160), box_rect)
    screen.blit(font.render(text, True, (255,255,255)), (x+5, y+3))

    if items_list:
        start_idx = combo_scroll_positions[combo_type]
        visible_items = items_list[start_idx:start_idx + MAX_VISIBLE_ITEMS]

        total_height = len(visible_items) * ITEM_HEIGHT
        shadow_surf = pygame.Surface((w, total_height))
        shadow_surf.set_alpha(160)
        shadow_surf.fill((0,0,0))
        screen.blit(shadow_surf, (x, y + h))

        for i, val in enumerate(visible_items):
            rect = pygame.Rect(x, y + h + i*ITEM_HEIGHT, w, ITEM_HEIGHT)
            pygame.draw.rect(screen, (60,60,120), rect)
            txt = font.render(str(val), True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=rect.center))

        if len(items_list) > MAX_VISIBLE_ITEMS:
            scroll_bar_height = 50
            scroll_bar_x = x + w - 10
            scroll_bar_y = y + h
            scroll_track_height = total_height
            pygame.draw.rect(screen, (100,100,100), (scroll_bar_x, scroll_bar_y, 10, scroll_track_height))

            ratio = start_idx / float(len(items_list) - MAX_VISIBLE_ITEMS)
            cursor_y = scroll_bar_y + int(ratio * (scroll_track_height - scroll_bar_height))
            pygame.draw.rect(screen, (200,200,200), (scroll_bar_x, cursor_y, 10, scroll_bar_height))

def create_player_selection_surface(players, selected_player, minimap_rect, team_colors):
    selection_height = 30
    padding = 5

    screen = pygame.display.get_surface()
    screen_height = screen.get_height()
    max_height = screen_height / 3

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

    resources_text = (f"Resources - Food: {selected_player.resources['food']}, "
                      f"Wood: {selected_player.resources['wood']}, "
                      f"Gold: {selected_player.resources['gold']}")
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
