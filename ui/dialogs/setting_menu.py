import pygame
from config import settings


class SettingMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_open = False

        self.font_title = pygame.font.SysFont(settings.FONT_NAME, 24, bold=True)
        self.font_button = pygame.font.SysFont(settings.FONT_NAME, 20, bold=True)
        self.font_icon = pygame.font.SysFont("segoe ui symbol", 30, bold=True)

        self.color_panel = (46, 96, 128)
        self.color_border = (120, 190, 220)
        self.color_button = (64, 125, 160)
        self.color_button_hover = (84, 145, 180)
        self.color_text = (240, 248, 255)
        self.color_overlay = (0, 0, 0, 70)

        self.toggle_rect = pygame.Rect(28, 28, 58, 58)
        self.panel_rect = pygame.Rect(28, 98, 250, 220)

        self.btn_continue_rect = pygame.Rect(48, 142, 210, 42)
        self.btn_sound_rect = pygame.Rect(48, 194, 210, 42)
        self.btn_home_rect = pygame.Rect(48, 246, 210, 42)

    def draw(self, sound_on=True):
        mouse_pos = pygame.mouse.get_pos()

        self._draw_circle_button(
            self.toggle_rect,
            "⚙",
            hovered=self.toggle_rect.collidepoint(mouse_pos),
        )

        if not self.is_open:
            return

        overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
        overlay.fill(self.color_overlay)
        self.screen.blit(overlay, (0, 0))

        pygame.draw.rect(self.screen, self.color_panel, self.panel_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.color_border, self.panel_rect, width=3, border_radius=16)

        title = self.font_title.render("SETTING", True, self.color_text)
        self.screen.blit(title, title.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 28)))

        self._draw_button(
            self.btn_continue_rect,
            "CONTINUE",
            hovered=self.btn_continue_rect.collidepoint(mouse_pos),
        )

        sound_text = "SOUND: ON" if sound_on else "SOUND: OFF"
        self._draw_button(
            self.btn_sound_rect,
            sound_text,
            hovered=self.btn_sound_rect.collidepoint(mouse_pos),
        )

        self._draw_button(
            self.btn_home_rect,
            "HOME",
            hovered=self.btn_home_rect.collidepoint(mouse_pos),
        )

    def _draw_button(self, rect, text, hovered=False):
        color = self.color_button_hover if hovered else self.color_button
        pygame.draw.rect(self.screen, color, rect, border_radius=14)
        pygame.draw.rect(self.screen, self.color_border, rect, width=2, border_radius=14)

        label = self.font_button.render(text, True, self.color_text)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            if self.toggle_rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                return "toggle"

            if not self.is_open:
                return None

            if self.btn_continue_rect.collidepoint(mouse_pos):
                self.is_open = False
                return "continue"

            if self.btn_sound_rect.collidepoint(mouse_pos):
                return "sound"

            if self.btn_home_rect.collidepoint(mouse_pos):
                self.is_open = False
                return "home"

            if not self.panel_rect.collidepoint(mouse_pos):
                self.is_open = False

        return None

    def _draw_circle_button(self, rect, text, hovered=False):
        color = self.color_button_hover if hovered else self.color_button
        center = rect.center
        radius = rect.width // 2

        pygame.draw.circle(self.screen, color, center, radius)
        pygame.draw.circle(self.screen, self.color_border, center, radius, 3)

        label = self.font_icon.render(text, True, self.color_text)
        self.screen.blit(label, label.get_rect(center=center))
