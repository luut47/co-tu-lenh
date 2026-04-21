from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .board import Board
from .move_rules import MoveType, get_valid_moves
from .piece import Color, Piece, PieceType
from .scoring import PIECE_SCORES


MAX_BRANCHING_BY_DEPTH = {
    4: 6,
    3: 8,
    2: 12,
    1: 18,
}
SEARCH_TIME_BUDGET = {
    1: 0.12,
    2: 0.22,
    3: 0.4,
    4: 0.65,
}

CAPTURE_MOVE_TYPES = {
    MoveType.CAPTURE_REPLACE,
    MoveType.CAPTURE_NO_REPLACE,
    MoveType.AIRSTRIKE_RETURN,
    MoveType.MUTUAL_DESTROY,
}


@dataclass(frozen=True)
class BotMove:
    piece_id: int
    to_x: int
    to_y: int
    move_type: MoveType | None
    score: int


def get_bot_move(board: Board, bot_color: Color, depth: int = 1) -> BotMove | None:
    legal_move_count = sum(1 for piece in board.pieces if piece.color == bot_color for _ in get_valid_moves(piece, board))
    effective_depth = _effective_depth(depth, legal_move_count)
    deadline = time.perf_counter() + SEARCH_TIME_BUDGET.get(depth, 0.25)
    transposition: dict[tuple, int] = {}

    board._search_depth_hint = effective_depth
    legal_moves = _get_all_moves(board, bot_color)
    if not legal_moves:
        return None

    best_score = None
    best_moves: list[BotMove] = []

    for piece, move in legal_moves:
        if time.perf_counter() >= deadline and best_moves:
            break
        next_board = _clone_board(board)
        if not _apply_move(next_board, piece.id, move["to"][0], move["to"][1], move["type"]):
            continue

        score = _alpha_beta_search(
            next_board,
            effective_depth - 1,
            bot_color,
            alpha=-10**9,
            beta=10**9,
            deadline=deadline,
            transposition=transposition,
        )
        bot_move = BotMove(
            piece_id=piece.id,
            to_x=move["to"][0],
            to_y=move["to"][1],
            move_type=move["type"],
            score=score,
        )

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [bot_move]
        elif score == best_score:
            best_moves.append(bot_move)

    if not best_moves:
        return None
    return random.choice(best_moves)


def _alpha_beta_search(
    board: Board,
    depth: int,
    perspective: Color,
    alpha: int,
    beta: int,
    deadline: float,
    transposition: dict[tuple, int],
) -> int:
    board._search_depth_hint = depth
    if time.perf_counter() >= deadline:
        return _evaluate(board, perspective)

    cache_key = (_board_signature(board), depth, perspective)
    cached = transposition.get(cache_key)
    if cached is not None:
        return cached

    if board.game_over:
        if board.winner_color is None:
            score = _evaluate(board, perspective)
            transposition[cache_key] = score
            return score
        score = 1_000_000 if board.winner_color == perspective else -1_000_000
        transposition[cache_key] = score
        return score

    if depth <= 0:
        score = _evaluate(board, perspective)
        transposition[cache_key] = score
        return score

    player_to_move = board.current_turn
    legal_moves = _get_all_moves(board, player_to_move)
    if not legal_moves:
        score = _evaluate(board, perspective)
        transposition[cache_key] = score
        return score

    if player_to_move == perspective:
        best_score = -10**9
        for piece, move in legal_moves:
            if time.perf_counter() >= deadline:
                break
            next_board = _clone_board(board)
            if not _apply_move(next_board, piece.id, move["to"][0], move["to"][1], move["type"]):
                continue
            score = _alpha_beta_search(next_board, depth - 1, perspective, alpha, beta, deadline, transposition)
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        final_score = best_score if best_score != -10**9 else _evaluate(board, perspective)
        transposition[cache_key] = final_score
        return final_score

    best_score = 10**9
    for piece, move in legal_moves:
        if time.perf_counter() >= deadline:
            break
        next_board = _clone_board(board)
        if not _apply_move(next_board, piece.id, move["to"][0], move["to"][1], move["type"]):
            continue
        score = _alpha_beta_search(next_board, depth - 1, perspective, alpha, beta, deadline, transposition)
        best_score = min(best_score, score)
        beta = min(beta, best_score)
        if beta <= alpha:
            break
    final_score = best_score if best_score != 10**9 else _evaluate(board, perspective)
    transposition[cache_key] = final_score
    return final_score


