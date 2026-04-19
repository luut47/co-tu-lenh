import pygame
import os
import sys
from config import settings

class HomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.SysFont(settings.FONT_NAME, 32)
        self.font_medium = pygame.font.SysFont(settings.FONT_NAME, 44)
        
        # Load images
        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'bg.png')).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))
        
        self.btn_human = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_human.png')).convert_alpha()
        self.btn_bot = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_bot.png')).convert_alpha()
        self.btn_guide = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_guide.png')).convert_alpha()
        self.btn_exit = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_exit.png')).convert_alpha()
        
        # Scale buttons down
        btn_w, btn_h = 280, 140
        self.btn_human = pygame.transform.smoothscale(self.btn_human, (btn_w, btn_h))
        self.btn_bot = pygame.transform.smoothscale(self.btn_bot, (btn_w, btn_h))
        self.btn_guide = pygame.transform.smoothscale(self.btn_guide, (btn_w, btn_h))
        self.btn_exit = pygame.transform.smoothscale(self.btn_exit, (btn_w, btn_h))

        self.right_side = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'home_right_side_.png')).convert_alpha()
        # Scale right side to fill height
        rs_h = settings.HEIGHT
        rs_w = int(self.right_side.get_width() * (rs_h / self.right_side.get_height()))
        self.right_side = pygame.transform.smoothscale(self.right_side, (rs_w, rs_h))
        
        left_pane_w = settings.WIDTH - rs_w
        self.left_center_x = left_pane_w // 2
        self.right_x = settings.WIDTH - rs_w
        self.right_y = 0
        
        start_y = 200
        gap = 40
        
        curr_y = start_y
        self.btn_human_rect = self.btn_human.get_rect(center=(self.left_center_x, curr_y))
        curr_y += btn_h + gap
        self.btn_bot_rect = self.btn_bot.get_rect(center=(self.left_center_x, curr_y))
        curr_y += btn_h + gap
        self.btn_guide_rect = self.btn_guide.get_rect(center=(self.left_center_x, curr_y))
        curr_y += btn_h + gap
        self.btn_exit_rect = self.btn_exit.get_rect(center=(self.left_center_x, curr_y))

        # Text lines
        self.credit_label = self.font_medium.render("Credit", True, settings.BLACK)
        self.author1 = self.font_small.render("Nguyen Trong Ha", True, settings.BLACK)
        self.author2 = self.font_small.render("Bui Van Han", True, settings.BLACK)
        self.author3 = self.font_small.render("Luu Minh Thang", True, settings.BLACK)
        
        curr_y = self.btn_exit_rect.bottom + 40
        self.credit_rect = self.credit_label.get_rect(center=(self.left_center_x, curr_y))
        
        # Left align the names
        a_w = max(self.author1.get_width(), self.author2.get_width(), self.author3.get_width())
        authors_left_x = self.left_center_x - a_w // 2
        
        curr_y += 45
        self.a1_rect = self.author1.get_rect(topleft=(authors_left_x, curr_y))
        curr_y += 45
        self.a2_rect = self.author2.get_rect(topleft=(authors_left_x, curr_y))
        curr_y += 45
        self.a3_rect = self.author3.get_rect(topleft=(authors_left_x, curr_y))

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        
        self.screen.blit(self.btn_human, self.btn_human_rect)
        self.screen.blit(self.btn_bot, self.btn_bot_rect)
        self.screen.blit(self.btn_guide, self.btn_guide_rect)
        self.screen.blit(self.btn_exit, self.btn_exit_rect)
        
        self.screen.blit(self.right_side, (self.right_x, self.right_y))
        
        self.screen.blit(self.credit_label, self.credit_rect)
        self.screen.blit(self.author1, self.a1_rect)
        self.screen.blit(self.author2, self.a2_rect)
        self.screen.blit(self.author3, self.a3_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.btn_human_rect.collidepoint(mouse_pos):
                    print("Human button clicked")
                elif self.btn_bot_rect.collidepoint(mouse_pos):
                    print("Bot button clicked")
                elif self.btn_guide_rect.collidepoint(mouse_pos):
                    print("Guide button clicked")
                elif self.btn_exit_rect.collidepoint(mouse_pos):
                    print("Exit button clicked")
                    pygame.quit()
                    sys.exit()
