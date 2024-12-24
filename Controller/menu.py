import pygame
import os
import sys
from Settings.setup import SAVE_DIRECTORY

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

VALID_GRID_SIZES = [i for i in range(100, 201, 10)]
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
