import pygame
import os
from config import settings

class CongrateVictoryPlayerScreen:
    def __init__(self, screen, winner_name="XXXXXX"):
        self.screen = screen
        self.winner_name = winner_name
        self.font_medium = pygame.font.SysFont(settings.FONT_NAME, 44)
        
        # Load background
        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_congrate_win_player_.png')).convert_alpha()
        # Assume it's a full screen background or a modal that we scale to fit screen
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))
        
        # Load button for winner name
        self.btn_name = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_name_player_victory_.png')).convert_alpha()
        
        # Positioning
        center_x = settings.WIDTH // 2
        # Position the button slightly below the vertical center
        self.btn_name_rect = self.btn_name.get_rect(center=(center_x, settings.HEIGHT // 2 + 80))
        
        # Render the winner name text
        self.name_text = self.font_medium.render(self.winner_name, True, settings.WHITE)
        self.name_text_rect = self.name_text.get_rect(center=self.btn_name_rect.center)

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.btn_name, self.btn_name_rect)
        self.screen.blit(self.name_text, self.name_text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.btn_name_rect.collidepoint(mouse_pos):
                    print(f"Winner {self.winner_name} button clicked")
