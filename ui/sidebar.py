import pygame
from config.constants import (
    SIDEBAR_X,
    SIDEBAR_Y,
    SIDEBAR_WIDTH,
    SIDEBAR_HEIGHT,
    SIDEBAR_COLOR,
    SIDEBAR_INNER_COLOR,
    SIDEBAR_OUTLINE,
    SIDEBAR_DARK,
    DASH_COLOR,
    BUTTON_BLUE,
    BUTTON_BLUE_EDGE,
    BUTTON_GRAY,
    BUTTON_GRAY_EDGE,
    TEXT_COLOR,
    WHITE,
    DISABLED_TEXT,
    RED_COLOR,
    BLUE_COLOR,
)
from ui.components.button import Button


class Sidebar:
    def __init__(self):
        self.label_font = pygame.font.SysFont("Times New Roman", 18, bold=True)
        self.box_title_font = pygame.font.SysFont("Times New Roman", 22, bold=False)
        self.button_font = pygame.font.SysFont("Times New Roman", 18, bold=True)

        self.surrender_button = Button(
            (SIDEBAR_X + 45, SIDEBAR_Y + SIDEBAR_HEIGHT + 18, 140, 42),
            "Đầu hàng",
            self.button_font,
            BUTTON_BLUE,
            BUTTON_BLUE_EDGE,
        )
        self.replay_button = Button(
            (SIDEBAR_X + 245, SIDEBAR_Y + SIDEBAR_HEIGHT + 18, 150, 42),
            "Mời chơi lại",
            self.button_font,
            BUTTON_GRAY,
            BUTTON_GRAY_EDGE,
            DISABLED_TEXT,
        )

        self.top_moves = []
        self.bottom_moves = []
        self.current_turn = "blue"
        self.selected_text = "Chưa chọn ô nào"

    def _draw_face(self, screen, x, y, color):
        pygame.draw.circle(screen, color, (x, y), 16)
        pygame.draw.circle(screen, SIDEBAR_DARK, (x, y), 2, 1)
        pygame.draw.circle(screen, SIDEBAR_DARK, (x - 5, y - 5), 2)
        pygame.draw.circle(screen, SIDEBAR_DARK, (x + 5, y - 5), 2)
        pygame.draw.arc(screen, SIDEBAR_DARK, (x - 7, y - 2, 16, 10), 0.2, 2.95, 2)
        pygame.draw.circle(screen, SIDEBAR_DARK, (x, y), 16, 2)

    def _draw_move_section(self, screen, *, face_color, title_y, box_y, items):
        self._draw_face(screen, SIDEBAR_X + 30, title_y + 18, face_color)

        pill_rect = pygame.Rect(SIDEBAR_X + 54, title_y + 3, 128, 34)
        pygame.draw.rect(screen, (83, 145, 180), pill_rect, border_radius=18)
        pygame.draw.rect(screen, SIDEBAR_DARK, pill_rect, 2, border_radius=18)
        title = self.box_title_font.render("Nước đi", True, WHITE)
        title_rect = title.get_rect(center=pill_rect.center)
        screen.blit(title, title_rect)

        outer = pygame.Rect(SIDEBAR_X + 12, box_y, SIDEBAR_WIDTH - 24, 190)
        pygame.draw.rect(screen, SIDEBAR_INNER_COLOR, outer, border_radius=32)
        pygame.draw.rect(screen, SIDEBAR_DARK, outer, 2, border_radius=32)

        if items:
            y = outer.y + 18
            for idx, move in enumerate(items[-6:]):
                line = self.label_font.render(f"{idx + 1}. {move}", True, WHITE)
                screen.blit(line, (outer.x + 20, y))
                y += 26
        else:
            empty = self.label_font.render("Chưa có nước đi", True, WHITE)
            info = self.label_font.render(self.selected_text, True, WHITE)
            screen.blit(empty, (outer.x + 20, outer.y + 22))
            screen.blit(info, (outer.x + 20, outer.y + 52))

    def draw(self, screen):
        panel_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        shadow = panel_rect.move(6, 8)
        shadow_surf = pygame.Surface((shadow.w, shadow.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 25), shadow_surf.get_rect(), border_radius=30)
        screen.blit(shadow_surf, shadow.topleft)

        pygame.draw.rect(screen, SIDEBAR_COLOR, panel_rect, border_radius=30)
        pygame.draw.rect(screen, SIDEBAR_OUTLINE, panel_rect, 3, border_radius=30)

        mid_y = SIDEBAR_Y + SIDEBAR_HEIGHT // 2 + 10
        for x in range(SIDEBAR_X - 20, SIDEBAR_X + SIDEBAR_WIDTH + 20, 12):
            pygame.draw.line(screen, DASH_COLOR, (x, mid_y), (x + 7, mid_y), 2)

        self._draw_move_section(
            screen,
            face_color=BLUE_COLOR,
            title_y=SIDEBAR_Y + 18,
            box_y=SIDEBAR_Y + 64,
            items=self.top_moves,
        )
        self._draw_move_section(
            screen,
            face_color=RED_COLOR,
            title_y=SIDEBAR_Y + 315,
            box_y=SIDEBAR_Y + 361,
            items=self.bottom_moves,
        )

        self.surrender_button.draw(screen)
        self.replay_button.draw(screen)

    def update_selected(self, row, col):
        self.selected_text = f"Ô đang chọn: ({row}, {col})"

    def record_move(self, row, col):
        move_text = f"({row}, {col})"
        if self.current_turn == "blue":
            self.top_moves.append(move_text)
            self.current_turn = "red"
        else:
            self.bottom_moves.append(move_text)
            self.current_turn = "blue"

    def reset(self):
        self.top_moves.clear()
        self.bottom_moves.clear()
        self.current_turn = "blue"
        self.selected_text = "Chưa chọn ô nào"
