import pygame

def draw_player_selection(screen, players, selected_player, minimap_rect):
    """
    Dessine les zones de sélection des joueurs au-dessus de la minimap.
    """
    selection_height = 30  # Hauteur de chaque zone de sélection
    padding = 5            # Espacement entre les zones
    for i, player in enumerate(players):
        # Calcul des coordonnées de chaque zone de sélection
        rect_x = minimap_rect.x
        rect_y = minimap_rect.y - (i + 1) * (selection_height + padding)
        rect_width = minimap_rect.width
        rect = pygame.Rect(rect_x, rect_y, rect_width, selection_height)
        
        # Couleur de sélection ou de fond
        color = (0, 100, 255) if player == selected_player else (150, 150, 150)
        pygame.draw.rect(screen, color, rect)
        
        # Texte du joueur (utilisez pygame.font pour le rendu du texte)
        font = pygame.font.Font(None, 24)
        text = font.render(f"Player {i}", True, (255, 255, 255))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

    return selection_height * len(players) + padding * (len(players) - 1)