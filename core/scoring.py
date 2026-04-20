"""Score calculation and win condition detection for Commander Chess."""

from .move_rules import MoveType, get_valid_moves
from .piece import Color, PieceType


PIECE_SCORES = {
    PieceType.INFANTRY: 10,
    PieceType.ENGINEER: 10,
    PieceType.ANTIAIR: 10,
    PieceType.MILITIA: 10,
    PieceType.TANK: 20,
    PieceType.MISSILE: 20,
    PieceType.ARTILLERY: 30,
    PieceType.AIRFORCE: 40,
    PieceType.NAVY: 80,
    PieceType.COMMANDER: 100,
    PieceType.HEADQUARTERS: 0,
}


class WinCondition:
    NONE = None
    COMMANDER_CAPTURED = "COMMANDER_CAPTURED"
    NO_MOVES_LEFT = "NO_MOVES_LEFT"
    TIME_UP = "TIME_UP"
    MARINE_DOMINANCE = "MARINE_DOMINANCE"
    AIR_DOMINANCE = "AIR_DOMINANCE"
    LAND_DOMINANCE = "LAND_DOMINANCE"
    COMMANDER_ISOLATED = "COMMANDER_ISOLATED"
    COMMANDER_TRAPPED = "COMMANDER_TRAPPED"
    RAID_WIN = "RAID_WIN"


WIN_BONUSES = {
    WinCondition.AIR_DOMINANCE: 100,
    WinCondition.MARINE_DOMINANCE: 100,
    WinCondition.LAND_DOMINANCE: 100,
    WinCondition.COMMANDER_CAPTURED: 200,
}


def get_piece_score(piece):
    """Returns the score value of a piece, including stacked passengers."""
    total = PIECE_SCORES.get(piece.type, 0)
    for passenger in piece.stacked_pieces:
        total += get_piece_score(passenger)
    return total


def check_win_conditions(board, score_red, score_blue, mode="standard"):
    """
    Returns (winner_color, condition, bonus_points) or (None, WinCondition.NONE, 0).
    The `mode` parameter is kept for compatibility with the existing board API.
    """
    del score_red, score_blue, mode

    red_pieces = [piece for piece in _iter_all_pieces(board.pieces) if piece.color == Color.RED]
    blue_pieces = [piece for piece in _iter_all_pieces(board.pieces) if piece.color == Color.BLUE]

    def count(pieces, piece_type):
        return sum(1 for piece in pieces if piece.type == piece_type)

    if not any(piece.type == PieceType.COMMANDER for piece in red_pieces):
        return Color.BLUE, WinCondition.COMMANDER_CAPTURED, WIN_BONUSES[WinCondition.COMMANDER_CAPTURED]
    if not any(piece.type == PieceType.COMMANDER for piece in blue_pieces):
        return Color.RED, WinCondition.COMMANDER_CAPTURED, WIN_BONUSES[WinCondition.COMMANDER_CAPTURED]

    init = board.initial_counts
    blue_navy_start = init.get((Color.BLUE, PieceType.NAVY), 0)
    red_navy_start = init.get((Color.RED, PieceType.NAVY), 0)
    if blue_navy_start >= 2 and count(blue_pieces, PieceType.NAVY) == 0:
        return Color.RED, WinCondition.MARINE_DOMINANCE, WIN_BONUSES[WinCondition.MARINE_DOMINANCE]
    if red_navy_start >= 2 and count(red_pieces, PieceType.NAVY) == 0:
        return Color.BLUE, WinCondition.MARINE_DOMINANCE, WIN_BONUSES[WinCondition.MARINE_DOMINANCE]

    blue_air_start = init.get((Color.BLUE, PieceType.AIRFORCE), 0)
    red_air_start = init.get((Color.RED, PieceType.AIRFORCE), 0)
    if blue_air_start >= 2 and count(blue_pieces, PieceType.AIRFORCE) == 0:
        return Color.RED, WinCondition.AIR_DOMINANCE, WIN_BONUSES[WinCondition.AIR_DOMINANCE]
    if red_air_start >= 2 and count(red_pieces, PieceType.AIRFORCE) == 0:
        return Color.BLUE, WinCondition.AIR_DOMINANCE, WIN_BONUSES[WinCondition.AIR_DOMINANCE]

    blue_land_now = (
        count(blue_pieces, PieceType.TANK)
        + count(blue_pieces, PieceType.INFANTRY)
        + count(blue_pieces, PieceType.ARTILLERY)
    )
    red_land_now = (
        count(red_pieces, PieceType.TANK)
        + count(red_pieces, PieceType.INFANTRY)
        + count(red_pieces, PieceType.ARTILLERY)
    )
    if blue_land_now == 0:
        return Color.RED, WinCondition.LAND_DOMINANCE, WIN_BONUSES[WinCondition.LAND_DOMINANCE]
    if red_land_now == 0:
        return Color.BLUE, WinCondition.LAND_DOMINANCE, WIN_BONUSES[WinCondition.LAND_DOMINANCE]

    for color in (Color.RED, Color.BLUE):
        commander = _find_commander(board, color)
        if commander is None:
            continue
        if not _has_supporting_units(board, color):
            winner = Color.BLUE if color == Color.RED else Color.RED
            return winner, WinCondition.COMMANDER_ISOLATED, 0
        if _is_commander_under_threat(board, color) and not _commander_has_escape(board, commander):
            winner = Color.BLUE if color == Color.RED else Color.RED
            return winner, WinCondition.COMMANDER_TRAPPED, 0

    active_color = getattr(board, "current_turn", None)
    if active_color is not None and not board.has_any_valid_move(active_color):
        winner = Color.BLUE if active_color == Color.RED else Color.RED
        return winner, WinCondition.NO_MOVES_LEFT, 0

    return None, WinCondition.NONE, 0


