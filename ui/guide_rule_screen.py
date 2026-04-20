import os
import pygame
from config import settings
from services.sound_manager import SoundManager


class GuideRuleScreen:
    def __init__(self, screen):
        self.screen = screen
        self.sound_manager = SoundManager()

        self.font_title = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_text = pygame.font.SysFont("Segoe UI", 24)
        self.font_button = pygame.font.SysFont("Segoe UI", 28, bold=True)

        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, "bg.png")).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))

        self.panel_rect = pygame.Rect(40, 25, 1840, 1030)
        self.text_rect = pygame.Rect(90, 120, 1720, 790)
        self.back_rect = pygame.Rect(0, 0, 210, 62)
        self.back_rect.bottomright = (self.panel_rect.right - 35, self.panel_rect.bottom - 25)

        self.panel_fill = (220, 235, 246, 238)
        self.panel_border = (8, 43, 74)
        self.button_fill = (35, 125, 173)
        self.button_hover = (47, 142, 193)
        self.text_color = (20, 20, 20)
        self.title_color = (248, 248, 248)
        self.shadow_color = (30, 30, 30)

        self.rule_lines = [
            "1. Cờ Tư lệnh chơi trên 11 cột x 12 hàng, quân đứng trên các giao điểm.",
            "2. Mỗi bên có 19 quân gồm 11 loại: Tư lệnh, Bộ binh, Xe tăng, Dân quân, Công binh,",
            "   Pháo binh, Cao xạ, Tên lửa, Không quân, Hải quân và Sở chỉ huy.",
            "3. Mục tiêu trong luật gốc là bắt Tư lệnh đối phương hoặc làm đối thủ mất một nhóm quân chiến lược.",
            "4. Trong bản game hiện tại, hai bên đi lần lượt và bên đỏ đi trước.",
            "5. Bàn cờ có địa hình đất liền, biển, sông và đoạn ngầm; mỗi loại quân chịu giới hạn khác nhau.",
            "6. Bộ binh, Công binh, Cao xạ: đi thẳng 1 ô. Dân quân: đi 1 ô cả thẳng lẫn chéo.",
            "7. Xe tăng: đi thẳng 1-2 ô. Pháo binh: đi hoặc tấn công trong tầm 1-3 ô theo thẳng hoặc chéo.",
            "8. Không quân: đi 1-4 ô theo thẳng hoặc chéo và có thể bay vượt vật cản.",
            "9. Hải quân: chỉ hoạt động tốt trong khu vực nước. Tư lệnh đi thẳng xa nhưng chỉ ăn ở ô kề ngay.",
            "10. Sở chỉ huy là vị trí chiến lược quan trọng, liên quan trực tiếp đến điều kiện thắng trong luật đầy đủ.",
            "11. Luật đầy đủ còn có phòng không, quân anh hùng, xếp chồng quân, bung quân và nhiều cơ chế đặc biệt khác.",
            "12. Phần Guide này đang ưu tiên giúp người chơi nắm nhanh luật nền tảng để vào chơi trước.",
        ]

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

        self._draw_text_shadow("RULES GUIDE", self.font_title, self.title_color, (self.panel_rect.centerx, 72))

        y = self.text_rect.top
        for line in self.rule_lines:
            surf = self.font_text.render(line, True, self.text_color)
            self.screen.blit(surf, (self.text_rect.left, y))
            y += 52

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