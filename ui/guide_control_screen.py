import os
import pygame
from config import settings
from services.sound_manager import SoundManager


class GuideControlScreen:
    def __init__(self, screen):
        self.screen = screen

        self.font_title = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_text = pygame.font.SysFont("Segoe UI", 26)
        self.font_button = pygame.font.SysFont("Segoe UI", 28, bold=True)

        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, "bg.png")).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))

        self.panel_rect = pygame.Rect(40, 25, 1840, 1030)
        self.back_rect = pygame.Rect(0, 0, 210, 62)
        self.back_rect.bottomright = (self.panel_rect.right - 35, self.panel_rect.bottom - 25)

        self.panel_fill = (220, 235, 246, 238)
        self.panel_border = (8, 43, 74)
        self.button_fill = (35, 125, 173)
        self.button_hover = (47, 142, 193)
        self.text_color = (20, 20, 20)
        self.title_color = (248, 248, 248)
        self.shadow_color = (30, 30, 30)

        self.steps = [
            "1. Ở màn hình chính, bấm Human để chơi 2 người hoặc bấm Bot để chơi với máy.",
            "2. Khi vào bàn cờ, bấm vào quân của mình để chọn. Quân đang chọn sẽ được viền nổi bật.",
            "3. Các chấm màu xanh là nước đi hợp lệ; chấm đỏ là vị trí có thể tấn công.",
            "4. Bấm vào một vị trí hợp lệ để di chuyển quân.",
            "5. Nếu đang chọn quân mà bấm sang quân cùng màu đúng lượt, hệ thống sẽ đổi sang quân mới.",
            "6. Đi xong một nước thì lượt sẽ chuyển sang bên còn lại.",
            "7. Một số nút như Surrender, Undo, Play Again và Setting đang được hoàn thiện dần.",
            "8. Nếu muốn học nhanh quân cờ và luật chơi, quay lại Guide Menu để chọn mục tương ứng.",
        ]

        self.sound_manager = SoundManager()

        self.panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(self.panel_surface, self.panel_fill, (0, 0, self.panel_rect.width, self.panel_rect.height), border_radius=24)
        pygame.draw.rect(self.panel_surface, self.panel_border, (0, 0, self.panel_rect.width, self.panel_rect.height), width=4, border_radius=24)

    def _draw_text_shadow(self, text, font, color, center):
        shadow = font.render(text, True, self.shadow_color)
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
        label = font.render(text, True, color)
        self.screen.blit(label, label.get_rect(center=center))

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.panel_surface, self.panel_rect.topleft)

        self._draw_text_shadow("CONTROL GUIDE", self.font_title, self.title_color, (self.panel_rect.centerx, 72))

        y = 185
        for step in self.steps:
            pygame.draw.circle(self.screen, self.panel_border, (115, y + 13), 6)
            surf = self.font_text.render(step, True, self.text_color)
            self.screen.blit(surf, (140, y))
            y += 86

        mouse_pos = pygame.mouse.get_pos()
        color = self.button_hover if self.back_rect.collidepoint(mouse_pos) else self.button_fill
        pygame.draw.rect(self.screen, color, self.back_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.panel_border, self.back_rect, width=3, border_radius=16)
        self._draw_text_shadow("Back", self.font_button, (255, 255, 255), self.back_rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(event.pos):
                from ui.guide_screen import GuideScreen
                self.sound_manager.play_button()

                return GuideScreen(self.screen)
        return None