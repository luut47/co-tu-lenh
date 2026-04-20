import os
import pygame
from config import settings
from core.piece import PieceType


class GuidePieceScreen:
    IMAGE_CACHE = None

    def __init__(self, screen):
        self.screen = screen

        self.font_title = pygame.font.SysFont("Segoe UI", 54, bold=True)
        self.font_header = pygame.font.SysFont("Segoe UI", 26, bold=True)
        self.font_name = pygame.font.SysFont("Segoe UI", 22, bold=True)
        self.font_desc = pygame.font.SysFont("Segoe UI", 20)
        self.font_button = pygame.font.SysFont("Segoe UI", 28, bold=True)
        self.font_note = pygame.font.SysFont("Segoe UI", 20)

        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, "bg.png")).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))

        self.panel_rect = pygame.Rect(40, 25, 1840, 1030)
        self.table_rect = pygame.Rect(70, 120, 1760, 800)
        self.back_rect = pygame.Rect(0, 0, 210, 62)
        self.back_rect.bottomright = (self.panel_rect.right - 35, self.panel_rect.bottom - 25)

        self.panel_fill = (220, 235, 246, 238)
        self.panel_border = (8, 43, 74)
        self.header_fill = (194, 176, 150)
        self.row_fill_a = (243, 248, 252)
        self.row_fill_b = (232, 241, 248)
        self.button_fill = (35, 125, 173)
        self.button_hover = (47, 142, 193)
        self.text_color = (20, 20, 20)
        self.title_color = (248, 248, 248)
        self.shadow_color = (30, 30, 30)

        self.left_col_w = 330
        self.header_h = 56
        self.row_h = 66
        self.image_size = 42

        self.piece_rows = [
            ("Tư lệnh", PieceType.COMMANDER, "Di chuyển thẳng nhiều ô nếu không bị chặn; chỉ ăn quân địch ở ô kề ngay phía trước hướng đi."),
            ("Bộ binh", PieceType.INFANTRY, "Đi thẳng 1 ô theo 4 hướng cơ bản. Đây là quân chiến đấu mặt đất cơ bản."),
            ("Xe tăng", PieceType.TANK, "Đi thẳng 1-2 ô. Dùng để đột phá và áp sát tuyến trước."),
            ("Dân quân", PieceType.MILITIA, "Đi 1 ô theo cả hướng thẳng lẫn chéo nên linh hoạt hơn bộ binh."),
            ("Công binh", PieceType.ENGINEER, "Đi thẳng 1 ô. Vai trò hỗ trợ cơ động và các luật đặc biệt về vượt địa hình."),
            ("Pháo binh", PieceType.ARTILLERY, "Đi hoặc tấn công trong tầm 1-3 ô theo thẳng hoặc chéo; bản hiện tại đang đơn giản hóa."),
            ("Cao xạ", PieceType.ANTIAIR, "Đi thẳng 1 ô. Trong luật đầy đủ còn có vai trò khống chế máy bay."),
            ("Tên lửa", PieceType.MISSILE, "Quân chiến lược phòng không và tầm xa trong luật gốc; bản hiện tại chưa bật đầy đủ kỹ năng đặc biệt."),
            ("Không quân", PieceType.AIRFORCE, "Đi 1-4 ô theo thẳng hoặc chéo và có thể bay vượt vật cản."),
            ("Hải quân", PieceType.NAVY, "Chỉ hoạt động ở khu biển trong bản hiện tại. Rất mạnh trong khu vực nước."),
            ("Sở chỉ huy", PieceType.HEADQUARTERS, "Mục tiêu chiến lược đặc biệt. Trong luật gốc liên quan trực tiếp đến điều kiện thắng."),
        ]

        self.images = self._get_cached_images()

        self.panel_surface = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        self.panel_surface.fill((0, 0, 0, 0))
        pygame.draw.rect(self.panel_surface, self.panel_fill, (0, 0, self.panel_rect.width, self.panel_rect.height), border_radius=24)
        pygame.draw.rect(self.panel_surface, self.panel_border, (0, 0, self.panel_rect.width, self.panel_rect.height), width=4, border_radius=24)

    def _type_to_filename(self, piece_type):
        mapping = {
            PieceType.COMMANDER: "commander",
            PieceType.INFANTRY: "infantry",
            PieceType.TANK: "tank",
            PieceType.MILITIA: "militia",
            PieceType.ENGINEER: "engineer",
            PieceType.ARTILLERY: "allitery",
            PieceType.ANTIAIR: "anti_aircraft_gun",
            PieceType.MISSILE: "rocket",
            PieceType.AIRFORCE: "airforce",
            PieceType.NAVY: "navy",
            PieceType.HEADQUARTERS: "headquaters",
        }
        return mapping[piece_type]

    def _get_cached_images(self):
        if GuidePieceScreen.IMAGE_CACHE is not None:
            return GuidePieceScreen.IMAGE_CACHE

        image_dir = os.path.join(settings.ASSETS_DIR, "images", "items_broads")
        cache = {}

        for _, piece_type, _ in self.piece_rows:
            filename = f"red_{self._type_to_filename(piece_type)}.png"
            path = os.path.join(image_dir, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.smoothscale(img, (self.image_size, self.image_size))
                cache[piece_type] = img

        GuidePieceScreen.IMAGE_CACHE = cache
        return cache

    def _draw_text_shadow(self, text, font, color, center):
        shadow = font.render(text, True, self.shadow_color)
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
        label = font.render(text, True, color)
        self.screen.blit(label, label.get_rect(center=center))

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""

        for word in words:
            test = word if current == "" else current + " " + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        return lines

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.panel_surface, self.panel_rect.topleft)

        self._draw_text_shadow("PIECES GUIDE", self.font_title, self.title_color, (self.panel_rect.centerx, 72))

        note = self.font_note.render("Cột 1 là ảnh quân cờ, cột 2 là tác dụng tóm tắt.", True, self.text_color)
        self.screen.blit(note, (78, 95))

        pygame.draw.rect(self.screen, self.header_fill, (self.table_rect.left, self.table_rect.top, self.table_rect.width, self.header_h), border_radius=12)
        pygame.draw.line(
            self.screen,
            self.panel_border,
            (self.table_rect.left + self.left_col_w, self.table_rect.top),
            (self.table_rect.left + self.left_col_w, self.table_rect.top + self.header_h + self.row_h * len(self.piece_rows)),
            2
        )

        self.screen.blit(self.font_header.render("Quân cờ", True, self.text_color), (self.table_rect.left + 28, self.table_rect.top + 12))
        self.screen.blit(self.font_header.render("Tác dụng / Cách di chuyển tóm tắt", True, self.text_color), (self.table_rect.left + self.left_col_w + 26, self.table_rect.top + 12))

        start_y = self.table_rect.top + self.header_h

        for i, (name, piece_type, desc) in enumerate(self.piece_rows):
            y = start_y + i * self.row_h
            row_rect = pygame.Rect(self.table_rect.left, y, self.table_rect.width, self.row_h)

            pygame.draw.rect(self.screen, self.row_fill_a if i % 2 == 0 else self.row_fill_b, row_rect)
            pygame.draw.rect(self.screen, self.panel_border, row_rect, 1)

            img = self.images.get(piece_type)
            if img:
                self.screen.blit(img, (self.table_rect.left + 20, y + 12))

            name_surface = self.font_name.render(name, True, self.text_color)
            self.screen.blit(name_surface, (self.table_rect.left + 78, y + 15))

            wrapped = self._wrap_text(desc, self.font_desc, self.table_rect.width - self.left_col_w - 40)
            text_y = y + 10
            for line in wrapped[:2]:
                line_surface = self.font_desc.render(line, True, self.text_color)
                self.screen.blit(line_surface, (self.table_rect.left + self.left_col_w + 18, text_y))
                text_y += 22

        mouse_pos = pygame.mouse.get_pos()
        back_color = self.button_hover if self.back_rect.collidepoint(mouse_pos) else self.button_fill
        pygame.draw.rect(self.screen, back_color, self.back_rect, border_radius=16)
        pygame.draw.rect(self.screen, self.panel_border, self.back_rect, width=3, border_radius=16)
        self._draw_text_shadow("Back", self.font_button, (255, 255, 255), self.back_rect.center)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(event.pos):
                from ui.guide_screen import GuideScreen
                return GuideScreen(self.screen)
        return None