def determine_winner_by_score(score_red, score_blue):
    """Called when time runs out. Returns (winner_color, is_draw)."""
    if score_red > score_blue:
        return Color.RED, False
    if score_blue > score_red:
        return Color.BLUE, False
    return None, True


def _iter_all_pieces(pieces):
    for piece in pieces:
        yield piece
        if piece.stacked_pieces:
            yield from _iter_all_pieces(piece.stacked_pieces)


def _find_commander(board, color):
    for piece in _iter_all_pieces(board.pieces):
        if piece.color == color and piece.type == PieceType.COMMANDER:
            return piece
    return None


def _has_supporting_units(board, color):
    for piece in _iter_all_pieces(board.pieces):
        if piece.color != color:
            continue
        if piece.type not in {PieceType.COMMANDER, PieceType.HEADQUARTERS}:
            return True
    return False


def _is_commander_under_threat(board, color):
    commander = _find_commander(board, color)
    if commander is None:
        return False
    return _is_square_under_threat(board, color, commander.position)


def _is_square_under_threat(board, color, square):
    if square is None:
        return False

    capture_moves = {
        MoveType.CAPTURE_REPLACE,
        MoveType.CAPTURE_NO_REPLACE,
        MoveType.AIRSTRIKE_RETURN,
        MoveType.MUTUAL_DESTROY,
    }
    for piece in board.pieces:
        if piece.color == color:
            continue
        for move in get_valid_moves(piece, board):
            if move["to"] == square and move["type"] in capture_moves:
                return True
    return False


def _commander_has_escape(board, commander):
    for move in get_valid_moves(commander, board):
        simulated = board.clone()
        simulated_commander = simulated.find_piece_by_id(commander.id)
        if simulated_commander is None:
            continue

        simulated.select_piece(simulated_commander)
        if not simulated.move_piece(move["to"][0], move["to"][1], preferred_type=move["type"]):
            continue

        moved_commander = simulated.find_piece_by_id(commander.id)
        if moved_commander is None:
            continue
        if not _is_square_under_threat(simulated, commander.color, moved_commander.position):
            return True
    return False
