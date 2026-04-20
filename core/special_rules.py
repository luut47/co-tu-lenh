from .piece import PieceType, Color
from .board_layout import get_zone, Zone

def check_river_crossing(piece, end_pos):
    """
    Returns True if the piece is allowed to move to end_pos over/into the river.
    Returns False if blocked by deep water constraints.
    """
    tx, ty = end_pos
    zone = get_zone(tx, ty)
    
    # Deep water check
    if zone == Zone.RIVER:
        # Allowed to go into deep water:
        allowed_types = [PieceType.TANK, PieceType.INFANTRY, PieceType.MILITIA, PieceType.COMMANDER]
        if piece.type not in allowed_types:
            # But wait, Air Force can fly over it? Yes, air force doesn't care.
            if piece.type != PieceType.AIRFORCE:
                return False
                
    # Fords (Zone.FORD) are safe for everyone
    return True

def get_aa_zones(board, color_to_check_against):
    """
    Returns a set of (x, y) tuples that are covered by enemy AA and Missile.
    color_to_check_against is the color of the Air Force (we look for ENEMY AA).
    """
    danger_zones = set()
    for p in board.pieces:
        if p.color != color_to_check_against:
            px, py = p.position
            if p.type == PieceType.ANTIAIR:
                # Radius 1
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        danger_zones.add((px + dx, py + dy))
            elif p.type == PieceType.MISSILE:
                # Radius 2 (Chebyshev)
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        danger_zones.add((px + dx, py + dy))
    return danger_zones

def apply_airforce_aa_interaction(piece, end_pos, board):
    """
    Checks if Air Force lands in an AA zone. If so, destroys the Air Force.
    Returns True if destroyed.
    """
    if piece.type != PieceType.AIRFORCE:
        return False
        
    danger_zones = get_aa_zones(board, piece.color)
    if end_pos in danger_zones:
        # Destroyed!
        if piece in board.pieces:
            board.pieces.remove(piece)
        return True
    return False

def can_combine(carrier, passenger):
    """
    Checks if carrier can pick up passenger.
    """
    if carrier.color != passenger.color:
        return False
        
    valid_carriers = [PieceType.TANK, PieceType.AIRFORCE, PieceType.NAVY]
    valid_passengers = [PieceType.COMMANDER, PieceType.INFANTRY, PieceType.MILITIA]
    
    if carrier.type not in valid_carriers:
        return False
        
    if passenger.type not in valid_passengers:
        return False
        
    if len(carrier.stacked_pieces) >= 2: # Max 3 pieces total (1 carrier + 2 passengers)
        return False
        
    return True

def apply_combination(carrier, passenger, board):
    """
    Merges passenger into carrier.
    """
    if can_combine(carrier, passenger):
        carrier.stacked_pieces.append(passenger)
        board.pieces.remove(passenger)
        return True
    return False

def split_combination(carrier, board, new_positions):
    """
    Splits the stack. Not fully integrated into UI yet, but logic is here.
    """
    pass


def get_commander_faceoff_blocked_dirs(piece, board):
    """
    Returns a set of (dx, dy) directions that are BLOCKED for a commander
    when facing the enemy commander with no piece between them.
    Empty set = no restriction.
    """
    if piece.type != PieceType.COMMANDER:
        return set()

    x, y = piece.position
    enemy_color = Color.BLUE if piece.color == Color.RED else Color.RED

    enemy_cmdr = None
    for p in board.pieces:
        if p.color == enemy_color and p.type == PieceType.COMMANDER:
            enemy_cmdr = p
            break

    if enemy_cmdr is None:
        return set()

    ex, ey = enemy_cmdr.position

    # Same column: face-off along Y axis
    if x == ex:
        min_y = min(y, ey) + 1
        max_y = max(y, ey)
        pieces_between = [
            p for p in board.pieces
            if p.position[0] == x and min_y <= p.position[1] < max_y
        ]
        if not pieces_between:
            return {(1, 0), (-1, 0)}   # block left/right

    # Same row: face-off along X axis
    elif y == ey:
        min_x = min(x, ex) + 1
        max_x = max(x, ex)
        pieces_between = [
            p for p in board.pieces
            if p.position[1] == y and min_x <= p.position[0] < max_x
        ]
        if not pieces_between:
            return {(0, 1), (0, -1)}   # block up/down

    return set()


def would_expose_commander_to_faceoff(board, piece, to_pos):
    """
    PIN RULE: Returns True if moving `piece` to `to_pos` would create a
    commander face-off (own commander exposed to direct line-of-sight with
    the enemy commander).  The move is illegal when this returns True.
    """
    from_pos = piece.position
    piece.position = to_pos   # temporarily simulate

    my_cmdr = piece if piece.type == PieceType.COMMANDER else None
    if my_cmdr is None:
        for p in board.pieces:
            if p.color == piece.color and p.type == PieceType.COMMANDER:
                my_cmdr = p
                break

    result = False
    if my_cmdr is not None:
        blocked = get_commander_faceoff_blocked_dirs(my_cmdr, board)
        result = len(blocked) > 0

    piece.position = from_pos   # restore
    return result
