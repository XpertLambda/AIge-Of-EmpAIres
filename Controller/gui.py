import pygame
import os
import sys
import time
from collections import OrderedDict, Counter
from Settings.setup import *
from Controller.init_assets import *
from Settings.setup import HALF_TILE_SIZE, MINIMAP_MARGIN, PANEL_RATIO, BG_RATIO
from Controller.utils import to_isometric, get_color_for_terrain
from Entity.Building import Building

pygame.init()
font = pygame.font.SysFont(None, 32)

user_choices["index_terminal_display"] = 2

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

def get_centered_rect_in_bottom_right(width, height, screen_width, screen_height, margin=10):
    rect = pygame.Rect(0, 0, width, height)
    center_x = screen_width - margin - (width // 2)
    center_y = screen_height - margin - (height // 2)
    rect.center = (center_x, center_y)
    return rect

def update_minimap_elements(game_state):
    from Entity.Building import Building
    from Entity.Resource.Gold import Gold

    camera = game_state['camera']
    game_map = game_state['game_map']
    team_colors = game_state['team_colors']
    scale_factor = game_state['minimap_scale']
    offset_x = game_state['minimap_offset_x']
    offset_y = game_state['minimap_offset_y']
    min_iso_x = game_state['minimap_min_iso_x']
    min_iso_y = game_state['minimap_min_iso_y']
    minimap_surface = game_state['minimap_entities_surface']

    minimap_surface.fill((0, 0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2

    entity_set = set()
    for pos, active_entities in game_map.grid.items():
        for ent in active_entities:
            entity_set.add(ent)

    MIN_BUILDING_SIZE = 3
    MIN_UNIT_RADIUS = 2

    for ent in entity_set:
        x_val, y_val = ent.x, ent.y
        iso_x, iso_y = to_isometric(x_val, y_val, tile_width, tile_height)
        mini_x = (iso_x - min_iso_x) * scale_factor + offset_x
        mini_y = (iso_y - min_iso_y) * scale_factor + offset_y

        if ent.team is not None:
            color_draw = team_colors[ent.team % len(team_colors)]
            if isinstance(ent, Building):
                half_dim = max(MIN_BUILDING_SIZE, ent.size)
                rect_building = pygame.Rect(
                    mini_x - half_dim, 
                    mini_y - half_dim, 
                    half_dim * 2, 
                    half_dim * 2
                )
                pygame.draw.rect(minimap_surface, (*color_draw, 150), rect_building)
            else:
                radius_val = max(MIN_UNIT_RADIUS, ent.size)
                pygame.draw.circle(minimap_surface, (*color_draw, 150), (mini_x, mini_y), radius_val)
        else:
            if isinstance(ent, Gold):
                gold_color = get_color_for_terrain('gold')
                radius_val = max(MIN_UNIT_RADIUS, ent.size)
                pygame.draw.circle(minimap_surface, (*gold_color, 150), (mini_x, mini_y), radius_val)

def run_gui_menu(screen, sw, sh):
    """
    Menu GUI bloquant : boucle Pygame jusqu'à ce que user_choices["validated"] == True
    ou fermeture de la fenêtre.

    Par défaut, toggle_button["index"] = 2 => Both (Terminal + GUI).
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
    
    back_button = {"text": "Retour", "rect": pygame.Rect(20, 20, 100, 40)}

    # On force la valeur par défaut à "Both" = index = 2
    toggle_button = {
        "rect": pygame.Rect(sw // 2 - 200, 400, 400, 50),
        "texts": ["Gui ONLY", "Terminal Display ONLY", "Terminal and Gui Display"],
        "index": 2  # => Both
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
                # Bouton "Retour"
                if (show_config_menu or show_load_menu) and back_button["rect"].collidepoint(mx, my):
                    show_main_menu = True
                    show_config_menu = False
                    show_load_menu = False
                    continue

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

                    # Si on clique en dehors, on referme
                    if not (combo_rect_grid.collidepoint(mx,my) or 
                            combo_rect_nbot.collidepoint(mx,my) or 
                            combo_rect_lvl.collidepoint(mx,my)):
                        combo_open = None

                if show_main_menu:
                    for i, btn in enumerate(main_buttons):
                        if btn["rect"].collidepoint(mx,my):
                            if i == 0:
                                user_choices["load_game"] = False
                                show_main_menu = False
                                show_config_menu = True
                            elif i == 1:
                                user_choices["load_game"] = True
                                show_main_menu = False
                                show_load_menu = True
                            else:
                                pygame.quit()
                                sys.exit()

                elif show_config_menu:
                    combo_rect_grid = pygame.Rect(sw//2 - 100, 100, 200, 30)
                    combo_rect_nbot = pygame.Rect(sw//2 - 100, 160, 200, 30)
                    combo_rect_lvl  = pygame.Rect(sw//2 - 100, 220, 200, 30)
                    if combo_rect_grid.collidepoint(mx,my):
                        combo_open = ("grid" if combo_open != "grid" else None)
                    elif combo_rect_nbot.collidepoint(mx,my):
                        combo_open = ("nbot" if combo_open != "nbot" else None)
                    elif combo_rect_lvl.collidepoint(mx,my):
                        combo_open = ("lvl" if combo_open != "lvl" else None)

                    chk_rect = pygame.Rect(sw//2 - 100, 280, 30, 30)
                    if chk_rect.collidepoint(mx,my):
                        gold_checked = not gold_checked
                        user_choices["gold_at_center"] = gold_checked

                    valid_rect = pygame.Rect(sw//2 - 50, 340, 100, 40)
                    if valid_rect.collidepoint(mx,my):
                        user_choices["validated"] = True
                        running = False

                    # Insert toggle_button logic here
                    if toggle_button["rect"].collidepoint(mx, my):
                        toggle_button["index"] = (toggle_button["index"] + 1) % len(toggle_button["texts"])
                        user_choices["index_terminal_display"] = toggle_button["index"]

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
            pygame.draw.rect(screen, (100, 100, 200), back_button["rect"])
            txt = font.render(back_button["text"], True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=back_button["rect"].center))

        elif show_load_menu:
            draw_load_menu(screen, sw, sh, save_files)
            pygame.draw.rect(screen, (100, 100, 200), back_button["rect"])
            txt = font.render(back_button["text"], True, (255,255,255))
            screen.blit(txt, txt.get_rect(center=back_button["rect"].center))

        pygame.display.flip()
        
        # Met à jour la variable globale index_terminal_display
        # d'après l'état du bouton toggle_button
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
    if combo_open != "grid":
        draw_combo_box(screen, sw//2 - 100, 100, 200, 30, f"Taille: {VALID_GRID_SIZES[idx_grid]}", None, idx_grid)
    if combo_open != "nbot":
        draw_combo_box(screen, sw//2 - 100, 160, 200, 30, f"Bots: {VALID_BOTS_COUNT[idx_nbot]}", None, idx_nbot)
    if combo_open != "lvl":
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
    from Settings.setup import user_choices
    if user_choices["index_terminal_display"] == 1:  # Terminal only mode
        return None

    selection_height = 30
    padding = 5

    screen = pygame.display.get_surface()
    screen_height = screen.get_height() if screen else 600  # Default height if no screen
    max_height = screen_height / 3

    columns = 1
    while columns <= 4:
        rows = (len(players) + columns - 1) // columns
        total_height = selection_height * rows + padding * (rows - 1)
        if (total_height <= max_height or columns == 4):
            break
        columns += 1

    button_width = (minimap_rect.width - padding * (columns - 1)) // columns
    rows = (len(players) + columns - 1) // columns
    total_height = selection_height * rows + padding * (rows - 1)

    surface = pygame.Surface((minimap_rect.width, total_height), pygame.SRCALPHA)
    font_sel = pygame.font.Font(None, 24)

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
        player_text = font_sel.render(f'Player {player.teamID}', True, (0, 0, 0))
        text_rect = player_text.get_rect(center=rect.center)
        surface.blit(player_text, text_rect)

    return surface

def create_player_info_surface(selected_player, screen_width, screen_height, team_colors):
    from Settings.setup import user_choices
    if user_choices["index_terminal_display"] == 1:  # Terminal only mode
        return None
        
    font_info = pygame.font.Font(None, 24)
    padding_x = int(screen_width * 0.0)  # 0.7% du screen width comme padding horizontal
    padding_y = int(screen_height * 0.028)  # 2% du screen height comme padding vertical
    surface = pygame.Surface((screen_width, 300), pygame.SRCALPHA)

    spacing_x = int(screen_width * 0.057)  # 3% du screen width entre les éléments
    spacing_y = int(screen_height * 0.022)  # 2% de la hauteur de l'écran entre les éléments

    gold_str = f"{selected_player.resources.gold}"
    wood_str = f"{selected_player.resources.wood}"
    food_str = f"{selected_player.resources.food}"

    gold_surf = font_info.render(gold_str, True, (255, 255, 255))
    wood_surf = font_info.render(wood_str, True, (255, 255, 255))
    food_surf = font_info.render(food_str, True, (255, 255, 255))

    x_offset = padding_x
    surface.blit(gold_surf, (x_offset, padding_y))  # Utilise padding_y au lieu de padding
    x_offset += gold_surf.get_width() + spacing_x
    surface.blit(wood_surf, (x_offset, padding_y))  # Utilise padding_y au lieu de padding
    x_offset += wood_surf.get_width() + spacing_x
    surface.blit(food_surf, (x_offset, padding_y))  # Utilise padding_y au lieu de padding

    y_after_resources = padding_y + gold_surf.get_height() + spacing_y

    # Player name
    team_color = team_colors[selected_player.teamID % len(team_colors)]
    player_name_surface = font_info.render(f"Player {selected_player.teamID}", True, team_color)
    surface.blit(player_name_surface, (padding_x, y_after_resources))
    y_after_resources += player_name_surface.get_height() + spacing_y

    # Units
    unit_counts = Counter(unit.acronym for unit in selected_player.units)
    units_text = "Units - " + ", ".join([f"{acronym}: {count}" for acronym, count in unit_counts.items()])
    units_surface = font_info.render(units_text, True, (255, 255, 255))
    surface.blit(units_surface, (padding_x, y_after_resources))
    y_after_resources += units_surface.get_height() + spacing_y

    # Buildings
    building_counts = Counter(building.acronym for building in selected_player.buildings)
    buildings_text = "Buildings - " + ", ".join([f"{acronym}: {count}" for acronym, count in building_counts.items()])
    buildings_surface = font_info.render(buildings_text, True, (255, 255, 255))
    surface.blit(buildings_surface, (padding_x, y_after_resources))
    y_after_resources += buildings_surface.get_height() + spacing_y

    # Population
    population_text = f"Population: {selected_player.population} / {selected_player.maximum_population}"
    population_surface = font.render(population_text, True, (255, 255, 255))
    surface.blit(population_surface, (padding_x, y_after_resources))

    return surface

def draw_game_over_overlay(screen, game_state):
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((50, 50, 50, 150))
    font_big = pygame.font.SysFont(None, 60)
    font_small = pygame.font.SysFont(None, 40)

    winner_id = game_state.get('winner_id', '?')
    text_surf = font_big.render(f"Bravo ! Joueur {winner_id} a gagné", True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(screen.get_width()//2, screen.get_height()//3))
    overlay.blit(text_surf, text_rect)

    button_text = "Quitter le jeu"
    button_surf = font_small.render(button_text, True, (255, 255, 255))
    button_width = button_surf.get_width() + 20
    button_height = button_surf.get_height() + 10
    button_x = (screen.get_width() - button_width) // 2
    button_y = screen.get_height() // 2
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    pygame.draw.rect(overlay, (100, 100, 100), button_rect)
    overlay.blit(button_surf, button_surf.get_rect(center=button_rect.center))

    game_state['game_over_button_rect'] = button_rect
    screen.blit(overlay, (0, 0))

def draw_pause_menu(screen, game_state):
    font = pygame.font.SysFont(None, 50)
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']

    pause_text = font.render("Pause Menu", True, (255, 255, 255))
    text_rect = pause_text.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(pause_text, text_rect)

    button_font = pygame.font.SysFont(None, 36)
    labels = ["Resume", "Load Game", "Save Game", "Exit"]
    y_start = text_rect.bottom + 40
    button_rects = {}

    for label in labels:
        text_surf = button_font.render(label, True, (255, 255, 255))
        rect = text_surf.get_rect(center=(screen_width // 2, y_start))
        pygame.draw.rect(screen, (50, 50, 50), rect.inflate(100, 20))
        screen.blit(text_surf, rect)
        button_rects[label] = rect
        y_start += 60

    game_state['pause_menu_button_rects'] = button_rects
