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
    Returns a list of dicts: {'to': (tx, ty), 'type': MoveType.MOVE}
    Only checks for physical movement capability, not attacks.
    """
    moves = []
    x, y = piece.position

    def can_move_to(tx, ty):
        if tx < 0 or tx >= COLS or ty < 0 or ty >= ROWS:
            return False
            
        p = board.get_piece_at(tx, ty)
        if p:
            return False # Blocked by any piece for pure movement
            
        return True

    dirs_straight = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    dirs_diag = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    dirs_all = dirs_straight + dirs_diag

    # 1. Infantry, Engineer, AntiAir
    if piece.type in [PieceType.INFANTRY, PieceType.ENGINEER, PieceType.ANTIAIR]:
        for dx, dy in dirs_straight:
            tx, ty = x + dx, y + dy
            if can_move_to(tx, ty):
                moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # 2. Militia
    elif piece.type == PieceType.MILITIA:
        for dx, dy in dirs_all:
            tx, ty = x + dx, y + dy
            if can_move_to(tx, ty):
                moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # 3. Tank
    elif piece.type == PieceType.TANK:
        for dx, dy in dirs_straight:
            for i in range(1, 3):
                tx, ty = x + dx * i, y + dy * i
                if not can_move_to(tx, ty):
                    break
                moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # 4. Artillery
    elif piece.type == PieceType.ARTILLERY:
        for dx, dy in dirs_straight:
            for i in range(1, 4):
                tx, ty = x + dx * i, y + dy * i
                if not can_move_to(tx, ty):
                    break
                moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # 5. Missile (Assume 1-2 steps)
    elif piece.type == PieceType.MISSILE:
        for dx, dy in dirs_straight:
            for i in range(1, 3):
                tx, ty = x + dx * i, y + dy * i
                if not can_move_to(tx, ty):
                    break
                moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # 6. Air Force (Ignores obstacles, 1-4 steps)
    elif piece.type == PieceType.AIRFORCE:
        for dx, dy in dirs_all:
            for i in range(1, 5):
                tx, ty = x + dx * i, y + dy * i
                if tx < 0 or tx >= COLS or ty < 0 or ty >= ROWS:
                    continue
                p = board.get_piece_at(tx, ty)
                if not p:
                    moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # 7. Navy (1-4 steps straight, only on Sea)
    elif piece.type == PieceType.NAVY:
        from .board_layout import SEA_COLS_LEFT, RIVER_ROWS
        for dx, dy in dirs_straight:
            for i in range(1, 5):
                tx, ty = x + dx * i, y + dy * i
                if not can_move_to(tx, ty):
                    break
                zone = get_zone(tx, ty)
                # Navy can move on Sea columns (x in 0,1) at any row
                if zone == Zone.SEA:
                    moves.append({'to': (tx, ty), 'type': MoveType.MOVE})
                # Navy can move across the entire river row (y=5)
                elif ty in RIVER_ROWS:
                    moves.append({'to': (tx, ty), 'type': MoveType.MOVE})



    # 8. Commander (unlimited straight)
    elif piece.type == PieceType.COMMANDER:
        for dx, dy in dirs_straight:
            for i in range(1, max(COLS, ROWS)):
                tx, ty = x + dx * i, y + dy * i
                if not can_move_to(tx, ty):
                    break
                moves.append({'to': (tx, ty), 'type': MoveType.MOVE})

    # Post-filter
    from .board_layout import SEA_COLS_LEFT
    final_moves = []
    for m in moves:
        tx, ty = m['to']
        zone = get_zone(tx, ty)

        # AirForce cannot land on Sea
        if piece.type == PieceType.AIRFORCE and zone == Zone.SEA:
            continue

        # Non-Navy cannot move onto Sea
        if zone == Zone.SEA and piece.type not in [PieceType.NAVY]:
            continue

        # Non-Navy (and non-AirForce) cannot enter River unless allowed by river-crossing rules
        # Navy is already allowed in sea-column river cells (handled above in Navy block)
        # Other pieces' river access is handled by check_river_crossing in board.py

        final_moves.append(m)

    return final_moves

