import math
import pygame
from config.constants import (
    BOARD_ROWS,
    BOARD_COLS,
    CELL_SIZE,
    BOARD_X,
    BOARD_Y,
    BOARD_BG_COLOR,
    BOARD_BORDER_COLOR,
    GRID_COLOR,
    WATER_COLOR,
    MARK_COLOR,
    BUSH_COLOR,
    COORD_COLOR,
    HIGHLIGHT_COLOR,
    BLUE_COLOR,
    RED_COLOR,
    WHITE,
)


class BoardView:
    def __init__(self, pieces=None, show_pieces=False):
        self.pieces = pieces or []
        self.show_pieces = show_pieces
        self.selected_cell = None
        self.coord_font = pygame.font.SysFont("Times New Roman", 16, bold=True)
        self.rank_font = pygame.font.SysFont("Times New Roman", 18, bold=True)

    def _cell_rect(self, row, col, row_span=1, col_span=1):
        return pygame.Rect(
            BOARD_X + col * CELL_SIZE,
            BOARD_Y + row * CELL_SIZE,
            col_span * CELL_SIZE,
            row_span * CELL_SIZE,
        )

    def _draw_board_base(self, screen):
        board_rect = pygame.Rect(
            BOARD_X,
            BOARD_Y,
            BOARD_COLS * CELL_SIZE,
            BOARD_ROWS * CELL_SIZE,
        )
        pygame.draw.rect(screen, BOARD_BG_COLOR, board_rect)
        pygame.draw.rect(screen, WATER_COLOR, self._cell_rect(0, 0, BOARD_ROWS, 2))
        pygame.draw.rect(screen, WATER_COLOR, self._cell_rect(5, 0, 1, BOARD_COLS))
        pygame.draw.rect(screen, BOARD_BORDER_COLOR, board_rect, 3)

    def _draw_grid(self, screen):
        for col in range(BOARD_COLS + 1):
            x = BOARD_X + col * CELL_SIZE
            pygame.draw.line(
                screen,
                GRID_COLOR,
                (x, BOARD_Y),
                (x, BOARD_Y + BOARD_ROWS * CELL_SIZE),
                2,
            )

        for row in range(BOARD_ROWS + 1):
            y = BOARD_Y + row * CELL_SIZE
            pygame.draw.line(
                screen,
                GRID_COLOR,
                (BOARD_X, y),
                (BOARD_X + BOARD_COLS * CELL_SIZE, y),
                2,
            )

    def _draw_ellipse_zone(self, screen, row, col, row_span, col_span):
        rect = self._cell_rect(row, col, row_span, col_span)
        pygame.draw.ellipse(screen, MARK_COLOR, rect, 1)

    def _draw_bush(self, screen, col, row):
        cx = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
        cy = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2
        strokes = [
            (-12, -10, -9, -19),
            (-9, 0, -12, -10),
            (-8, 11, -10, 1),
            (-2, -12, -1, -21),
            (4, -4, 2, -15),
            (8, 9, 5, -1),
            (12, -6, 10, -16),
        ]
        for x1, y1, x2, y2 in strokes:
            pygame.draw.line(screen, BUSH_COLOR, (cx + x1, cy + y1), (cx + x2, cy + y2), 2)

    def _draw_marks(self, screen):
        zones = [
            (0, 0, 2, 2),
            (1, 0, 2, 3),
            (1, 2, 2, 3),
            (0, 4, 4, 4),
            (1, 6, 2, 3),
            (1, 7, 2, 3),
            (9, 0, 2, 2),
            (7, 0, 2, 3),
            (7, 2, 2, 3),
            (7, 4, 4, 4),
            (7, 6, 2, 3),
            (7, 7, 2, 3),
        ]
        # for zone in zones:
        #     self._draw_ellipse_zone(screen, *zone)

        self._draw_bush(screen, 4, 5)
        self._draw_bush(screen, 6, 5)

    def _draw_coords(self, screen):
        for col in range(BOARD_COLS):
            text = self.coord_font.render(str(col + 1), True, COORD_COLOR)
            rect = text.get_rect(
                center=(BOARD_X + col * CELL_SIZE + CELL_SIZE // 2, BOARD_Y + BOARD_ROWS * CELL_SIZE + 13)
            )
            screen.blit(text, rect)

        for row in range(BOARD_ROWS + 1):
            value = BOARD_ROWS - row
            text = self.coord_font.render(str(value), True, COORD_COLOR)
            rect = text.get_rect(center=(BOARD_X - 15, BOARD_Y + row * CELL_SIZE))
            screen.blit(text, rect)

    def _draw_selection(self, screen):
        if not self.selected_cell:
            return
        row, col = self.selected_cell
        pygame.draw.rect(
            screen,
            HIGHLIGHT_COLOR,
            self._cell_rect(row, col),
            4,
            border_radius=10,
        )

    def _draw_piece(self, screen, row, col, team, rank):
        center_x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
        center_y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2
        team_color = RED_COLOR if team == "red" else BLUE_COLOR

        outer_r = CELL_SIZE // 2 - 5
        inner_r = outer_r - 4
        ring_r = outer_r - 1

        pygame.draw.circle(screen, (232, 214, 176), (center_x, center_y), outer_r)
        pygame.draw.circle(screen, team_color, (center_x, center_y), inner_r)
        pygame.draw.circle(screen, (244, 235, 210), (center_x, center_y), ring_r, 2)
        pygame.draw.circle(screen, (120, 91, 56), (center_x, center_y), outer_r, 1)

        label = self.rank_font.render(str(rank), True, WHITE)
        label_rect = label.get_rect(center=(center_x, center_y))
        screen.blit(label, label_rect)

    def draw_pieces(self, screen):
        if not self.show_pieces:
            return
        for piece in self.pieces:
            self._draw_piece(
                screen,
                piece["row"],
                piece["col"],
                piece["team"],
                piece.get("rank", "?"),
            )

    def draw(self, screen):
        self._draw_board_base(screen)
        self._draw_grid(screen)
        self._draw_marks(screen)
        self._draw_selection(screen)
        self._draw_coords(screen)
        self.draw_pieces(screen)

    def handle_click(self, pos):
        x, y = pos
        if not (
            BOARD_X <= x < BOARD_X + BOARD_COLS * CELL_SIZE
            and BOARD_Y <= y < BOARD_Y + BOARD_ROWS * CELL_SIZE
        ):
            return None

        col = (x - BOARD_X) // CELL_SIZE
        row = (y - BOARD_Y) // CELL_SIZE
        self.selected_cell = (row, col)
        return self.selected_cell
