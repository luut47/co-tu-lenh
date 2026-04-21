import os
import threading

import pygame

from config import settings
from core.board import Board
from core.board_renderer import BoardRenderer
from core.bot_ai import get_bot_move
from core.move_rules import MoveType
from core.piece import Color
from core.turn_timer import TurnTimer
from services.player_achievement_service import PlayerAchievementService


class HumanVsBotHomeScreen:
    def __init__(self, screen, difficulty="normal"):
        self.screen = screen
        self.difficulty = difficulty
        self.font_small = pygame.font.SysFont(settings.FONT_NAME, 32)
        self.font_medium = pygame.font.SysFont(settings.FONT_NAME, 44)
        self.font_move = pygame.font.SysFont(settings.FONT_NAME, 16)

        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, "on_play_screen_backgroud_.png")).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))

        self.icon_human = pygame.image.load(os.path.join(settings.IMAGES_DIR, "icon_human.png")).convert_alpha()
        self.icon_human_2 = pygame.image.load(os.path.join(settings.IMAGES_DIR, "icon_human_2_.png")).convert_alpha()
        self.slide_time = pygame.image.load(os.path.join(settings.IMAGES_DIR, "slide_time_couting_.png")).convert_alpha()

        self.panel_right = pygame.image.load(os.path.join(settings.IMAGES_DIR, "panel_show_user_moved_.png")).convert_alpha()
        self.panel_detail = pygame.image.load(os.path.join(settings.IMAGES_DIR, "panel_show_user_moved_detail_.png")).convert_alpha()

        self.btn_surrender = pygame.image.load(os.path.join(settings.IMAGES_DIR, "btn_surrender.png")).convert_alpha()
        self.btn_undo = pygame.image.load(os.path.join(settings.IMAGES_DIR, "btn_bot_mode_undo_moved_.png")).convert_alpha()
        self.btn_invite_replay = pygame.image.load(os.path.join(settings.IMAGES_DIR, "btn_play_again_bot_.png")).convert_alpha()

        face_size = (50, 50)
        slide_size = (300, 60)
        panel_w, panel_h = 550, 750
        detail_w, detail_h = 460, 200
        btn_w, btn_h = 180, 60
        btn_undo_w, btn_undo_h = 100, 60

        self.icon_human = pygame.transform.smoothscale(self.icon_human, face_size)
        self.icon_human_2 = pygame.transform.smoothscale(self.icon_human_2, face_size)
        self.slide_time = pygame.transform.smoothscale(self.slide_time, slide_size)

        self.panel_right = pygame.transform.smoothscale(self.panel_right, (panel_w, panel_h))
        self.panel_detail = pygame.transform.smoothscale(self.panel_detail, (detail_w, detail_h))

        self.btn_surrender = pygame.transform.smoothscale(self.btn_surrender, (btn_w, btn_h))
        self.btn_undo = pygame.transform.smoothscale(self.btn_undo, (btn_undo_w, btn_undo_h))
        self.btn_invite_replay = pygame.transform.smoothscale(self.btn_invite_replay, (btn_w, btn_h))

        detail_icon_size = (40, 40)
        self.small_icon_human = pygame.transform.smoothscale(self.icon_human, detail_icon_size)
        self.small_icon_human_2 = pygame.transform.smoothscale(self.icon_human_2, detail_icon_size)

        board_w = 800
        board_h = int(board_w * (11 / 10))
        board_x = 200
        board_y = (settings.HEIGHT - board_h) // 2

        self.board = Board()
        self.board_renderer = BoardRenderer(pygame.Rect(board_x, board_y, board_w, board_h))

        self.match_finished = False
        self.show_winner_overlay = False
        self.winner = None

        self.human_info = {"name": "Human", "side": Color.RED}
        self.bot_info = {"name": f"Bot ({difficulty.title()})", "side": Color.BLUE}
        self.p1_info = self.bot_info
        self.p2_info = self.human_info
        self.p1_moves = []
        self.p2_moves = []
        self.timer_p1 = TurnTimer(60)
        self.timer_p2 = TurnTimer(60)
        self.achievement_service = PlayerAchievementService()

        self.bot_color = Color.BLUE
        self.bot_delay_ms = {
            "easy": 120,
            "normal": 180,
            "hard": 220,
            "asian": 260,
        }.get(difficulty, 180)
        self.bot_turn_ready_at = 0
        self.bot_worker = None
        self.bot_result = None
        self.bot_result_lock = threading.Lock()
        self.bot_request_id = 0
        self.undo_stack = []

        self.panel_right_rect = self.panel_right.get_rect(right=settings.WIDTH - 200, centery=settings.HEIGHT // 2)

        padding_y = 40
        self.panel_detail_top_rect = self.panel_detail.get_rect(
            midtop=(self.panel_right_rect.centerx, self.panel_right_rect.top + padding_y + 10)
        )
        self.panel_detail_bottom_rect = self.panel_detail.get_rect(
            midbottom=(self.panel_right_rect.centerx, self.panel_right_rect.bottom - padding_y)
        )

        self.small_icon1_rect = self.small_icon_human.get_rect(
            topleft=(self.panel_detail_top_rect.left, self.panel_detail_top_rect.top - 40)
        )
        self.small_icon2_rect = self.small_icon_human_2.get_rect(
            topleft=(self.panel_detail_bottom_rect.left, self.panel_detail_bottom_rect.top - 40)
        )

        self.btn_invite_replay_rect = self.btn_invite_replay.get_rect(
            bottomright=(self.panel_right_rect.right - 20, settings.HEIGHT - 40)
        )
        self.btn_undo_rect = self.btn_undo.get_rect(
            bottomright=(self.btn_invite_replay_rect.left, settings.HEIGHT - 40)
        )
        self.btn_surrender_rect = self.btn_surrender.get_rect(
            bottomright=(self.btn_undo_rect.left, settings.HEIGHT - 40)
        )

        self.last_time = pygame.time.get_ticks()
        self._init_game_ui()
        self._queue_bot_turn()

    def _init_game_ui(self):
        self.icon_top_rect = self.icon_human.get_rect(topleft=(300, 30))
        self.name_top_label = self.font_medium.render(self.p1_info["name"], True, settings.BLACK)
        self.name_top_rect = self.name_top_label.get_rect(midleft=(self.icon_top_rect.right + 20, self.icon_top_rect.centery))
        self.slide_time_top_rect = self.slide_time.get_rect(center=(settings.WIDTH // 2, self.icon_top_rect.centery))

        self.icon_bottom_rect = self.icon_human_2.get_rect(bottomleft=(300, settings.HEIGHT - 30))
        self.name_bottom_label = self.font_medium.render(self.p2_info["name"], True, settings.BLACK)
        self.name_bottom_rect = self.name_bottom_label.get_rect(
            midleft=(self.icon_bottom_rect.right + 20, self.icon_bottom_rect.centery)
        )
        self.slide_time_bottom_rect = self.slide_time.get_rect(center=(settings.WIDTH // 2, self.icon_bottom_rect.centery))

        self.timer_p1.reset()
        self.timer_p2.reset()
        self._sync_timers()
        self.last_time = pygame.time.get_ticks()

    def update(self):
        if self.show_winner_overlay:
            self.last_time = pygame.time.get_ticks()
            return

        if self.board.game_over and not self.match_finished:
            self._end_game(self.board.winner_color)
            return

        if self.match_finished:
            self.last_time = pygame.time.get_ticks()
            return

        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0
        self.last_time = current_time

        if self.board.current_turn == self.p1_info["side"]:
            self.timer_p1.update(dt)
            if self.timer_p1.is_time_out():
                self.board.time_up()
                self._end_game(self.board.winner_color)
                return
        else:
            self.timer_p2.update(dt)
            if self.timer_p2.is_time_out():
                self.board.time_up()
                self._end_game(self.board.winner_color)
                return

        self._maybe_run_bot_turn()

    def _sync_timers(self):
        self.timer_p1.reset()
        self.timer_p2.reset()

        if self.board.current_turn == self.p1_info["side"]:
            self.timer_p1.start()
            self.timer_p2.stop()
        else:
            self.timer_p2.start()
            self.timer_p1.stop()

    def _end_game(self, winner_color):
        self.match_finished = True
        self.show_winner_overlay = True
        self.timer_p1.stop()
        self.timer_p2.stop()

        if winner_color is None:
            self.winner = "Hoa"
            return

        if self.human_info["side"] == winner_color:
            w_name = self.human_info["name"]
            l_name = self.bot_info["name"]
        else:
            w_name = self.bot_info["name"]
            l_name = self.human_info["name"]

        self.winner = w_name
        self.achievement_service.record_win(w_name)
        self.achievement_service.record_loss(l_name)

    def reset_match_state(self):
        self.board = Board()
        self.match_finished = False
        self.show_winner_overlay = False
        self.winner = None
        self.p1_moves = []
        self.p2_moves = []
        self.bot_worker = None
        self.bot_result = None
        self.bot_request_id = 0
        self.undo_stack = []
        self._init_game_ui()
        self._queue_bot_turn()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        self.screen.blit(self.icon_human, self.icon_top_rect)
        self.screen.blit(self.name_top_label, self.name_top_rect)
        self.screen.blit(self.slide_time, self.slide_time_top_rect)
        if self.match_finished:
            p1_score = self.board.score_blue
            t1_text = str(p1_score)
            t1_color = (220, 50, 50)
        else:
            t1_text = self.timer_p1.get_time_string()
            t1_color = settings.BLACK
        t1_label = self.font_medium.render(t1_text, True, t1_color)
        self.screen.blit(t1_label, t1_label.get_rect(center=self.slide_time_top_rect.center))

        self.screen.blit(self.icon_human_2, self.icon_bottom_rect)
        self.screen.blit(self.name_bottom_label, self.name_bottom_rect)
        self.screen.blit(self.slide_time, self.slide_time_bottom_rect)
        if self.match_finished:
            p2_score = self.board.score_red
            t2_text = str(p2_score)
            t2_color = (220, 50, 50)
        else:
            t2_text = self.timer_p2.get_time_string()
            t2_color = settings.BLACK
        t2_label = self.font_medium.render(t2_text, True, t2_color)
        self.screen.blit(t2_label, t2_label.get_rect(center=self.slide_time_bottom_rect.center))

        self.screen.blit(self.panel_right, self.panel_right_rect)

        self.screen.blit(self.panel_detail, self.panel_detail_top_rect)
        self.screen.blit(self.small_icon_human, self.small_icon1_rect)
        lbl_n1 = self.font_small.render(self.p1_info["name"], True, settings.BLACK)
        self.screen.blit(lbl_n1, (self.small_icon1_rect.right + 10, self.small_icon1_rect.top + 10))
        self._draw_moves(self.p1_moves, self.small_icon1_rect.bottom + 15, self.panel_detail_top_rect.left + 30)

        self.screen.blit(self.panel_detail, self.panel_detail_bottom_rect)
        self.screen.blit(self.small_icon_human_2, self.small_icon2_rect)
        lbl_n2 = self.font_small.render(self.p2_info["name"], True, settings.BLACK)
        self.screen.blit(lbl_n2, (self.small_icon2_rect.right + 10, self.small_icon2_rect.top + 10))
        self._draw_moves(self.p2_moves, self.small_icon2_rect.bottom + 15, self.panel_detail_bottom_rect.left + 30)

        self.board_renderer.draw(self.screen, self.board)

        self.screen.blit(self.btn_surrender, self.btn_surrender_rect)
        if self.undo_stack and not self.match_finished:
            self.screen.blit(self.btn_undo, self.btn_undo_rect)
        if self.match_finished:
            self.screen.blit(self.btn_invite_replay, self.btn_invite_replay_rect)

        if self.show_winner_overlay:
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont(settings.FONT_NAME, 72, bold=True)
            if self.winner == "Hoa":
                overlay_text = "Van dau ket thuc voi ty so hoa"
            else:
                overlay_text = f"Chuc mung nguoi choi {self.winner} thang"
            msg = font_big.render(overlay_text, True, (255, 215, 0))
            self.screen.blit(msg, msg.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))

            font_small = pygame.font.SysFont(settings.FONT_NAME, 32)
            msg2 = font_small.render("Nhan chuot de tiep tuc xem ban co", True, (255, 255, 255))
            self.screen.blit(msg2, msg2.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 60)))

    def _draw_moves(self, moves_list, start_y, start_x):
        display_moves = moves_list[-7:]
        y = start_y
        for move in display_moves:
            txt = self.font_move.render(move, True, (255, 255, 255))
            self.screen.blit(txt, (start_x, y + 40))
            y += 20

    def handle_event(self, event):
        if self.show_winner_overlay:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_invite_replay_rect.collidepoint(event.pos):
                    self.reset_match_state()
                else:
                    self.show_winner_overlay = False
            return self

        if self.match_finished:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_invite_replay_rect.collidepoint(event.pos):
                    self.reset_match_state()
            return self

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.btn_surrender_rect.collidepoint(event.pos):
                self._end_game(Color.BLUE)
                return self
            if event.button == 1 and self.btn_undo_rect.collidepoint(event.pos):
                self._undo_last_round()
                return self

            if self.board.current_turn != self.human_info["side"]:
                return self

            if event.button in (1, 3):
                self._handle_human_click(event.pos, event.button)

        return self

    def _handle_human_click(self, mouse_pos, mouse_button):
        board_pos = self.board_renderer.get_board_pos(*mouse_pos)
        if not board_pos:
            return

        x, y = board_pos
        if self.board.selected_piece:
            piece = self.board.selected_piece
            from_pos = piece.position
            matching_moves = self.board.get_matching_moves(x, y)
            preferred_type = None

            if mouse_button == 1:
                if any(move["type"] == MoveType.CAPTURE_REPLACE for move in matching_moves):
                    preferred_type = MoveType.CAPTURE_REPLACE
            elif mouse_button == 3:
                if any(move["type"] == MoveType.AIRSTRIKE_RETURN for move in matching_moves):
                    preferred_type = MoveType.AIRSTRIKE_RETURN

            undo_snapshot = self._capture_undo_state()
            success = self.board.move_piece(x, y, preferred_type=preferred_type)
            if success:
                self.undo_stack.append(undo_snapshot)
                self._append_logs(piece.color, piece, from_pos, x, y)
                self._after_turn_change()
            elif mouse_button == 1:
                clicked_piece = self.board.get_piece_at(x, y)
                self.board.select_piece(clicked_piece)
        elif mouse_button == 1:
            clicked_piece = self.board.get_piece_at(x, y)
            self.board.select_piece(clicked_piece)

    def _append_logs(self, color, piece, from_pos, x, y):
        logs_to_add = self.board.combat_logs if self.board.combat_logs else [f"{piece.type.name}{from_pos} -> {(x, y)}"]
        target_moves = self.p1_moves if color == self.p1_info["side"] else self.p2_moves
        target_moves.extend(logs_to_add)

    def _after_turn_change(self):
        if self.board.game_over:
            self._end_game(self.board.winner_color)
            return
        self._sync_timers()
        self._queue_bot_turn()

    def _maybe_run_bot_turn(self):
        if self.match_finished or self.board.game_over or self.board.current_turn != self.bot_color:
            return

        bot_move = self._consume_bot_result()
        if bot_move is not None:
            self._apply_bot_move(bot_move)
            return

        if self.bot_worker and self.bot_worker.is_alive():
            return
        if pygame.time.get_ticks() < self.bot_turn_ready_at:
            return

        self._start_bot_search()

    def _start_bot_search(self):
        board_snapshot = self.board.clone()
        depth = self._difficulty_depth()
        self.bot_request_id += 1
        request_id = self.bot_request_id

        def _worker():
            move = get_bot_move(board_snapshot, self.bot_color, depth)
            with self.bot_result_lock:
                self.bot_result = (request_id, move)

        self.bot_worker = threading.Thread(target=_worker, daemon=True)
        self.bot_worker.start()

    def _consume_bot_result(self):
        with self.bot_result_lock:
            if self.bot_result is None:
                return None
            request_id, move = self.bot_result
            if request_id != self.bot_request_id:
                return None
            self.bot_result = None
            return move

    def _apply_bot_move(self, bot_move):
        if bot_move is None:
            self._end_game(self.human_info["side"])
            return

        piece = self.board.find_piece_by_id(bot_move.piece_id)
        if piece is None:
            return

        from_pos = piece.position
        self.board.select_piece(piece)
        success = self.board.move_piece(bot_move.to_x, bot_move.to_y, preferred_type=bot_move.move_type)
        if not success:
            return

        self._append_logs(piece.color, piece, from_pos, bot_move.to_x, bot_move.to_y)
        self._after_turn_change()

    def _queue_bot_turn(self):
        if self.board.current_turn == self.bot_color:
            self.bot_turn_ready_at = pygame.time.get_ticks() + self.bot_delay_ms
            with self.bot_result_lock:
                self.bot_result = None

    def _difficulty_depth(self):
        return {
            "easy": 1,
            "normal": 2,
            "hard": 3,
            "asian": 4,
        }.get(self.difficulty, 2)

    def _capture_undo_state(self):
        return {
            "board": self.board.clone(),
            "p1_moves": list(self.p1_moves),
            "p2_moves": list(self.p2_moves),
            "timer_p1_remaining": self.timer_p1.remaining_time,
            "timer_p2_remaining": self.timer_p2.remaining_time,
        }

    def _undo_last_round(self):
        if not self.undo_stack:
            return

        snapshot = self.undo_stack.pop()
        self.board = snapshot["board"].clone()
        self.p1_moves = list(snapshot["p1_moves"])
        self.p2_moves = list(snapshot["p2_moves"])
        self.timer_p1.remaining_time = snapshot["timer_p1_remaining"]
        self.timer_p2.remaining_time = snapshot["timer_p2_remaining"]
        self.match_finished = False
        self.show_winner_overlay = False
        self.winner = None
        self.board.selected_piece = None
        self.board.valid_moves = []

        self.bot_request_id += 1
        self.bot_worker = None
        self.bot_turn_ready_at = 0
        with self.bot_result_lock:
            self.bot_result = None

        self.timer_p1.stop()
        self.timer_p2.stop()
        if self.board.current_turn == self.p1_info["side"]:
            self.timer_p1.start()
        else:
            self.timer_p2.start()
        self.last_time = pygame.time.get_ticks()
