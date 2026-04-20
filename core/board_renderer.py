import pygame
import os
from config import settings
from .board_layout import Zone, get_zone, COLS, ROWS
from .piece import PieceType, Color
from .move_rules import MoveType

class BoardRenderer:
    def __init__(self, rect):
        """
        rect: pygame.Rect defining where the board should be drawn.
        """
        self.rect = rect
        
        # Calculate cell size based on rect and board dimensions
        # The board is drawn on intersections.
        # COLS = 11 -> 10 horizontal segments
        # ROWS = 12 -> 11 vertical segments
        self.cell_w = self.rect.width / (COLS - 1)
        self.cell_h = self.rect.height / (ROWS - 1)
        
        # Colors
        self.COLOR_LAND = (230, 230, 230)
        self.COLOR_SEA = (173, 216, 230)
        self.COLOR_RIVER = (100, 149, 237)
        self.COLOR_FORD = (240, 230, 140)
        self.COLOR_LINE = (50, 50, 50)
        self.COLOR_HIGHLIGHT = (255, 255, 0)
        self.COLOR_MOVE = (0, 255, 0)
        self.COLOR_ATTACK = (255, 0, 0)
        
        self.piece_images = {}
        self._load_images()

    def _load_images(self):
        # Map PieceType to filename suffix
        type_to_filename = {
            PieceType.COMMANDER: "commander",
            PieceType.INFANTRY: "infantry",
            PieceType.TANK: "tank",
            PieceType.MILITIA: "militia",
            PieceType.ENGINEER: "engineer",
            PieceType.ARTILLERY: "allitery", # Note typo in asset name
            PieceType.ANTIAIR: "anti_aircraft_gun",
            PieceType.MISSILE: "rocket",
            PieceType.AIRFORCE: "airforce",
            PieceType.NAVY: "navy",
            PieceType.HEADQUARTERS: "headquaters" # Note typo in asset name
        }
        
        colors = {Color.RED: "red", Color.BLUE: "blue"}
        
        # Size for pieces (slightly smaller than cell size to fit)
        # We base size on the minimum of cell_w and cell_h
        piece_size = int(min(self.cell_w, self.cell_h) * 0.8)
        
        for c_enum, c_str in colors.items():
            for t_enum, t_str in type_to_filename.items():
                filename = f"{c_str}_{t_str}.png"
                path = os.path.join(settings.ASSETS_DIR, 'images', 'items_broads', filename)
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (piece_size, piece_size))
                    self.piece_images[(c_enum, t_enum)] = img
                else:
                    print(f"Warning: Missing asset {filename}")

    def _get_pixel_pos(self, x, y):
        # Top-left is (0,0) in pygame, but let's draw (0,0) at bottom-left?
        # Standard: Y=0 is bottom, Y=11 is top.
        # So pixel Y is inverted.
        px = self.rect.left + x * self.cell_w
        py = self.rect.bottom - y * self.cell_h
        return px, py

    def get_board_pos(self, pixel_x, pixel_y):
        # Convert pixel to nearest board intersection (x, y)
        if not self.rect.collidepoint(pixel_x, pixel_y):
            return None
            
        # Add half cell size before division to round to nearest intersection
        x = int((pixel_x - self.rect.left + self.cell_w / 2) / self.cell_w)
        
        # Invert Y logic
        y_from_bottom = self.rect.bottom - pixel_y
        y = int((y_from_bottom + self.cell_h / 2) / self.cell_h)
        
        if 0 <= x < COLS and 0 <= y < ROWS:
            return x, y
        return None

    def draw(self, surface, board):
        # 1. Draw Zones (Backgrounds for cells)
        # We draw background rectangles between intersections.
        for x in range(COLS - 1):
            for y in range(ROWS - 1):
                # The zone of a cell can be tricky since zones are on points.
                # We'll just color the grid squares based on the bottom-left point's zone
                # or a mix. Let's interpolate based on get_zone(x, y).
                z = get_zone(x, y)
                color = self.COLOR_LAND
                if z == Zone.SEA:
                    color = self.COLOR_SEA
                elif z == Zone.RIVER:
                    color = self.COLOR_RIVER
                elif z == Zone.FORD:
                    color = self.COLOR_FORD
                    
                px1, py1 = self._get_pixel_pos(x, y)
                # Note py1 is bottom, py2 is top (smaller value)
                rect = pygame.Rect(px1, py1 - self.cell_h, self.cell_w, self.cell_h)
                pygame.draw.rect(surface, color, rect)
                
        # 2. Draw Grid Lines
        for x in range(COLS):
            p1 = self._get_pixel_pos(x, 0)
            p2 = self._get_pixel_pos(x, ROWS - 1)
            pygame.draw.line(surface, self.COLOR_LINE, p1, p2, 2)
            
        for y in range(ROWS):
            p1 = self._get_pixel_pos(0, y)
            p2 = self._get_pixel_pos(COLS - 1, y)
            pygame.draw.line(surface, self.COLOR_LINE, p1, p2, 2)
            
        # 3. Draw Highlights
        if board.selected_piece:
            px, py = self._get_pixel_pos(*board.selected_piece.position)
            pygame.draw.circle(surface, self.COLOR_HIGHLIGHT, (int(px), int(py)), int(self.cell_w * 0.45), 4)
            
        for move in board.valid_moves:
            mx, my = move['to']
            px, py = self._get_pixel_pos(mx, my)
            color = self.COLOR_MOVE
            if move['type'] == MoveType.CAPTURE:
                color = self.COLOR_ATTACK
            elif move['type'] == MoveType.COMBINE:
                color = (255, 255, 0) # Yellow for combine
            pygame.draw.circle(surface, color, (int(px), int(py)), int(self.cell_w * 0.2))

        # 4. Draw Pieces
        for piece in board.pieces:
            px, py = self._get_pixel_pos(*piece.position)
            img = self.piece_images.get((piece.color, piece.type))
            if img:
                rect = img.get_rect(center=(int(px), int(py)))
                surface.blit(img, rect)
            else:
                # Fallback: draw a colored circle
                c = (255, 0, 0) if piece.color == Color.RED else (0, 0, 255)
                pygame.draw.circle(surface, c, (int(px), int(py)), int(self.cell_w * 0.3))
