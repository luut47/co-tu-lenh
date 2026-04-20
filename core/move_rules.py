from enum import Enum

from .board_layout import COLS, ROWS, Zone, get_zone, is_river_mouth
from .piece import Color, PieceType


class MoveType(Enum):
    MOVE = "MOVE"
    CAPTURE_REPLACE = "CAPTURE_REPLACE"
    CAPTURE_NO_REPLACE = "CAPTURE_NO_REPLACE"
    COMBINE = "COMBINE"
    DEPLOY = "DEPLOY"
    AIRSTRIKE_RETURN = "AIRSTRIKE_RETURN"
    AIRSPACE_CRASH = "AIRSPACE_CRASH"
    MUTUAL_DESTROY = "MUTUAL_DESTROY"


STRAIGHT_DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
DIAGONAL_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ALL_DIRS = STRAIGHT_DIRS + DIAGONAL_DIRS
MISSILE_PATTERN = {
    (1, 0), (2, 0), (-1, 0), (-2, 0),
    (0, 1), (0, 2), (0, -1), (0, -2),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
}
DEEP_RIVER_PIECES = {
    PieceType.INFANTRY,
    PieceType.ENGINEER,
    PieceType.MILITIA,
    PieceType.TANK,
    PieceType.COMMANDER,
}
ENGINEER_PASSENGERS = {PieceType.ARTILLERY, PieceType.ANTIAIR, PieceType.MISSILE}
NAVY_PASSENGERS = {PieceType.ARTILLERY, PieceType.ANTIAIR, PieceType.MISSILE}


def get_valid_moves(piece, board):
    moves = []
    x, y = piece.position

    def add_move(move_type, tx, ty, extra_data=None):
        if not _in_bounds(tx, ty):
            return
        move = {"type": move_type, "to": (tx, ty), "extra_data": extra_data}
        if not _violates_commander_facing(piece, move, board):
            moves.append(move)

    def add_step(tx, ty, allow_combine=False):
        if not _in_bounds(tx, ty):
            return
        target_piece = board.get_piece_at(tx, ty)
        if target_piece:
            if target_piece.color == piece.color:
                if allow_combine and _can_combine(piece, target_piece):
                    add_move(MoveType.COMBINE, tx, ty)
                return
            capture_type = _get_capture_type(piece, target_piece, board, (x, y), (tx, ty))
            if capture_type:
                add_move(capture_type, tx, ty)
            return
        if _can_move_to(piece, board, tx, ty) and _line_clear_for_move(piece, board, (x, y), (tx, ty)):
            add_move(MoveType.MOVE, tx, ty)

    def add_slide(directions, max_steps):
        for dx, dy in directions:
            for step in range(1, max_steps + 1):
                tx, ty = x + dx * step, y + dy * step
                if not _in_bounds(tx, ty):
                    break
                target_piece = board.get_piece_at(tx, ty)
                if target_piece:
                    if target_piece.color == piece.color:
                        if _can_combine(piece, target_piece):
                            add_move(MoveType.COMBINE, tx, ty)
                    else:
                        capture_type = _get_capture_type(piece, target_piece, board, (x, y), (tx, ty))
                        if capture_type:
                            add_move(capture_type, tx, ty)
                    break
                if _can_move_to(piece, board, tx, ty) and _line_clear_for_move(piece, board, (x, y), (tx, ty)):
                    add_move(MoveType.MOVE, tx, ty)
                else:
                    break

    if piece.type in {PieceType.INFANTRY, PieceType.ENGINEER, PieceType.ANTIAIR}:
        unit_dirs = ALL_DIRS if piece.is_hero else STRAIGHT_DIRS
        unit_range = 2 if piece.is_hero else 1
        add_slide(unit_dirs, unit_range)
        if piece.type == PieceType.ENGINEER and piece.stacked_pieces:
            _add_engineer_bridge_moves(piece, board, add_move)
    elif piece.type == PieceType.MILITIA:
        add_slide(ALL_DIRS, 2 if piece.is_hero else 1)
    elif piece.type == PieceType.TANK:
        add_slide(ALL_DIRS if piece.is_hero else STRAIGHT_DIRS, 3 if piece.is_hero else 2)
    elif piece.type == PieceType.MISSILE:
        for dx, dy in _get_missile_pattern(piece):
            add_step(x + dx, y + dy)
    elif piece.type == PieceType.COMMANDER:
        add_slide(ALL_DIRS if piece.is_hero else STRAIGHT_DIRS, max(COLS, ROWS))
    elif piece.type == PieceType.ARTILLERY:
        add_slide(ALL_DIRS, 4 if piece.is_hero else 3)
        _add_artillery_attacks(piece, board, add_move)
    elif piece.type == PieceType.AIRFORCE:
        _add_airforce_moves(piece, board, add_move)
    elif piece.type == PieceType.NAVY:
        add_slide(STRAIGHT_DIRS, max(COLS, ROWS))
        _add_navy_attacks(piece, board, add_move)

    if _can_deploy(piece):
        _add_deploy_moves(piece, board, add_move)

    return moves