def _evaluate(board: Board, perspective: Color) -> int:
    score = 0
    for piece in _iter_all_pieces(board.pieces):
        value = PIECE_SCORES.get(piece.type, 0)
        if piece.is_hero:
            value += 15
        if piece.color == perspective:
            score += value
        else:
            score -= value

    score_delta = board.score_blue - board.score_red
    if perspective == Color.RED:
        score -= score_delta * 5
    else:
        score += score_delta * 5

    opponent = Color.BLUE if perspective == Color.RED else Color.RED
    score += (_piece_count(board, perspective) - _piece_count(board, opponent)) * 4

    my_attack_pressure = 0
    enemy_attack_pressure = 0
    for piece in board.pieces:
        move_count = len(get_valid_moves(piece, board))
        if piece.color == perspective:
            my_attack_pressure += min(move_count, 6)
        else:
            enemy_attack_pressure += min(move_count, 6)
    score += (my_attack_pressure - enemy_attack_pressure) * 2

    my_commander = _find_commander(board, perspective)
    enemy_commander = _find_commander(board, opponent)
    if my_commander is None:
        score -= 50_000
    if enemy_commander is None:
        score += 50_000

    return score


def _get_all_moves(board: Board, color: Color) -> list[tuple[Piece, dict]]:
    moves: list[tuple[Piece, dict]] = []
    for piece in board.pieces:
        if piece.color != color:
            continue

        piece_moves = get_valid_moves(piece, board)
        piece_moves.sort(key=_move_priority, reverse=True)
        for move in piece_moves:
            moves.append((piece, move))

    moves.sort(key=lambda item: _move_priority(item[1]), reverse=True)
    branch_limit = MAX_BRANCHING_BY_DEPTH.get(max(1, getattr(board, "_search_depth_hint", 1)), 24)
    return moves[:branch_limit]


def _clone_board(board: Board) -> Board:
    cloned = board.clone()
    cloned._search_depth_hint = getattr(board, "_search_depth_hint", 1)
    return cloned


def _apply_move(board: Board, piece_id: int, to_x: int, to_y: int, move_type: MoveType | None) -> bool:
    piece = board.find_piece_by_id(piece_id)
    if piece is None:
        return False

    board.current_turn = piece.color
    board.select_piece(piece)
    return board.move_piece(to_x, to_y, preferred_type=move_type)


def _iter_all_pieces(pieces):
    for piece in pieces:
        yield piece
        if piece.stacked_pieces:
            yield from _iter_all_pieces(piece.stacked_pieces)


def _find_commander(board: Board, color: Color):
    for piece in _iter_all_pieces(board.pieces):
        if piece.color == color and piece.type == PieceType.COMMANDER:
            return piece
    return None


def _move_priority(move: dict) -> int:
    if move["type"] in CAPTURE_MOVE_TYPES:
        base = 30
        weapon = (move.get("extra_data") or {}).get("weapon")
        if weapon == "anti_ship_missile":
            return base + 5
        if weapon == "navy_artillery":
            return base + 4
        return base
    if move["type"] == MoveType.COMBINE:
        return 20
    if move["type"] == MoveType.DEPLOY:
        return 10
    return 0


def _effective_depth(requested_depth: int, legal_move_count: int) -> int:
    if requested_depth <= 2:
        return requested_depth
    if legal_move_count > 40:
        return max(2, requested_depth - 2)
    if legal_move_count > 24:
        return max(2, requested_depth - 1)
    return requested_depth


def _piece_count(board: Board, color: Color) -> int:
    return sum(1 for piece in _iter_all_pieces(board.pieces) if piece.color == color)


def _board_signature(board: Board):
    pieces = []
    for piece in _iter_all_pieces(board.pieces):
        pieces.append((
            piece.id,
            piece.type.name,
            piece.color.name,
            piece.position[0],
            piece.position[1],
            int(piece.is_hero),
        ))
    pieces.sort()
    return (
        tuple(pieces),
        board.current_turn.name,
        board.score_red,
        board.score_blue,
        board.bonus_action_piece_id,
        board.game_over,
        board.winner_color.name if board.winner_color else None,
    )
