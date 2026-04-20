import random
from .piece_factory import setup_default_pieces
from .piece import Color, PieceType
from .move_rules import get_valid_moves, MoveType
from .combat_rules import get_valid_attacks, resolve_combat
from .special_rules import (
    check_river_crossing, apply_airforce_aa_interaction,
    can_combine, apply_combination,
    get_commander_faceoff_blocked_dirs,
    would_expose_commander_to_faceoff,
)
from .scoring import check_win_conditions, determine_winner_by_score, WinCondition

class Board:
    def __init__(self, mode="standard"):
        self.pieces = setup_default_pieces()
        self.current_turn = random.choice([Color.RED, Color.BLUE])
        self.selected_piece = None
        self.valid_moves = []
        self.combat_logs = []
        self.mode = mode

        # Score tracking
        self.score_red  = 0
        self.score_blue = 0

        # Win state
        self.game_over   = False
        self.winner_color = None
        self.win_condition = WinCondition.NONE

        # Track initial piece counts per (color, type) for win condition detection
        self.initial_counts = {}
        for p in self.pieces:
            key = (p.color, p.type)
            self.initial_counts[key] = self.initial_counts.get(key, 0) + 1

        
    def get_piece_at(self, x, y):
        for p in self.pieces:
            if p.position == (x, y):
                return p
        return None
        
    def select_piece(self, piece):
        if piece and piece.color == self.current_turn:
            self.selected_piece = piece
            self.valid_moves = []
            
            # 1. Physical moves (filtered by river crossing)
            for m in get_valid_moves(piece, self):
                if check_river_crossing(piece, m['to']):
                    self.valid_moves.append(m)

            # 2. Attacks
            for a in get_valid_attacks(piece, self):
                if a.get('is_stand_still', False) or check_river_crossing(piece, a['to']):
                    a['type'] = MoveType.CAPTURE
                    self.valid_moves.append(a)

            # 3. Combine moves (adjacent ally carrier/passenger)
            cx, cy = piece.position
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
                tx, ty = cx + dx, cy + dy
                p = self.get_piece_at(tx, ty)
                if p and p.color == piece.color:
                    if can_combine(p, piece):
                        self.valid_moves.append({'to': (tx, ty), 'type': MoveType.COMBINE, 'carrier': p, 'passenger': piece})
                    elif can_combine(piece, p):
                        self.valid_moves.append({'to': (tx, ty), 'type': MoveType.COMBINE, 'carrier': piece, 'passenger': p})

            # 4. PIN RULE: Remove any move that would expose own commander to face-off.
            # This covers:
            #   a) A blocker piece moving away, leaving commanders in direct sight
            #   b) The Commander itself moving into a face-off position
            self.valid_moves = [
                m for m in self.valid_moves
                if not would_expose_commander_to_faceoff(self, piece, m['to'])
            ]

            # 5. FACE-OFF ESCAPE RESTRICTION: If commanders are already facing each
            # other (initial state or after a capture), the commander in face-off
            # cannot escape sideways (belt-and-suspenders on top of pin rule).
            blocked_dirs = get_commander_faceoff_blocked_dirs(piece, self)
            if blocked_dirs:
                self.valid_moves = [
                    m for m in self.valid_moves
                    if not self._move_is_in_dirs(piece.position, m['to'], blocked_dirs)
                ]
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
            
        self.combat_logs = []
            
        if move_data['type'] == MoveType.COMBINE:
            apply_combination(move_data['carrier'], move_data['passenger'], self)
            self.combat_logs.append(f"Combined {move_data['passenger'].type.name} into {move_data['carrier'].type.name}")
            
        elif move_data['type'] == MoveType.CAPTURE:
            logs, scores = resolve_combat(self.selected_piece, (to_x, to_y), self)
            self.combat_logs.extend(logs)
            # Apply earned scores
            self.score_red  += scores.get(Color.RED,  0)
            self.score_blue += scores.get(Color.BLUE, 0)
            print(f"Current score: RED={self.score_red}, BLUE={self.score_blue}")
            
            # If not stand-still, move the attacker
            if not move_data.get('is_stand_still', False):
                if self.selected_piece in self.pieces:
                    self.selected_piece.move_to((to_x, to_y))
                    
            # Check AA for Air Force after moving
            if not move_data.get('is_stand_still', False):
                if apply_airforce_aa_interaction(self.selected_piece, (to_x, to_y), self):
                    self.combat_logs.append("AIRFORCE destroyed by entering AA Zone!")
                    
        else:
            # MoveType.MOVE
            self.selected_piece.move_to((to_x, to_y))
            if apply_airforce_aa_interaction(self.selected_piece, (to_x, to_y), self):
                self.combat_logs.append("AIRFORCE destroyed by entering AA Zone!")

        # Check win conditions after every move
        winner, condition = check_win_conditions(self, self.score_red, self.score_blue, self.mode)
        if winner is not None or condition == WinCondition.NONE:
            # Only act when there IS a winner
            if winner is not None:
                self.game_over = True
                self.winner_color = winner
                self.win_condition = condition
                print(f"Match finished: winner = {winner.name} ({condition})")

        self.check_heroic_promotion()
        self.switch_turn()
        return True

    def time_up(self):
        """Called by UI when the turn timer expires for the whole match."""
        winner, is_draw = determine_winner_by_score(self.score_red, self.score_blue)
        self.game_over = True
        self.winner_color = winner   # None if draw
        self.win_condition = WinCondition.TIME_UP
        print(f"Match finished (time up): winner={winner}, draw={is_draw}")
        print(f"UI switched from timer to score display")

    def check_heroic_promotion(self):
        pass

    def switch_turn(self):
        self.current_turn = Color.BLUE if self.current_turn == Color.RED else Color.RED
        self.unselect_piece()

    @staticmethod
    def _move_is_in_dirs(from_pos, to_pos, blocked_dirs):
        """Returns True if the move from_pos→to_pos is purely in one of blocked_dirs."""
        fx, fy = from_pos
        tx, ty = to_pos
        dx = tx - fx
        dy = ty - fy
        # Normalize to unit vector for comparison
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
        return (dx, dy) in blocked_dirs