def _add_artillery_attacks(piece, board, add_move):
    x, y = piece.position
    for dx, dy in ALL_DIRS:
        for step in range(1, (4 if piece.is_hero else 3) + 1):
            tx, ty = x + dx * step, y + dy * step
            if not _in_bounds(tx, ty):
                break
            target_piece = board.get_piece_at(tx, ty)
            if target_piece is None or target_piece.color == piece.color:
                continue
            move_type = MoveType.CAPTURE_NO_REPLACE if get_zone(tx, ty) == Zone.SEA else MoveType.CAPTURE_REPLACE
            add_move(move_type, tx, ty)


def _add_airforce_moves(piece, board, add_move):
    x, y = piece.position
    enemy_defense = _compute_air_defense(board, piece.color)
    for dx, dy in ALL_DIRS:
        for step in range(1, (5 if piece.is_hero else 4) + 1):
            tx, ty = x + dx * step, y + dy * step
            if not _in_bounds(tx, ty):
                break

            path = _squares_between((x, y), (tx, ty), include_end=False)
            crash_square = None
            if not piece.is_hero:
                crash_square = next((square for square in path if square in enemy_defense), None)

            target_piece = board.get_piece_at(tx, ty)
            if target_piece is None:
                if crash_square is not None:
                    add_move(MoveType.AIRSPACE_CRASH, tx, ty, {"crash_at": crash_square})
                    continue
                if (tx, ty) in enemy_defense and not piece.is_hero:
                    add_move(MoveType.AIRSPACE_CRASH, tx, ty, {"crash_at": (tx, ty)})
                    continue
                add_move(MoveType.MOVE, tx, ty)
                continue

            if target_piece.color == piece.color:
                continue

            if target_piece.type in {PieceType.ANTIAIR, PieceType.MISSILE} and not piece.is_hero:
                add_move(MoveType.MUTUAL_DESTROY, tx, ty)
                continue

            if (tx, ty) in enemy_defense and not piece.is_hero:
                add_move(MoveType.MUTUAL_DESTROY, tx, ty)
                continue

            if crash_square is not None:
                add_move(MoveType.AIRSPACE_CRASH, tx, ty, {"crash_at": crash_square})
                continue

            add_move(MoveType.CAPTURE_REPLACE, tx, ty)
            if target_piece.type != PieceType.AIRFORCE:
                add_move(MoveType.AIRSTRIKE_RETURN, tx, ty, {"return_to": (x, y)})


def _add_navy_attacks(piece, board, add_move):
    if _stack_contains_type(piece, PieceType.ARTILLERY):
        _add_navy_land_artillery_attacks(piece, board, add_move)
    if _stack_contains_type(piece, PieceType.MISSILE):
        _add_navy_antiship_attacks(piece, board, add_move)


