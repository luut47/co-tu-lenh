import os
import pygame
from config import settings


class GuideScreen:
    def __init__(self, screen):
        self.screen = screen

        self.font_title = pygame.font.SysFont("Segoe UI", 64, bold=True)
        self.font_button = pygame.font.SysFont("Segoe UI", 34, bold=True)

        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, "bg.png")).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))

        panel_w, panel_h = 980, 760
        self.panel_rect = pygame.Rect(
            (settings.WIDTH - panel_w) // 2,
            (settings.HEIGHT - panel_h) // 2,
            panel_w,
            panel_h
)

        btn_w, btn_h = 420, 86
        center_x = self.panel_rect.centerx
        start_y = self.panel_rect.top + 220
        gap = 115

        self.btn_piece_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.btn_piece_rect.center = (center_x, start_y)

        self.btn_rule_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.btn_rule_rect.center = (center_x, start_y + gap)

        self.btn_control_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.btn_control_rect.center = (center_x, start_y + gap * 2)

        self.btn_back_rect = pygame.Rect(0, 0, 220, 70)
        self.btn_back_rect.center = (center_x, start_y + gap * 3 + 30)

        self.panel_fill = (220, 235, 246, 235)
        self.panel_border = (8, 43, 74)
        self.button_fill = (35, 125, 173)
        self.button_hover = (47, 142, 193)
        self.text_color = (255, 255, 255)
        self.title_color = (248, 248, 248)
        self.shadow_color = (30, 30, 30)

        self.panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        self.panel_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(
            self.panel_surface,
            self.panel_fill,
            (0, 0, self.panel_rect.width, self.panel_rect.height),
            border_radius=28
        )
        pygame.draw.rect(
            self.panel_surface,
            self.panel_border,
            (0, 0, self.panel_rect.width, self.panel_rect.height),
            width=4,
            border_radius=28
        )

    def _draw_text_with_shadow(self, text, font, color, center):
        shadow = font.render(text, True, self.shadow_color)
        shadow_rect = shadow.get_rect(center=(center[0] + 3, center[1] + 3))
        self.screen.blit(shadow, shadow_rect)

        label = font.render(text, True, color)
        label_rect = label.get_rect(center=center)
        self.screen.blit(label, label_rect)

    def _draw_button(self, rect, text, mouse_pos):
        color = self.button_hover if rect.collidepoint(mouse_pos) else self.button_fill
        pygame.draw.rect(self.screen, color, rect, border_radius=18)
        pygame.draw.rect(self.screen, self.panel_border, rect, width=3, border_radius=18)
        self._draw_text_with_shadow(text, self.font_button, self.text_color, rect.center)

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.panel_surface, self.panel_rect.topleft)

        self._draw_text_with_shadow(
            "GUIDE",
            self.font_title,
            self.title_color,
            (self.panel_rect.centerx, self.panel_rect.top + 95)
        )

        mouse_pos = pygame.mouse.get_pos()
        self._draw_button(self.btn_piece_rect, "Pieces Guide", mouse_pos)
        self._draw_button(self.btn_rule_rect, "Rules Guide", mouse_pos)
        self._draw_button(self.btn_control_rect, "Control Guide", mouse_pos)
        self._draw_button(self.btn_back_rect, "Back", mouse_pos)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.btn_piece_rect.collidepoint(mouse_pos):
                from ui.guide_piece_screen import GuidePieceScreen
                return GuidePieceScreen(self.screen)

            elif self.btn_rule_rect.collidepoint(mouse_pos):
                from ui.guide_rule_screen import GuideRuleScreen
                return GuideRuleScreen(self.screen)

            elif self.btn_control_rect.collidepoint(mouse_pos):
                from ui.guide_control_screen import GuideControlScreen
                return GuideControlScreen(self.screen)

            elif self.btn_back_rect.collidepoint(mouse_pos):
                from ui.home_screen import HomeScreen
                return HomeScreen(self.screen)

        return None