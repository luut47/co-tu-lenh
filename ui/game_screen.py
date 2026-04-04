import math
import pygame
from config.constants import (
    WIDTH,
    HEIGHT,
    BOARD_X,
    BOARD_Y,
    BOARD_PIXEL_WIDTH,
    BOARD_PIXEL_HEIGHT,
    TOP_PLAYER_Y,
    BOTTOM_PLAYER_Y,
    TOP_PLAYER_ICON_X,
    BOTTOM_PLAYER_ICON_X,
    PLAYER_NAME_X,
    TOP_TIMER_X,
    BOTTOM_TIMER_X,
    TOP_RIGHT_ICON_X,
    TOP_RIGHT_ICON_Y,
    BG_TOP,
    BG_BOTTOM,
    MID_BAND_COLOR,
    MID_LINE_COLOR,
    BOARD_CARD_COLOR,
    WHITE,
    TEXT_COLOR,
    BLUE_COLOR,
    RED_COLOR,
    SIDEBAR_DARK,
)
from core.mock_data import mock_pieces
from ui.board_view import BoardView
from ui.sidebar import Sidebar


class GameScreen:
    def __init__(self, screen):
        self.screen = screen
        self.board_view = BoardView(mock_pieces, show_pieces=False)
        self.sidebar = Sidebar()
        self.name_font = pygame.font.SysFont("Times New Roman", 24)
        self.timer_font = pygame.font.SysFont("Times New Roman", 22)

    def _draw_gradient_background(self):
        for y in range(HEIGHT):
            t = y / max(HEIGHT - 1, 1)
            color = (
                int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t),
                int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t),
                int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t),
            )
            pygame.draw.line(self.screen, color, (0, y), (WIDTH, y))

        band_rect = pygame.Rect(0, HEIGHT // 2 - 28, WIDTH, 56)
        band = pygame.Surface((band_rect.w, band_rect.h), pygame.SRCALPHA)
        band.fill((*MID_BAND_COLOR, 55))
        self.screen.blit(band, band_rect.topleft)
        pygame.draw.line(self.screen, MID_LINE_COLOR, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), 2)

    def _draw_face(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x, y), 24)
        pygame.draw.circle(self.screen, SIDEBAR_DARK, (x - 7, y - 6), 2)
        pygame.draw.circle(self.screen, SIDEBAR_DARK, (x + 7, y - 6), 2)
        pygame.draw.arc(self.screen, SIDEBAR_DARK, (x - 12, y - 2, 24, 14), 0.2, 2.95, 2)
        pygame.draw.circle(self.screen, SIDEBAR_DARK, (x, y), 24, 2)

    def _draw_settings_icon(self):
        x, y = TOP_RIGHT_ICON_X, TOP_RIGHT_ICON_Y
        button_color = (0, 103, 151)
        gear_color = (208, 214, 220)

        pygame.draw.circle(self.screen, button_color, (x, y), 26)
        pygame.draw.circle(self.screen, SIDEBAR_DARK, (x, y), 26, 2)

        for index in range(8):
            angle = math.radians(index * 45)
            x1 = x + int(math.cos(angle) * 10)
            y1 = y + int(math.sin(angle) * 10)
            x2 = x + int(math.cos(angle) * 17)
            y2 = y + int(math.sin(angle) * 17)
            pygame.draw.line(self.screen, gear_color, (x1, y1), (x2, y2), 4)
            pygame.draw.line(self.screen, SIDEBAR_DARK, (x1, y1), (x2, y2), 1)

        pygame.draw.circle(self.screen, gear_color, (x, y), 10)
        pygame.draw.circle(self.screen, SIDEBAR_DARK, (x, y), 10, 2)
        pygame.draw.circle(self.screen, button_color, (x, y), 4)
        pygame.draw.circle(self.screen, SIDEBAR_DARK, (x, y), 4, 1)

    def _draw_timer(self, x, y, text="00:00"):
        points = [
            (x, y),
            (x + 230, y),
            (x + 246, y + 16),
            (x + 230, y + 32),
            (x, y + 32),
        ]
        pygame.draw.polygon(self.screen, (157, 209, 233), points)
        pygame.draw.polygon(self.screen, SIDEBAR_DARK, points, 2)
        label = self.timer_font.render(text, True, TEXT_COLOR)
        rect = label.get_rect(center=(x + 120, y + 16))
        self.screen.blit(label, rect)

    def _draw_player_bars(self):
        self._draw_face(TOP_PLAYER_ICON_X, TOP_PLAYER_Y, (78, 134, 165))
        self._draw_face(BOTTOM_PLAYER_ICON_X , BOTTOM_PLAYER_Y + 30, RED_COLOR)

        top_name = self.name_font.render("Name", True, TEXT_COLOR)
        bottom_name = self.name_font.render("Name", True, TEXT_COLOR)
        self.screen.blit(top_name, (PLAYER_NAME_X, TOP_PLAYER_Y - 15))
        self.screen.blit(bottom_name, (PLAYER_NAME_X, BOTTOM_PLAYER_Y + 16))

        self._draw_timer(TOP_TIMER_X, TOP_PLAYER_Y - 20)
        self._draw_timer(BOTTOM_TIMER_X, BOTTOM_PLAYER_Y + 15)
        self._draw_settings_icon()

    def _draw_board_card(self):
        card_rect = pygame.Rect(120, 70, 643, 630)
        pygame.draw.rect(self.screen, BOARD_CARD_COLOR, card_rect)

    def draw(self):
        self._draw_gradient_background()
        self._draw_board_card()
        self._draw_player_bars()
        self.board_view.draw(self.screen)
        self.sidebar.draw(self.screen)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cell = self.board_view.handle_click(event.pos)
            if cell:
                row, col = cell
                self.sidebar.update_selected(row, col)

        if self.sidebar.surrender_button.is_click(event):
            self.sidebar.current_turn = "red" if self.sidebar.current_turn == "blue" else "blue"

        if self.sidebar.replay_button.is_click(event):
            self.board_view.selected_cell = None
            self.sidebar.reset()
