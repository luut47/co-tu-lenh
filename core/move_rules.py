from enum import Enum
from .piece import PieceType, Color
from .board_layout import get_zone, Zone, COLS, ROWS

class MoveType(Enum):
    MOVE = "MOVE"
    CAPTURE = "CAPTURE"
    COMBINE = "COMBINE"
    DEPLOY = "DEPLOY"
    SPECIAL = "SPECIAL"

def get_valid_moves(piece, board):
    """
    Returns a list of dictionaries:
    [{'type': MoveType, 'to': (x, y), 'extra_data': None}]
    """
    moves = []
    x, y = piece.position

    def add_move(tx, ty):
        if tx < 0 or tx >= COLS or ty < 0 or ty >= ROWS:
            return False
        
        target_piece = board.get_piece_at(tx, ty)
        if target_piece:
            if target_piece.color != piece.color:
                # Capture
                moves.append({'type': MoveType.CAPTURE, 'to': (tx, ty), 'extra_data': None})
            else:
                # Combine or blocked
                # Simplification: blocked for now, except for combine logic handled elsewhere
                pass
            return False # Blocked
        else:
            moves.append({'type': MoveType.MOVE, 'to': (tx, ty), 'extra_data': None})
            return True # Path clear

    dirs_straight = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dirs_diag = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs_all = dirs_straight + dirs_diag

    # Infantry, Engineer, AntiAir: 1 step straight
    if piece.type in [PieceType.INFANTRY, PieceType.ENGINEER, PieceType.ANTIAIR]:
        for dx, dy in dirs_straight:
            add_move(x + dx, y + dy)

    # Militia: 1 step straight + diagonal
    elif piece.type == PieceType.MILITIA:
        for dx, dy in dirs_all:
            add_move(x + dx, y + dy)

    # Tank: 1-2 steps straight
    elif piece.type == PieceType.TANK:
        for dx, dy in dirs_straight:
            for i in range(1, 3):
                if not add_move(x + dx * i, y + dy * i):
                    break

    # Commander: unlimited straight move, but capture 1 block
    elif piece.type == PieceType.COMMANDER:
        for dx, dy in dirs_straight:
            for i in range(1, max(COLS, ROWS)):
                tx, ty = x + dx * i, y + dy * i
                if tx < 0 or tx >= COLS or ty < 0 or ty >= ROWS:
                    break
                target_piece = board.get_piece_at(tx, ty)
                if target_piece:
                    if target_piece.color != piece.color and i == 1:
                        # Capture only adjacent
                        moves.append({'type': MoveType.CAPTURE, 'to': (tx, ty), 'extra_data': None})
                    break
                else:
                    moves.append({'type': MoveType.MOVE, 'to': (tx, ty), 'extra_data': None})

    # Artillery: 1-3 steps straight + diag. Can jump when capturing?
    # Simple implementation for now: 1-3 steps.
    elif piece.type == PieceType.ARTILLERY:
        for dx, dy in dirs_all:
            for i in range(1, 4):
                if not add_move(x + dx * i, y + dy * i):
                    break
                    
    # AirForce: 1-4 steps, ignores obstacles
    elif piece.type == PieceType.AIRFORCE:
        for dx, dy in dirs_all:
            for i in range(1, 5):
                tx, ty = x + dx * i, y + dy * i
                if tx < 0 or tx >= COLS or ty < 0 or ty >= ROWS:
                    continue
                target_piece = board.get_piece_at(tx, ty)
                if target_piece:
                    if target_piece.color != piece.color:
                        moves.append({'type': MoveType.CAPTURE, 'to': (tx, ty), 'extra_data': None})
                else:
                    moves.append({'type': MoveType.MOVE, 'to': (tx, ty), 'extra_data': None})

    # Navy: only on SEA
    elif piece.type == PieceType.NAVY:
        for dx, dy in dirs_all:
            tx, ty = x + dx, y + dy
            if get_zone(tx, ty) == Zone.SEA:
                add_move(tx, ty)

    # Filter out invalid moves (e.g., non-Navy on Sea without crossing, or Land pieces on Sea)
    # This is a simplification. Actual Co Tu Lenh rules are more complex.
    final_moves = []
    for m in moves:
        tx, ty = m['to']
        zone = get_zone(tx, ty)
        if piece.type != PieceType.NAVY and zone == Zone.SEA:
            # Only Navy or Airforce can be on Sea. Sometimes Engineer can?
            if piece.type != PieceType.AIRFORCE:
                continue
        final_moves.append(m)

    return final_moves
