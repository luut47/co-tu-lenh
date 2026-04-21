from .move_rules import MoveType, get_valid_moves
from .piece import Color, Piece, PieceType
from .piece_factory import setup_default_pieces
from .scoring import WinCondition, check_win_conditions, determine_winner_by_score, get_piece_score


class Board:
    def __init__(self, mode="standard"):
        self.pieces = setup_default_pieces()
        self.current_turn = Color.RED
        self.selected_piece = None
        self.valid_moves = []
        self.last_move_to = None
        self.combat_logs = []
        self.bonus_action_piece_id = None
        self.mode = mode

        self.score_red = 0
        self.score_blue = 0

        self.game_over = False
        self.winner_color = None
        self.win_condition = WinCondition.NONE

        self.initial_counts = {}
        for p in self.pieces:
            key = (p.color, p.type)
            self.initial_counts[key] = self.initial_counts.get(key, 0) + 1

    def get_piece_at(self, x, y):
        for p in self.pieces:
            if p.position == (x, y):
                return p
        return None

    def find_piece_by_id(self, piece_id):
        for piece in self.pieces:
            if piece.id == piece_id:
                return piece
        return None

    def select_piece(self, piece):
        if (
            piece
            and piece.color == self.current_turn
            and (self.bonus_action_piece_id is None or piece.id == self.bonus_action_piece_id)
        ):
            self.selected_piece = piece
            self.valid_moves = get_valid_moves(piece, self)
        else:
            self.selected_piece = None
            self.valid_moves = []

    def unselect_piece(self):
        self.selected_piece = None
        self.valid_moves = []

    def get_matching_moves(self, to_x, to_y):
        return [move for move in self.valid_moves if move["to"] == (to_x, to_y)]

    def move_piece(self, to_x, to_y, preferred_type=None):
        if not self.selected_piece or self.game_over:
            return False

        matching_moves = self.get_matching_moves(to_x, to_y)
        if not matching_moves:
            return False

        move_data = None
        if preferred_type is not None:
            for move in matching_moves:
                if move["type"] == preferred_type:
                    move_data = move
                    break
        if move_data is None:
            move_data = matching_moves[0]

        piece = self.selected_piece
        from_pos = piece.position
        move_type = move_data["type"]
        extra_data = move_data.get("extra_data") or {}
        target = self.get_piece_at(to_x, to_y)
        self.combat_logs = []

        if move_type in {
            MoveType.CAPTURE_REPLACE,
            MoveType.CAPTURE_NO_REPLACE,
            MoveType.AIRSTRIKE_RETURN,
            MoveType.MUTUAL_DESTROY,
        }:
            if target:
                self._award_score(piece.color, target)
                self.pieces.remove(target)

        if move_type == MoveType.COMBINE:
            target = self.get_piece_at(to_x, to_y)
            if not target:
                return False
            carrier, passenger = _resolve_combine_roles(piece, target)
            if carrier is None or passenger is None:
                return False
            carrier.add_to_stack(passenger)
            if passenger in self.pieces:
                self.pieces.remove(passenger)
            self.last_move_to = (to_x, to_y)
            self.combat_logs.append(f"Combined {passenger.type.name} into {carrier.type.name}")
        elif move_type == MoveType.DEPLOY:
            if not piece.stacked_pieces:
                return False
            deployed_piece = piece.stacked_pieces.pop()
            deployed_piece.move_to((to_x, to_y))
            self.pieces.append(deployed_piece)
            self.last_move_to = (to_x, to_y)
            self.combat_logs.append(f"Deployed {deployed_piece.type.name} -> {(to_x, to_y)}")
            self.bonus_action_piece_id = deployed_piece.id
        elif move_type == MoveType.CAPTURE_NO_REPLACE:
            self.last_move_to = (to_x, to_y)
            if target:
                self.combat_logs.append(
                    f"{piece.type.name}{from_pos} destroy {target.type.name}{(to_x, to_y)}"
                )
        elif move_type == MoveType.AIRSTRIKE_RETURN:
            return_to = move_data.get("extra_data", {}).get("return_to", from_pos)
            piece.move_to(return_to)
            self.last_move_to = (to_x, to_y)
            if target:
                self.combat_logs.append(
                    f"{piece.type.name}{from_pos} destroy {target.type.name}{(to_x, to_y)} and returned to {return_to}"
                )
        elif move_type == MoveType.AIRSPACE_CRASH:
            crash_at = move_data.get("extra_data", {}).get("crash_at", (to_x, to_y))
            if piece in self.pieces:
                piece.move_to(crash_at)
                self.pieces.remove(piece)
            self.last_move_to = crash_at
            self.combat_logs.append(
                f"{piece.type.name}{from_pos} entered enemy air-defense at {crash_at} and was destroyed"
            )
        elif move_type == MoveType.MUTUAL_DESTROY:
            if piece in self.pieces:
                self.pieces.remove(piece)
            self.last_move_to = (to_x, to_y)
            if target:
                self.combat_logs.append(
                    f"{piece.type.name}{from_pos} destroy {target.type.name}{(to_x, to_y)} and was destroyed"
                )
        else:
            if move_type == MoveType.CAPTURE_REPLACE and extra_data.get("weapon") == "navy_artillery":
                artillery_piece = _extract_stacked_piece(piece, PieceType.ARTILLERY)
                if artillery_piece is None:
                    return False
                artillery_piece.move_to((to_x, to_y))
                self.pieces.append(artillery_piece)
                self.selected_piece = artillery_piece
                self.last_move_to = (to_x, to_y)
                if target:
                    self.combat_logs.append(
                        f"ARTILLERY from NAVY{from_pos} destroy {target.type.name}{(to_x, to_y)} and occupied {(to_x, to_y)}"
                    )
            else:
                piece.move_to((to_x, to_y))
                self.last_move_to = (to_x, to_y)
                if move_type == MoveType.CAPTURE_REPLACE and target:
                    weapon = extra_data.get("weapon")
                    if weapon == "anti_ship_missile":
                        self.combat_logs.append(
                            f"NAVY{from_pos} fired anti-ship missile, destroy {target.type.name}{(to_x, to_y)} and occupied {(to_x, to_y)}"
                        )
                    elif weapon == "navy_artillery":
                        self.combat_logs.append(
                            f"{piece.type.name}{from_pos} destroy {target.type.name}{(to_x, to_y)} and occupied {(to_x, to_y)}"
                        )
                    else:
                        self.combat_logs.append(
                            f"{piece.type.name}{from_pos} destroy {target.type.name}{(to_x, to_y)} and occupied {(to_x, to_y)}"
                        )
                else:
                    self.combat_logs.append(f"{piece.type.name}{from_pos} -> {(to_x, to_y)}")

        self.check_heroic_promotion()
        self._check_game_over()
        if not self.game_over:
            if move_type == MoveType.DEPLOY and self.bonus_action_piece_id is not None:
                bonus_piece = self.find_piece_by_id(self.bonus_action_piece_id)
                if bonus_piece:
                    self.select_piece(bonus_piece)
                if not self.valid_moves:
                    self.bonus_action_piece_id = None
                    self.switch_turn()
            elif self.bonus_action_piece_id is not None and piece.id == self.bonus_action_piece_id:
                self.bonus_action_piece_id = None
                self.switch_turn()
            else:
                self.switch_turn()
        else:
            self.bonus_action_piece_id = None
            self.unselect_piece()
        return True

    def _award_score(self, color, captured_piece):
        score = get_piece_score(captured_piece)
        if color == Color.RED:
            self.score_red += score
        else:
            self.score_blue += score

    def _check_game_over(self):
        winner, condition, bonus = check_win_conditions(self, self.score_red, self.score_blue, self.mode)
        if winner is not None:
            self._award_bonus(winner, bonus)
            self.game_over = True
            self.winner_color = winner
            self.win_condition = condition

    def time_up(self):
        winner, _is_draw = determine_winner_by_score(self.score_red, self.score_blue)
        self.game_over = True
        self.winner_color = winner
        self.win_condition = WinCondition.TIME_UP

    def check_heroic_promotion(self):
        moved_piece = self.selected_piece
        if moved_piece is None or moved_piece not in self.pieces:
            return
        if moved_piece.is_hero:
            return

        enemy_color = Color.BLUE if moved_piece.color == Color.RED else Color.RED
        enemy_commander = self._find_commander(enemy_color)
        if enemy_commander is None:
            return

        for move in get_valid_moves(moved_piece, self):
            if move["to"] == enemy_commander.position and move["type"] in {
                MoveType.CAPTURE_REPLACE,
                MoveType.CAPTURE_NO_REPLACE,
                MoveType.AIRSTRIKE_RETURN,
                MoveType.MUTUAL_DESTROY,
            }:
                moved_piece.is_hero = True
                self.combat_logs.append(f"{moved_piece.type.name} promoted to HERO")
                return

    def switch_turn(self):
        self.bonus_action_piece_id = None
        self.current_turn = Color.BLUE if self.current_turn == Color.RED else Color.RED
        self.unselect_piece()

    def has_any_valid_move(self, color=None):
        target_color = color or self.current_turn
        for piece in self.pieces:
            if piece.color != target_color:
                continue
            if get_valid_moves(piece, self):
                return True
        return False

    def clone(self):
        cloned = Board(self.mode)
        cloned.pieces = [_clone_piece(piece) for piece in self.pieces]
        cloned.current_turn = self.current_turn
        cloned.selected_piece = None
        cloned.valid_moves = []
        cloned.last_move_to = self.last_move_to
        cloned.combat_logs = list(self.combat_logs)
        cloned.bonus_action_piece_id = self.bonus_action_piece_id
        cloned.score_red = self.score_red
        cloned.score_blue = self.score_blue
        cloned.game_over = self.game_over
        cloned.winner_color = self.winner_color
        cloned.win_condition = self.win_condition
        cloned.initial_counts = dict(self.initial_counts)
        return cloned

    def _award_bonus(self, color, bonus):
        if bonus <= 0:
            return
        if color == Color.RED:
            self.score_red += bonus
        else:
            self.score_blue += bonus

    def _find_commander(self, color):
        for piece in self._iter_all_pieces():
            if piece.color == color and piece.type == PieceType.COMMANDER:
                return piece
        return None

    def _iter_all_pieces(self):
        for piece in self.pieces:
            yield piece
            if piece.stacked_pieces:
                yield from _iter_nested_pieces(piece.stacked_pieces)


