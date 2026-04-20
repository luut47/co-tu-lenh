from .piece_factory import setup_default_pieces
from .piece import Color
from .move_rules import get_valid_moves, MoveType

class Board:
    def __init__(self):
        self.pieces = setup_default_pieces()
        self.current_turn = Color.RED
        self.selected_piece = None
        self.valid_moves = [] # List of available moves for selected piece
        
    def get_piece_at(self, x, y):
        for p in self.pieces:
            if p.position == (x, y):
                return p
        return None
        
    def select_piece(self, piece):
        if piece and piece.color == self.current_turn:
            self.selected_piece = piece
            self.valid_moves = get_valid_moves(piece, self)
        else:
            self.selected_piece = None
            self.valid_moves = []
            
    def unselect_piece(self):
        self.selected_piece = None
        self.valid_moves = []
        
    def move_piece(self, to_x, to_y):
        if not self.selected_piece:
            return False
            
        move_data = None
        for m in self.valid_moves:
            if m['to'] == (to_x, to_y):
                move_data = m
                break
                
        if not move_data:
            return False
            
        if move_data['type'] == MoveType.CAPTURE:
            target = self.get_piece_at(to_x, to_y)
            if target:
                self.pieces.remove(target)
                
        # Move the piece
        self.selected_piece.move_to((to_x, to_y))
        
        # Switch turn
        self.current_turn = Color.BLUE if self.current_turn == Color.RED else Color.RED
        
        # Clear selection
        self.unselect_piece()
        return True
