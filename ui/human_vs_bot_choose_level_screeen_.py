import pygame
import os
from config import settings
from ui.human_vs_bot_home_screen_ import HumanVsBotHomeScreen
from services.sound_manager import SoundManager

class HumanVsBotChooseLevelScreen:
    def __init__(self, screen):
        self.screen = screen
        
        # Load background
        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'screen_choose_bot_level_.png')).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))
        
        # Load buttons
        btn_w, btn_h = 300, 170
        self.btn_easy = pygame.transform.smoothscale(pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_level_easy.png')).convert_alpha(), (btn_w, btn_h))
        self.btn_normal = pygame.transform.smoothscale(pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_level_nomal_.png')).convert_alpha(), (btn_w, btn_h))
        self.btn_hard = pygame.transform.smoothscale(pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_level_hard.png')).convert_alpha(), (btn_w, btn_h))
        self.btn_asian = pygame.transform.smoothscale(pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_level_asian_.png')).convert_alpha(), (btn_w, btn_h))
        
        # Positioning
        center_x = settings.WIDTH // 2
        
        # Start Y around 450, adjust gap if needed
        start_y = 300
        gap = 200
        
        self.btn_easy_rect = self.btn_easy.get_rect(center=(center_x, start_y))
        self.btn_normal_rect = self.btn_normal.get_rect(center=(center_x, start_y + gap))
        self.btn_hard_rect = self.btn_hard.get_rect(center=(center_x, start_y + gap * 2))
        self.btn_asian_rect = self.btn_asian.get_rect(center=(center_x, start_y + gap * 3))

        self.sound_manager = SoundManager()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.btn_easy, self.btn_easy_rect)
        self.screen.blit(self.btn_normal, self.btn_normal_rect)
        self.screen.blit(self.btn_hard, self.btn_hard_rect)
        self.screen.blit(self.btn_asian, self.btn_asian_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.btn_easy_rect.collidepoint(mouse_pos):
                    self.sound_manager.play_button()
                    return HumanVsBotHomeScreen(self.screen)
                elif self.btn_normal_rect.collidepoint(mouse_pos):
                    self.sound_manager.play_button()
                    return HumanVsBotHomeScreen(self.screen)
                elif self.btn_hard_rect.collidepoint(mouse_pos):
                    self.sound_manager.play_button()
                    return HumanVsBotHomeScreen(self.screen)
                elif self.btn_asian_rect.collidepoint(mouse_pos):
                    self.sound_manager.play_button()
                    return HumanVsBotHomeScreen(self.screen)