def _add_navy_land_artillery_attacks(piece, board, add_move):
    x, y = piece.position
    for dx, dy in ALL_DIRS:
        max_steps = 4 if piece.is_hero else 3
        for step in range(1, max_steps + 1):
            tx, ty = x + dx * step, y + dy * step
            if not _in_bounds(tx, ty):
                break

            target_piece = board.get_piece_at(tx, ty)
            if target_piece is None:
                continue
            if target_piece.color == piece.color:
                continue

            if get_zone(tx, ty) != Zone.LAND:
                break

            move_type = (
                MoveType.CAPTURE_REPLACE
                if _navy_attack_requires_replacement((x, y), (tx, ty))
                else MoveType.CAPTURE_NO_REPLACE
            )
            add_move(move_type, tx, ty, {"weapon": "navy_artillery"})


def _add_navy_antiship_attacks(piece, board, add_move):
    x, y = piece.position
    for dx, dy in ALL_DIRS:
        max_steps = 5 if piece.is_hero else 4
        for step in range(1, max_steps + 1):
            tx, ty = x + dx * step, y + dy * step
            if not _in_bounds(tx, ty):
                break

            target_piece = board.get_piece_at(tx, ty)
            if target_piece is None:
                continue
            if target_piece.color == piece.color:
                continue
            if target_piece.type != PieceType.NAVY:
                break
            if not _is_navy_antiship_target_square(tx, ty):
                break

            add_move(MoveType.CAPTURE_REPLACE, tx, ty, {"weapon": "anti_ship_missile"})
            break


def _add_deploy_moves(piece, board, add_move):
    passenger = piece.stacked_pieces[-1]
    for dx, dy in ALL_DIRS:
        tx, ty = piece.position[0] + dx, piece.position[1] + dy
        if not _in_bounds(tx, ty):
            continue
        if board.get_piece_at(tx, ty):
            continue
        if _can_piece_enter_square(passenger.type, tx, ty):
            add_move(MoveType.DEPLOY, tx, ty)


