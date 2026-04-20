"""
scoring.py
Handles score calculation and win condition detection for Commander Chess.
"""
from .piece import PieceType, Color

# ─────────────────────────────────────────────
# I. Điểm mỗi loại quân
# ─────────────────────────────────────────────
PIECE_SCORES = {
    PieceType.INFANTRY:    10,
    PieceType.ENGINEER:    10,
    PieceType.ANTIAIR:     10,
    PieceType.MILITIA:     10,
    PieceType.TANK:        20,
    PieceType.MISSILE:     20,
    PieceType.ARTILLERY:   30,
    PieceType.AIRFORCE:    40,
    PieceType.NAVY:        80,
    PieceType.COMMANDER:  100,
    PieceType.HEADQUARTERS: 0,
}

def get_piece_score(piece):
    """Returns the score value of a piece (including any stacked passengers)."""
    total = PIECE_SCORES.get(piece.type, 0)
    for p in piece.stacked_pieces:
        total += PIECE_SCORES.get(p.type, 0)
    return total


# ─────────────────────────────────────────────
# II. Kiểm tra điều kiện chiến thắng
# ─────────────────────────────────────────────
class WinCondition:
    NONE = None
    COMMANDER_CAPTURED   = "COMMANDER_CAPTURED"
    NO_MOVES_LEFT        = "NO_MOVES_LEFT"
    TIME_UP              = "TIME_UP"
    MARINE_DOMINANCE     = "MARINE_DOMINANCE"
    AIR_DOMINANCE        = "AIR_DOMINANCE"
    LAND_DOMINANCE       = "LAND_DOMINANCE"
    RAID_WIN             = "RAID_WIN"


def check_win_conditions(board, score_red, score_blue, mode="standard"):
    """
    Returns (winner_color, condition) or (None, WinCondition.NONE) if no winner yet.
    All domain conditions (Marine/Air/Land) are ALWAYS checked.
    The `mode` parameter can add extra conditions in future but doesn't restrict defaults.
    """
    red_pieces  = [p for p in board.pieces if p.color == Color.RED]
    blue_pieces = [p for p in board.pieces if p.color == Color.BLUE]

    def count(pieces, ptype):
        return sum(1 for p in pieces if p.type == ptype)

    # ── 1. Commander captured (top priority) ──────────────────────────────────
    if not any(p.type == PieceType.COMMANDER for p in red_pieces):
        print("Win condition: COMMANDER_CAPTURED → BLUE wins")
        return Color.BLUE, WinCondition.COMMANDER_CAPTURED

    if not any(p.type == PieceType.COMMANDER for p in blue_pieces):
        print("Win condition: COMMANDER_CAPTURED → RED wins")
        return Color.RED, WinCondition.COMMANDER_CAPTURED

    # ── 2. Marine dominance: both Navies of a side destroyed ──────────────────
    # Each side starts with exactly 2 Navy. Count of 0 = both destroyed.
    init = board.initial_counts  # set in Board.__init__

    blue_navy_start = init.get((Color.BLUE, PieceType.NAVY), 0)
    red_navy_start  = init.get((Color.RED,  PieceType.NAVY), 0)

    if blue_navy_start >= 2 and count(blue_pieces, PieceType.NAVY) == 0:
        print("Win condition: MARINE_DOMINANCE → RED wins (destroyed all Blue Navies)")
        return Color.RED, WinCondition.MARINE_DOMINANCE
    if red_navy_start >= 2 and count(red_pieces, PieceType.NAVY) == 0:
        print("Win condition: MARINE_DOMINANCE → BLUE wins (destroyed all Red Navies)")
        return Color.BLUE, WinCondition.MARINE_DOMINANCE

    # ── 3. Air dominance: both Air Forces of a side destroyed ─────────────────
    blue_af_start = init.get((Color.BLUE, PieceType.AIRFORCE), 0)
    red_af_start  = init.get((Color.RED,  PieceType.AIRFORCE), 0)

    if blue_af_start >= 2 and count(blue_pieces, PieceType.AIRFORCE) == 0:
        print("Win condition: AIR_DOMINANCE → RED wins (destroyed all Blue AirForces)")
        return Color.RED, WinCondition.AIR_DOMINANCE
    if red_af_start >= 2 and count(red_pieces, PieceType.AIRFORCE) == 0:
        print("Win condition: AIR_DOMINANCE → BLUE wins (destroyed all Red AirForces)")
        return Color.BLUE, WinCondition.AIR_DOMINANCE

    # ── 4. Land dominance: all Tank + Infantry + Artillery of a side destroyed ─
    blue_land_start = (
        init.get((Color.BLUE, PieceType.TANK), 0) +
        init.get((Color.BLUE, PieceType.INFANTRY), 0) +
        init.get((Color.BLUE, PieceType.ARTILLERY), 0)
    )
    red_land_start = (
        init.get((Color.RED, PieceType.TANK), 0) +
        init.get((Color.RED, PieceType.INFANTRY), 0) +
        init.get((Color.RED, PieceType.ARTILLERY), 0)
    )

    if blue_land_start >= 6:  # started with 2+2+2
        blue_land_now = (count(blue_pieces, PieceType.TANK) +
                         count(blue_pieces, PieceType.INFANTRY) +
                         count(blue_pieces, PieceType.ARTILLERY))
        if blue_land_now == 0:
            print("Win condition: LAND_DOMINANCE → RED wins (destroyed all Blue land forces)")
            return Color.RED, WinCondition.LAND_DOMINANCE

    if red_land_start >= 6:
        red_land_now = (count(red_pieces, PieceType.TANK) +
                        count(red_pieces, PieceType.INFANTRY) +
                        count(red_pieces, PieceType.ARTILLERY))
        if red_land_now == 0:
            print("Win condition: LAND_DOMINANCE → BLUE wins (destroyed all Red land forces)")
            return Color.BLUE, WinCondition.LAND_DOMINANCE

    return None, WinCondition.NONE



def determine_winner_by_score(score_red, score_blue):
    """Called when time runs out. Returns (winner_color, is_draw)."""
    if score_red > score_blue:
        print(f"Time up → RED wins by score: RED={score_red}, BLUE={score_blue}")
        return Color.RED, False
    elif score_blue > score_red:
        print(f"Time up → BLUE wins by score: RED={score_red}, BLUE={score_blue}")
        return Color.BLUE, False
    else:
        print(f"Time up → Draw: RED={score_red}, BLUE={score_blue}")
        return None, True   # Draw
