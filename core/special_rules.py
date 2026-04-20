"""Auxiliary rule helpers kept in sync with the active move engine."""

from .board_layout import Zone, get_zone
from .move_rules import MISSILE_PATTERN, STRAIGHT_DIRS
from .piece import Color, PieceType


DEEP_RIVER_PIECES = {
    PieceType.TANK,
    PieceType.INFANTRY,
    PieceType.MILITIA,
    PieceType.COMMANDER,
    PieceType.ENGINEER,
}


def check_river_crossing(piece, end_pos):
    """Returns True when the piece may enter the destination zone."""
    tx, ty = end_pos
    zone = get_zone(tx, ty)
    if zone == Zone.FORD:
        return piece.type != PieceType.HEADQUARTERS
    if zone == Zone.RIVER:
        return piece.type in DEEP_RIVER_PIECES or piece.type == PieceType.AIRFORCE
    return True


def get_aa_zones(board, color_to_check_against):
    """Returns enemy anti-air coverage using the same geometry as move_rules."""
    danger_zones = set()
    for piece in board.pieces:
        if piece.color == color_to_check_against:
            continue
        px, py = piece.position
        if piece.type == PieceType.ANTIAIR or (
            piece.type == PieceType.NAVY and any(stacked.type == PieceType.ANTIAIR for stacked in piece.stacked_pieces)
        ):
            for dx, dy in STRAIGHT_DIRS:
                danger_zones.add((px + dx, py + dy))
        elif piece.type == PieceType.MISSILE:
            for dx, dy in MISSILE_PATTERN:
                danger_zones.add((px + dx, py + dy))
    return danger_zones


def apply_airforce_aa_interaction(piece, end_pos, board):
    """Destroys an aircraft that ends inside enemy AA coverage."""
    if piece.type != PieceType.AIRFORCE or piece.is_hero:
        return False

    if end_pos in get_aa_zones(board, piece.color):
        if piece in board.pieces:
            board.pieces.remove(piece)
        return True
    return False


def can_combine(carrier, passenger):
    """Checks stack legality for the supported carry mechanics."""
    if carrier.color != passenger.color:
        return False
    if carrier.type == PieceType.HEADQUARTERS:
        return passenger.type == PieceType.COMMANDER and not carrier.stacked_pieces
    if carrier.type == PieceType.ENGINEER and passenger.type in {
        PieceType.ARTILLERY,
        PieceType.ANTIAIR,
        PieceType.MISSILE,
    }:
        return not carrier.stacked_pieces
    return False


def apply_combination(carrier, passenger, board):
    if not can_combine(carrier, passenger):
        return False
    carrier.add_to_stack(passenger)
    if passenger in board.pieces:
        board.pieces.remove(passenger)
    return True


def split_combination(carrier, board, new_positions):
    """Detaches stacked pieces to the requested empty positions."""
    if not carrier.stacked_pieces:
        return False
    if len(new_positions) != len(carrier.stacked_pieces):
        return False

    detached = []
    for piece, pos in zip(list(carrier.stacked_pieces), new_positions):
        if board.get_piece_at(*pos):
            return False
        piece.move_to(pos)
        detached.append(piece)

    carrier.stacked_pieces.clear()
    board.pieces.extend(detached)
    return True


def get_commander_faceoff_blocked_dirs(piece, board):
    """Returns blocked orthogonal directions when commanders face each other."""
    if piece.type != PieceType.COMMANDER:
        return set()

    enemy_color = Color.BLUE if piece.color == Color.RED else Color.RED
    enemy_commander = None
    for current in board.pieces:
        if current.color == enemy_color and current.type == PieceType.COMMANDER:
            enemy_commander = current
            break
    if enemy_commander is None:
        return set()

    x, y = piece.position
    ex, ey = enemy_commander.position
    if x == ex:
        lower = min(y, ey) + 1
        upper = max(y, ey)
        occupied = [p for p in board.pieces if p.position[0] == x and lower <= p.position[1] < upper]
        return {(1, 0), (-1, 0)} if not occupied else set()
    if y == ey:
        lower = min(x, ex) + 1
        upper = max(x, ex)
        occupied = [p for p in board.pieces if p.position[1] == y and lower <= p.position[0] < upper]
        return {(0, 1), (0, -1)} if not occupied else set()
    return set()


def would_expose_commander_to_faceoff(board, piece, to_pos):
    """Simulates the move and checks whether the mover exposes its commander."""
    from_pos = piece.position
    piece.position = to_pos
    try:
        own_commander = piece if piece.type == PieceType.COMMANDER else None
        if own_commander is None:
            for current in board.pieces:
                if current.color == piece.color and current.type == PieceType.COMMANDER:
                    own_commander = current
                    break
        return bool(own_commander and get_commander_faceoff_blocked_dirs(own_commander, board))
    finally:
        piece.position = from_pos
