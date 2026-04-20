import os

import pygame

from config import settings
from .asset_cache import load_image
from .board_layout import COLS, ROWS, get_zone, Zone
from .move_rules import MoveType
from .piece import Color, PieceType


class BoardRenderer:
    _shared_piece_images = {}

    def __init__(self, rect):
        self.rect = rect
        self.cell_w = self.rect.width / (COLS - 1)
        self.cell_h = self.rect.height / (ROWS - 1)

        self.COLOR_LAND = (230, 230, 230)
        self.COLOR_SEA = (173, 216, 230)
        self.COLOR_RIVER = (100, 149, 237)
        self.COLOR_FORD = (240, 230, 140)
        self.COLOR_LINE = (50, 50, 50)
        self.COLOR_BRIDGE = (150, 120, 80)
        self.COLOR_HIGHLIGHT = (255, 255, 0)
        self.COLOR_LAST_MOVE = (45, 140, 255)
        self.COLOR_MOVE = (0, 255, 0)
        self.COLOR_ATTACK = (255, 0, 0)
        self.COLOR_COMBINE = (255, 165, 0)
        self.COLOR_DEPLOY = (186, 85, 211)
        self.COLOR_RETURN_ATTACK = (30, 90, 220)
        self.COLOR_AIRSPACE_CRASH = (255, 140, 0)

        piece_size = int(min(self.cell_w, self.cell_h) * 0.8)
        self.piece_images = self._get_piece_images(piece_size)

    @classmethod
    def _get_piece_images(cls, piece_size):
        if piece_size not in cls._shared_piece_images:
            cls._shared_piece_images[piece_size] = cls._load_images(piece_size)
        return cls._shared_piece_images[piece_size]

    @staticmethod
    def _load_images(piece_size):
        type_to_filename = {
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

        colors = {Color.RED: "red", Color.BLUE: "blue"}
        piece_images = {}
        for c_enum, c_str in colors.items():
            for t_enum, t_str in type_to_filename.items():
                filename = f"{c_str}_{t_str}.png"
                path = os.path.join(settings.ASSETS_DIR, "images", "items_broads", filename)
                if os.path.exists(path):
                    piece_images[(c_enum, t_enum)] = load_image(path, (piece_size, piece_size))
                else:
                    print(f"Warning: Missing asset {filename}")
        return piece_images

    def _get_pixel_pos(self, x, y):
        px = self.rect.left + x * self.cell_w
        py = self.rect.bottom - y * self.cell_h
        return px, py

    def get_board_pos(self, pixel_x, pixel_y):
        if not self.rect.collidepoint(pixel_x, pixel_y):
            return None

        x = int((pixel_x - self.rect.left + self.cell_w / 2) / self.cell_w)
        y_from_bottom = self.rect.bottom - pixel_y
        y = int((y_from_bottom + self.cell_h / 2) / self.cell_h)

        if 0 <= x < COLS and 0 <= y < ROWS:
            return x, y
        return None

    def draw(self, surface, board):
        pygame.draw.rect(surface, self.COLOR_LAND, self.rect)

        sea_rect = pygame.Rect(
            int(self.rect.left),
            int(self.rect.top),
            int(self.cell_w * 2),
            int(self.rect.height),
        )
        pygame.draw.rect(surface, self.COLOR_SEA, sea_rect)

        river_top_left = self._get_pixel_pos(2, 6)
        river_bottom_right = self._get_pixel_pos(COLS - 1, 5)
        river_rect = pygame.Rect(
            int(river_top_left[0]),
            int(river_top_left[1]),
            int(river_bottom_right[0] - river_top_left[0]),
            int(river_bottom_right[1] - river_top_left[1]),
        )
        pygame.draw.rect(surface, self.COLOR_RIVER, river_rect)

        self._draw_bridge_marker(surface, 5)
        self._draw_bridge_marker(surface, 7)

        for x in range(COLS):
            p1 = self._get_pixel_pos(x, 0)
            p2 = self._get_pixel_pos(x, ROWS - 1)
            pygame.draw.line(surface, self.COLOR_LINE, p1, p2, 2)

        for y in range(ROWS):
            p1 = self._get_pixel_pos(0, y)
            p2 = self._get_pixel_pos(COLS - 1, y)
            pygame.draw.line(surface, self.COLOR_LINE, p1, p2, 2)

        if board.selected_piece:
            px, py = self._get_pixel_pos(*board.selected_piece.position)
            pygame.draw.circle(surface, self.COLOR_HIGHLIGHT, (int(px), int(py)), int(self.cell_w * 0.45), 4)

        overlay_moves = []
        for move in board.valid_moves:
            mx, my = move["to"]
            target_piece = board.get_piece_at(mx, my)
            if target_piece is None:
                px, py = self._get_pixel_pos(mx, my)
                color = self._get_move_color(move["type"])
                pygame.draw.circle(surface, color, (int(px), int(py)), int(self.cell_w * 0.2))
            else:
                overlay_moves.append(move)

        for piece in board.pieces:
            px, py = self._get_pixel_pos(*piece.position)
            img = self.piece_images.get((piece.color, piece.type))
            if img:
                rect = img.get_rect(center=(int(px), int(py)))
                surface.blit(img, rect)
            else:
                c = (255, 0, 0) if piece.color == Color.RED else (0, 0, 255)
                pygame.draw.circle(surface, c, (int(px), int(py)), int(self.cell_w * 0.3))

            if piece.stacked_pieces:
                badge_radius = max(10, int(self.cell_w * 0.12))
                badge_center = (int(px + self.cell_w * 0.22), int(py - self.cell_h * 0.22))
                pygame.draw.circle(surface, (250, 250, 250), badge_center, badge_radius)
                pygame.draw.circle(surface, self.COLOR_LINE, badge_center, badge_radius, 2)

        for move in overlay_moves:
            mx, my = move["to"]
            px, py = self._get_pixel_pos(mx, my)
            color = self._get_move_color(move["type"])
            radius = int(self.cell_w * 0.38)
            width = max(4, int(self.cell_w * 0.06))
            pygame.draw.circle(surface, color, (int(px), int(py)), radius, width)
            if move["type"] == MoveType.AIRSTRIKE_RETURN:
                inner_radius = max(8, int(self.cell_w * 0.16))
                pygame.draw.circle(surface, self.COLOR_RETURN_ATTACK, (int(px), int(py)), inner_radius, 2)

        if board.last_move_to:
            px, py = self._get_pixel_pos(*board.last_move_to)
            pygame.draw.circle(surface, self.COLOR_LAST_MOVE, (int(px), int(py)), int(self.cell_w * 0.12))
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), int(self.cell_w * 0.12), 2)

    def _get_move_color(self, move_type):
        if move_type in {MoveType.CAPTURE_REPLACE, MoveType.CAPTURE_NO_REPLACE, MoveType.MUTUAL_DESTROY}:
            return self.COLOR_ATTACK
        if move_type == MoveType.AIRSTRIKE_RETURN:
            return self.COLOR_RETURN_ATTACK
        if move_type == MoveType.AIRSPACE_CRASH:
            return self.COLOR_AIRSPACE_CRASH
        if move_type == MoveType.COMBINE:
            return self.COLOR_COMBINE
        if move_type == MoveType.DEPLOY:
            return self.COLOR_DEPLOY
        return self.COLOR_MOVE

    def _draw_bridge_marker(self, surface, board_x):
        center_x = self.rect.left + board_x * self.cell_w
        center_y = self.rect.bottom - 5.5 * self.cell_h
        line_h = max(18, int(self.cell_h * 0.55))
        pygame.draw.line(
            surface,
            self.COLOR_LINE,
            (int(center_x), int(center_y - line_h / 2)),
            (int(center_x), int(center_y + line_h / 2)),
            3,
        )

        dash_w = max(4, int(self.cell_w * 0.08))
        dash_h = max(8, int(self.cell_h * 0.16))
        x_offsets = [-0.20, -0.11, 0.11, 0.20]
        y_offsets = [-0.28, -0.08, 0.12, 0.32]

        for x_factor in x_offsets:
            for y_factor in y_offsets:
                rect = pygame.Rect(
                    int(center_x + x_factor * self.cell_w - dash_w / 2),
                    int(center_y + y_factor * self.cell_h - dash_h / 2),
                    dash_w,
                    dash_h,
                )
                pygame.draw.rect(surface, self.COLOR_BRIDGE, rect, border_radius=2)
