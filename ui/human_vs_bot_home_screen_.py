import pygame
import os
import sys
from config import settings

class HumanVsBotHomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.SysFont(settings.FONT_NAME, 32)
        self.font_medium = pygame.font.SysFont(settings.FONT_NAME, 44)
        
        # Load images
        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'on_play_screen_backgroud_.png')).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))
        
        self.icon_human = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'icon_human.png')).convert_alpha()
        self.icon_human_2 = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'icon_human_2_.png')).convert_alpha()
        self.slide_time = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'slide_time_couting_.png')).convert_alpha()
        
        self.panel_right = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'panel_show_user_moved_.png')).convert_alpha()
        self.panel_detail = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'panel_show_user_moved_detail_.png')).convert_alpha()
        
        self.btn_setting = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_setting_.png')).convert_alpha()
        
        self.btn_surrender = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_surrender.png')).convert_alpha()
        self.btn_undo = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_bot_mode_undo_moved_.png')).convert_alpha()
        self.btn_play_again = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_play_again_bot_.png')).convert_alpha()
        # Scale UI assets down to prevent overlapping
        face_size = (50, 50)
        slide_size = (300, 60)
        setting_size = (100, 150)
        panel_w, panel_h = 500, 750
        detail_w, detail_h = 400, 200
        btn_w, btn_h = 180, 60
        btn_undo_w, btn_undo_h = 100, 60
        
        self.icon_human = pygame.transform.smoothscale(self.icon_human, face_size)
        self.icon_human_2 = pygame.transform.smoothscale(self.icon_human_2, face_size)
        self.slide_time = pygame.transform.smoothscale(self.slide_time, slide_size)
        
        self.panel_right = pygame.transform.smoothscale(self.panel_right, (panel_w, panel_h))
        self.panel_detail = pygame.transform.smoothscale(self.panel_detail, (detail_w, detail_h))
        
        self.btn_setting = pygame.transform.smoothscale(self.btn_setting, setting_size)
        self.btn_surrender = pygame.transform.smoothscale(self.btn_surrender, (btn_w, btn_h))
        self.btn_undo = pygame.transform.smoothscale(self.btn_undo, (btn_undo_w , btn_undo_h ))
        self.btn_play_again = pygame.transform.smoothscale(self.btn_play_again, (btn_w, btn_h))
        
        # Resize small icons for detail panel
        detail_icon_size = (40, 40)
        self.small_icon_human = pygame.transform.smoothscale(self.icon_human, detail_icon_size)
        self.small_icon_human_2 = pygame.transform.smoothscale(self.icon_human_2, detail_icon_size)
        
        # Positioning
        
        # Top Player (Blue)
        self.icon_human_rect = self.icon_human.get_rect(topleft=(300, 30))
        self.name1_label = self.font_medium.render("Human", True, settings.BLACK)
        self.name1_rect = self.name1_label.get_rect(midleft=(self.icon_human_rect.right + 20, self.icon_human_rect.centery))
        
        self.slide_time_top_rect = self.slide_time.get_rect(center=(settings.WIDTH // 2, self.icon_human_rect.centery))
        self.time1_label = self.font_medium.render("00:00", True, settings.BLACK)
        self.time1_rect = self.time1_label.get_rect(center=self.slide_time_top_rect.center)
        
        # Bottom Player (Red)
        self.icon_human_2_rect = self.icon_human_2.get_rect(bottomleft=(300, settings.HEIGHT - 30))
        self.name2_label = self.font_medium.render("Bot", True, settings.BLACK)
        self.name2_rect = self.name2_label.get_rect(midleft=(self.icon_human_2_rect.right + 20, self.icon_human_2_rect.centery))
        
        self.slide_time_bottom_rect = self.slide_time.get_rect(center=(settings.WIDTH // 2, self.icon_human_2_rect.centery))
        self.time2_label = self.font_medium.render("00:00", True, settings.BLACK)
        self.time2_rect = self.time2_label.get_rect(center=self.slide_time_bottom_rect.center)
        
        # Settings button
        self.btn_setting_rect = self.btn_setting.get_rect(topright=(settings.WIDTH - 40, 30))
        
        # Right Panel
        self.panel_right_rect = self.panel_right.get_rect(right=settings.WIDTH - 200, centery=settings.HEIGHT // 2)
        
        # Detail panels inside Right Panel
        padding_y = 40
        self.panel_detail_top_rect = self.panel_detail.get_rect(midtop=(self.panel_right_rect.centerx, self.panel_right_rect.top + padding_y+10))
        
        self.panel_detail_bottom_rect = self.panel_detail.get_rect(midbottom=(self.panel_right_rect.centerx, self.panel_right_rect.bottom - padding_y))
        
        # Small icons inside detail panels
        self.small_icon1_rect = self.small_icon_human.get_rect(topleft=(self.panel_detail_top_rect.left , self.panel_detail_top_rect.top - 40))

        self.small_icon2_rect = self.small_icon_human_2.get_rect(topleft=(self.panel_detail_bottom_rect.left , self.panel_detail_bottom_rect.top - 40))
        
        # Bottom Buttons
        self.btn_play_again_rect = self.btn_play_again.get_rect(bottomright=(self.panel_right_rect.right - 20, settings.HEIGHT - 40))
        self.btn_undo_rect = self.btn_undo.get_rect(bottomright=(self.btn_play_again_rect.left , settings.HEIGHT - 40))
        self.btn_surrender_rect = self.btn_surrender.get_rect(bottomright=(self.btn_undo_rect.left , settings.HEIGHT - 40))

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        
        # Top Player
        self.screen.blit(self.icon_human, self.icon_human_rect)
        self.screen.blit(self.name1_label, self.name1_rect)
        self.screen.blit(self.slide_time, self.slide_time_top_rect)
        self.screen.blit(self.time1_label, self.time1_rect)
        
        # Bottom Player
        self.screen.blit(self.icon_human_2, self.icon_human_2_rect)
        self.screen.blit(self.name2_label, self.name2_rect)
        self.screen.blit(self.slide_time, self.slide_time_bottom_rect)
        self.screen.blit(self.time2_label, self.time2_rect)
        
        # Settings
        self.screen.blit(self.btn_setting, self.btn_setting_rect)
        
        # Right Panel
        self.screen.blit(self.panel_right, self.panel_right_rect)
        
        # Detail Top
        self.screen.blit(self.panel_detail, self.panel_detail_top_rect)
        self.screen.blit(self.small_icon_human, self.small_icon1_rect)
        
        # Detail Bottom
        self.screen.blit(self.panel_detail, self.panel_detail_bottom_rect)
        self.screen.blit(self.small_icon_human_2, self.small_icon2_rect)
        
        # Bottom Buttons
        self.screen.blit(self.btn_surrender, self.btn_surrender_rect)
        self.screen.blit(self.btn_undo, self.btn_undo_rect)
        self.screen.blit(self.btn_play_again, self.btn_play_again_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.btn_setting_rect.collidepoint(mouse_pos):
                    print("Setting button clicked")
                elif self.btn_surrender_rect.collidepoint(mouse_pos):
                    print("Surrender button clicked")
                elif self.btn_undo_rect.collidepoint(mouse_pos):
                    print("Undo button clicked")
                elif self.btn_play_again_rect.collidepoint(mouse_pos):
                    print("Play again button clicked")

    