def _iter_nested_pieces(pieces):
    for piece in pieces:
        yield piece
        if piece.stacked_pieces:
            yield from _iter_nested_pieces(piece.stacked_pieces)


def _clone_piece(piece: Piece):
    copied_piece = Piece(piece.id, piece.type, piece.color, piece.position, piece.is_hero)
    copied_piece.stacked_pieces = [_clone_piece(stacked_piece) for stacked_piece in piece.stacked_pieces]
    return copied_piece


def _extract_stacked_piece(piece: Piece, piece_type: PieceType):
    for index in range(len(piece.stacked_pieces) - 1, -1, -1):
        stacked_piece = piece.stacked_pieces[index]
        if stacked_piece.type == piece_type:
            return piece.stacked_pieces.pop(index)
    return None


def _resolve_combine_roles(piece_a: Piece, piece_b: Piece):
    if piece_a.type == PieceType.HEADQUARTERS and piece_b.type == PieceType.COMMANDER:
        return piece_a, piece_b
    if piece_b.type == PieceType.HEADQUARTERS and piece_a.type == PieceType.COMMANDER:
        return piece_b, piece_a

    if piece_a.type == PieceType.NAVY and piece_b.type in {PieceType.ARTILLERY, PieceType.ANTIAIR, PieceType.MISSILE}:
        return piece_a, piece_b
    if piece_b.type == PieceType.NAVY and piece_a.type in {PieceType.ARTILLERY, PieceType.ANTIAIR, PieceType.MISSILE}:
        return piece_b, piece_a

    if piece_a.type == PieceType.ENGINEER and piece_b.type in {PieceType.ARTILLERY, PieceType.ANTIAIR, PieceType.MISSILE}:
        return piece_a, piece_b
    if piece_b.type == PieceType.ENGINEER and piece_a.type in {PieceType.ARTILLERY, PieceType.ANTIAIR, PieceType.MISSILE}:
        return piece_b, piece_a

    return None, None