def _add_engineer_bridge_moves(piece, board, add_move):
    passenger = piece.stacked_pieces[-1]
    if passenger.type not in ENGINEER_PASSENGERS:
        return

    x, y = piece.position
    for dy in (-2, 2):
        mid_y = y + (dy // 2)
        tx, ty = x, y + dy
        if not _in_bounds(tx, ty) or not _in_bounds(x, mid_y):
            continue
        if get_zone(x, mid_y) != Zone.RIVER:
            continue
        if get_zone(x, y) != Zone.LAND or get_zone(tx, ty) != Zone.LAND:
            continue

        target_piece = board.get_piece_at(tx, ty)
        if target_piece is None:
            add_move(MoveType.MOVE, tx, ty)
            continue
        if target_piece.color != piece.color:
            add_move(MoveType.CAPTURE_REPLACE, tx, ty)


def _get_capture_type(piece, target_piece, board, start, dest):
    if piece.type == PieceType.COMMANDER:
        if _line_length(start, dest) == 1 and _is_straight_line(start, dest):
            return MoveType.CAPTURE_REPLACE
        return None
    if piece.type in {PieceType.INFANTRY, PieceType.ENGINEER, PieceType.ANTIAIR}:
        line_limit = 2 if piece.is_hero else 1
        if _line_length(start, dest) > line_limit:
            return None
        if not _is_straight_line(start, dest) and not (piece.is_hero and _is_straight_or_diagonal(start, dest)):
            return None
        return MoveType.CAPTURE_NO_REPLACE if get_zone(*dest) == Zone.SEA else MoveType.CAPTURE_REPLACE
    if piece.type == PieceType.MILITIA:
        if _line_length(start, dest) > (2 if piece.is_hero else 1):
            return None
        if not _is_straight_or_diagonal(start, dest):
            return None
        return MoveType.CAPTURE_NO_REPLACE if get_zone(*dest) == Zone.SEA else MoveType.CAPTURE_REPLACE
    if piece.type == PieceType.TANK:
        line_limit = 3 if piece.is_hero else 2
        if _line_length(start, dest) > line_limit:
            return None
        if not _is_straight_line(start, dest) and not (piece.is_hero and _is_straight_or_diagonal(start, dest)):
            return None
        if not _line_clear_for_move(piece, board, start, dest, include_end=False):
            return None
        return MoveType.CAPTURE_NO_REPLACE if get_zone(*dest) == Zone.SEA else MoveType.CAPTURE_REPLACE
    if piece.type == PieceType.MISSILE:
        dx = dest[0] - start[0]
        dy = dest[1] - start[1]
        if (dx, dy) in _get_missile_pattern(piece):
            return MoveType.CAPTURE_NO_REPLACE if get_zone(*dest) == Zone.SEA else MoveType.CAPTURE_REPLACE
        return None
    if piece.type == PieceType.ARTILLERY:
        if _is_straight_or_diagonal(start, dest) and _line_length(start, dest) <= (4 if piece.is_hero else 3):
            return MoveType.CAPTURE_NO_REPLACE if get_zone(*dest) == Zone.SEA else MoveType.CAPTURE_REPLACE
        return None
    if piece.type in {PieceType.NAVY, PieceType.AIRFORCE}:
        return None
    return None


def _can_move_to(piece, board, tx, ty):
    if piece.type == PieceType.HEADQUARTERS:
        return False
    if board.get_piece_at(tx, ty):
        return False
    return _can_piece_enter_square(piece.type, tx, ty)


def _can_piece_enter_square(piece_type, x, y):
    zone = get_zone(x, y)
    if zone is None:
        return False
    if piece_type == PieceType.AIRFORCE:
        return True
    if piece_type == PieceType.NAVY:
        return zone in {Zone.SEA, Zone.RIVER}
    if piece_type == PieceType.HEADQUARTERS:
        return False
    if zone == Zone.FORD:
        return True
    if zone == Zone.SEA:
        return False
    if zone == Zone.RIVER:
        return piece_type in DEEP_RIVER_PIECES
    return True


def _line_clear_for_move(piece, board, start, dest, include_end=True):
    for square in _squares_between(start, dest, include_end=include_end):
        if not _can_piece_enter_square(piece.type, square[0], square[1]):
            return False
        if square != dest and board.get_piece_at(*square):
            return False
    if include_end and board.get_piece_at(*dest):
        return False
    return True


def _compute_air_defense(board, moving_color):
    defended = set()
    for piece in board.pieces:
        if piece.color == moving_color:
            continue
        x, y = piece.position
        if piece.type == PieceType.ANTIAIR or (
            piece.type == PieceType.NAVY and _stack_contains_type(piece, PieceType.ANTIAIR)
        ):
            for dx, dy in STRAIGHT_DIRS:
                tx, ty = x + dx, y + dy
                if _in_bounds(tx, ty):
                    defended.add((tx, ty))
        elif piece.type == PieceType.MISSILE:
            for dx, dy in MISSILE_PATTERN:
                tx, ty = x + dx, y + dy
                if _in_bounds(tx, ty):
                    defended.add((tx, ty))
    return defended


def _get_missile_pattern(piece):
    if not piece.is_hero:
        return MISSILE_PATTERN

    heroic_pattern = set(MISSILE_PATTERN)
    heroic_pattern.update({
        (3, 0), (-3, 0), (0, 3), (0, -3),
        (2, 2), (2, -2), (-2, 2), (-2, -2),
    })
    return heroic_pattern


def _can_combine(piece, target_piece):
    if piece.color != target_piece.color:
        return False
    if target_piece.type == PieceType.HEADQUARTERS:
        return piece.type == PieceType.COMMANDER and len(target_piece.stacked_pieces) == 0
    if target_piece.type == PieceType.NAVY and piece.type in NAVY_PASSENGERS:
        carried_types = {stacked_piece.type for stacked_piece in target_piece.stacked_pieces}
        return piece.type not in carried_types and PieceType.COMMANDER not in carried_types
    if piece.type in ENGINEER_PASSENGERS and target_piece.type == PieceType.ENGINEER:
        return len(target_piece.stacked_pieces) == 0
    return False


def _can_deploy(piece):
    return bool(piece.stacked_pieces)


def _violates_commander_facing(piece, move, board):
    commanders = {}
    blockers = set()

    for current in _iter_pieces(board.pieces):
        blockers.add(current.position)
        if current.type == PieceType.COMMANDER:
            commanders[current.color] = current.position

    target_piece = board.get_piece_at(*move["to"])
    blockers.discard(piece.position)

    if move["type"] == MoveType.MUTUAL_DESTROY:
        if piece.type == PieceType.COMMANDER:
            commanders.pop(piece.color, None)
        if target_piece and target_piece.type == PieceType.COMMANDER:
            commanders.pop(target_piece.color, None)
            blockers.discard(target_piece.position)
    else:
        if piece.type == PieceType.COMMANDER:
            commanders[piece.color] = move["to"]
        blockers.add(move["to"] if move["type"] != MoveType.CAPTURE_NO_REPLACE else piece.position)
        if target_piece and target_piece.type == PieceType.COMMANDER:
            commanders.pop(target_piece.color, None)
            blockers.discard(target_piece.position)

    if len(commanders) != 2:
        return False

    red = commanders.get(Color.RED)
    blue = commanders.get(Color.BLUE)
    if red is None or blue is None:
        return False
    if red[0] != blue[0] and red[1] != blue[1]:
        return False

    blockers.discard(red)
    blockers.discard(blue)
    for square in _squares_between(red, blue, include_end=False):
        if square in blockers:
            return False
    return True


def _squares_between(start, dest, include_end=True):
    dx = dest[0] - start[0]
    dy = dest[1] - start[1]
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
    distance = max(abs(dx), abs(dy))
    squares = []
    for step in range(1, distance + 1):
        if step == distance and not include_end:
            break
        squares.append((start[0] + step_x * step, start[1] + step_y * step))
    return squares


def _line_length(start, dest):
    return max(abs(dest[0] - start[0]), abs(dest[1] - start[1]))


def _is_straight_line(start, dest):
    return start[0] == dest[0] or start[1] == dest[1]


def _is_straight_or_diagonal(start, dest):
    dx = abs(dest[0] - start[0])
    dy = abs(dest[1] - start[1])
    return dx == 0 or dy == 0 or dx == dy


def _is_coast_square(x, y):
    if get_zone(x, y) != Zone.LAND:
        return False
    for dx, dy in STRAIGHT_DIRS:
        tx, ty = x + dx, y + dy
        if _in_bounds(tx, ty) and get_zone(tx, ty) == Zone.SEA:
            return True
    return False


def _navy_attack_requires_replacement(start, dest):
    if not _is_coast_square(*dest):
        return False
    crossed_land = False
    for square in _squares_between(start, dest, include_end=False):
        if get_zone(*square) == Zone.LAND:
            crossed_land = True
            break
    return not crossed_land


def _is_navy_antiship_target_square(x, y):
    zone = get_zone(x, y)
    return zone == Zone.SEA or (zone == Zone.RIVER and is_river_mouth(x, y))


def _stack_contains_type(piece, piece_type):
    return any(stacked_piece.type == piece_type for stacked_piece in piece.stacked_pieces)


def _in_bounds(x, y):
    return 0 <= x < COLS and 0 <= y < ROWS


def _iter_pieces(pieces):
    for piece in pieces:
        yield piece
        if piece.stacked_pieces:
            yield from _iter_pieces(piece.stacked_pieces)
