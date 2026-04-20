import pygame
from services.sound_manager import SoundManager

class SwapSidesDialog:
    def __init__(self, surface, font_name, width=500, height=300):
        self.surface = surface
        self.width = width
        self.height = height
        self.font_large = pygame.font.SysFont(font_name, 48, bold=True)
        self.font_medium = pygame.font.SysFont(font_name, 36)
        self.font_small = pygame.font.SysFont(font_name, 24)

        # Center dialog
        sw, sh = surface.get_size()
        self.rect = pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)

        # Buttons (Bottom)
        btn_w = 150
        btn_h = 50
        self.btn_yes = pygame.Rect(self.rect.centerx - btn_w - 20, self.rect.bottom - 80, btn_w, btn_h)
        self.btn_no = pygame.Rect(self.rect.centerx + 20, self.rect.bottom - 80, btn_w, btn_h)

        self.done = False
        self.result = False # True = swap, False = no swap
        self.sound_manager = SoundManager()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos
                
                
                # Actions
                if self.btn_yes.collidepoint(pos):
                    self.sound_manager.play_button()
                    self.result = True
                    self.done = True
                elif self.btn_no.collidepoint(pos):
                    self.sound_manager.play_button()
                    self.result = False
                    self.done = True

    def draw(self):
        # Draw overlay background
        overlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.surface.blit(overlay, (0, 0))

        # Draw dialog box
        pygame.draw.rect(self.surface, (240, 240, 240), self.rect, border_radius=15)
        pygame.draw.rect(self.surface, (100, 100, 100), self.rect, 3, border_radius=15)

        # Title
        title = self.font_large.render("ĐỔI BÊN?", True, (50, 50, 50))
        self.surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top + 50)))

        # Message
        msg = self.font_medium.render("2 bạn có muốn đổi bên không?", True, (50, 50, 50))
        self.surface.blit(msg, msg.get_rect(center=(self.rect.centerx, self.rect.centery - 20)))

        # Buttons
        self._draw_button(self.btn_yes, "Có", (76, 175, 80), (255, 255, 255))
        self._draw_button(self.btn_no, "Không", (244, 67, 54), (255, 255, 255))

    def _draw_button(self, rect, text, bg_color, text_color):
        pygame.draw.rect(self.surface, bg_color, rect, border_radius=8)
        lbl = self.font_medium.render(text, True, text_color)
        self.surface.blit(lbl, lbl.get_rect(center=rect.center))

    def reset(self):
        self.done = False
        self.result = False
