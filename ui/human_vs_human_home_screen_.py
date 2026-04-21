import pygame
import os
import sys
from config import settings
from core.board import Board
from core.board_renderer import BoardRenderer
from core.piece import Color
from core.move_rules import MoveType
from ui.dialogs.player_setup_dialog import PlayerSetupDialog
from ui.dialogs.swap_sides_dialog import SwapSidesDialog
from ui.dialogs.setting_menu import SettingMenu
from core.turn_timer import TurnTimer
from services.player_achievement_service import PlayerAchievementService
from services.sound_manager import SoundManager

class HumanVsHumanHomeScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.SysFont(settings.FONT_NAME, 32)
        self.font_medium = pygame.font.SysFont(settings.FONT_NAME, 44)
        self.font_move = pygame.font.SysFont(settings.FONT_NAME, 16)
        
        # Load images
        self.bg = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'on_play_screen_backgroud_.png')).convert()
        self.bg = pygame.transform.smoothscale(self.bg, (settings.WIDTH, settings.HEIGHT))
        
        self.icon_human = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'icon_human.png')).convert_alpha()
        self.icon_human_2 = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'icon_human_2_.png')).convert_alpha()
        self.slide_time = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'slide_time_couting_.png')).convert_alpha()
        
        self.panel_right = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'panel_show_user_moved_.png')).convert_alpha()
        self.panel_detail = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'panel_show_user_moved_detail_.png')).convert_alpha()
        
        self.btn_surrender = pygame.image.load(os.path.join(settings.IMAGES_DIR, 'btn_surrender.png')).convert_alpha()
        self.btn_invite_replay = pygame.image.load(os.path.join(settings.IMAGES_DIR,'btn_invite_replay.png')).convert_alpha()
        
        # Scale UI assets down to prevent overlapping
        face_size = (50, 50)
        slide_size = (300, 60)
        panel_w, panel_h = 550, 750
        detail_w, detail_h = 460, 200
        btn_w, btn_h = 180, 60
        
        self.icon_human = pygame.transform.smoothscale(self.icon_human, face_size)
        self.icon_human_2 = pygame.transform.smoothscale(self.icon_human_2, face_size)
        self.slide_time = pygame.transform.smoothscale(self.slide_time, slide_size)
        
        self.panel_right = pygame.transform.smoothscale(self.panel_right, (panel_w, panel_h))
        self.panel_detail = pygame.transform.smoothscale(self.panel_detail, (detail_w, detail_h))
        
        self.btn_surrender = pygame.transform.smoothscale(self.btn_surrender, (btn_w, btn_h))
        self.btn_invite_replay = pygame.transform.smoothscale(self.btn_invite_replay, (btn_w, btn_h))
        
        # Resize small icons for detail panel
        detail_icon_size = (40, 40)
        self.small_icon_human = pygame.transform.smoothscale(self.icon_human, detail_icon_size)
        self.small_icon_human_2 = pygame.transform.smoothscale(self.icon_human_2, detail_icon_size)
        
        # Core Game Board - Position on the left (original layout)
        board_w = 800
        board_h = int(board_w * (11 / 10))
        board_x = 200
        board_y = (settings.HEIGHT - board_h) // 2
        
        self.board = Board()
        self.board_renderer = BoardRenderer(pygame.Rect(board_x, board_y, board_w, board_h))

        self.player_setup_completed = False
        self.match_finished = False
        self.show_winner_overlay = False
        self.show_swap_dialog = False
        self.winner = None

        # Setup Dialogs
        self.setup_dialog = PlayerSetupDialog(self.screen, settings.FONT_NAME)
        self.swap_dialog = SwapSidesDialog(self.screen, settings.FONT_NAME)
        self.show_dialog = True
        
        # Game State
        self.p1_info = None # Blue side
        self.p2_info = None # Red side
        self.p1_moves = []
        self.p2_moves = []
        self.timer_p1 = TurnTimer(60)
        self.timer_p2 = TurnTimer(60)
        self.achievement_service = PlayerAchievementService()

        # Right Panel and Detail Rects
        self.panel_right_rect = self.panel_right.get_rect(right=settings.WIDTH - 200, centery=settings.HEIGHT // 2)
        
        padding_y = 40
        self.panel_detail_top_rect = self.panel_detail.get_rect(midtop=(self.panel_right_rect.centerx, self.panel_right_rect.top + padding_y + 10))
        self.panel_detail_bottom_rect = self.panel_detail.get_rect(midbottom=(self.panel_right_rect.centerx, self.panel_right_rect.bottom - padding_y))
        
        self.small_icon1_rect = self.small_icon_human.get_rect(topleft=(self.panel_detail_top_rect.left, self.panel_detail_top_rect.top - 40))
        self.small_icon2_rect = self.small_icon_human_2.get_rect(topleft=(self.panel_detail_bottom_rect.left, self.panel_detail_bottom_rect.top - 40))

        # Bottom Buttons
        self.btn_invite_replay_rect = self.btn_invite_replay.get_rect(bottomright=(self.panel_right_rect.right - 20, settings.HEIGHT - 40))
        self.btn_surrender_rect = self.btn_surrender.get_rect(bottomright=(self.btn_invite_replay_rect.left - 20, settings.HEIGHT - 40))

        # Time tracking for update()
        self.last_time = pygame.time.get_ticks()
        self.setting_menu = SettingMenu(self.screen)
        self.sound_manager = SoundManager()

    def _init_game_ui(self):
        # Called after dialog finishes
        # Determine who is top/bottom. Blue is top, Red is bottom.
        if self.p1_info['side'] == Color.BLUE:
            top_player = self.p1_info
            bottom_player = self.p2_info
        else:
            top_player = self.p2_info
            bottom_player = self.p1_info

        # Top Player UI (Blue)
        self.icon_top_rect = self.icon_human.get_rect(topleft=(300, 30))
        self.name_top_label = self.font_medium.render(top_player['name'], True, settings.BLACK)
        self.name_top_rect = self.name_top_label.get_rect(midleft=(self.icon_top_rect.right + 20, self.icon_top_rect.centery))
        self.slide_time_top_rect = self.slide_time.get_rect(center=(settings.WIDTH // 2, self.icon_top_rect.centery))
        
        # Bottom Player UI (Red)
        self.icon_bottom_rect = self.icon_human_2.get_rect(bottomleft=(300, settings.HEIGHT - 30))
        self.name_bottom_label = self.font_medium.render(bottom_player['name'], True, settings.BLACK)
        self.name_bottom_rect = self.name_bottom_label.get_rect(midleft=(self.icon_bottom_rect.right + 20, self.icon_bottom_rect.centery))
        self.slide_time_bottom_rect = self.slide_time.get_rect(center=(settings.WIDTH // 2, self.icon_bottom_rect.centery))

        # Reset timers
        self.timer_p1.reset()
        self.timer_p2.reset()
        
        # Start timer for whoever goes first
        if self.p1_info['side'] == self.board.current_turn:
            self.timer_p1.start()
            self.timer_p2.stop()
        else:
            self.timer_p2.start()
            self.timer_p1.stop()
            
        self.last_time = pygame.time.get_ticks()

    def update(self):
        if self.show_dialog or self.show_winner_overlay or self.show_swap_dialog:
            self.last_time = pygame.time.get_ticks()
            return

        # If board already detected a win, trigger end-game flow
        if self.board.game_over and not self.match_finished:
            self._end_game(self.board.winner_color)
            return

        if self.match_finished:
            self.last_time = pygame.time.get_ticks()
            return

        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0
        self.last_time = current_time

        # Check whose turn it is and update their timer
        if self.board.current_turn == self.p1_info['side']:
            self.timer_p1.update(dt)
            if self.timer_p1.is_time_out():
                print(f"{self.board.current_turn.name} turn ended -> switch to the other")
                self.board.switch_turn()
                self._sync_timers()
        else:
            self.timer_p2.update(dt)
            if self.timer_p2.is_time_out():
                print(f"{self.board.current_turn.name} turn ended -> switch to the other")
                self.board.switch_turn()
                self._sync_timers()

    def _sync_timers(self):
        self.timer_p1.reset()
        self.timer_p2.reset()
        
        # Start the timer for whoever's turn it is now
        if self.board.current_turn == self.p1_info['side']:
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
        
        w_name = ""
        l_name = ""
        if self.p1_info['side'] == winner_color:
            w_name = self.p1_info['name']
            l_name = self.p2_info['name']
        else:
            w_name = self.p2_info['name']
            l_name = self.p1_info['name']
            
        self.winner = w_name
        self.achievement_service.record_win(w_name)
        self.achievement_service.record_loss(l_name)
        print(f"Match finished, winner = {self.winner}")

    def reset_match_state(self):
        print("Replay clicked -> reset board state only")
        self.board = Board()
        self.match_finished = False
        self.show_winner_overlay = False
        self.winner = None
        self.p1_moves = []
        self.p2_moves = []
        self._init_game_ui()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        
        if self.show_dialog:
            self.setup_dialog.draw()
            return
            
        # Top Player (Blue)
        self.screen.blit(self.icon_human, self.icon_top_rect)
        self.screen.blit(self.name_top_label, self.name_top_rect)
        self.screen.blit(self.slide_time, self.slide_time_top_rect)
        # After game ends → show score instead of timer
        if self.match_finished:
            p1_score = self.board.score_red if self.p1_info['side'] == Color.RED else self.board.score_blue
            t1_text = str(p1_score)
            t1_color = (220, 50, 50)
        else:
            t1_text = self.timer_p1.get_time_string()
            t1_color = settings.BLACK
        t1_label = self.font_medium.render(t1_text, True, t1_color)
        self.screen.blit(t1_label, t1_label.get_rect(center=self.slide_time_top_rect.center))
        
        # Bottom Player (Red)
        self.screen.blit(self.icon_human_2, self.icon_bottom_rect)
        self.screen.blit(self.name_bottom_label, self.name_bottom_rect)
        self.screen.blit(self.slide_time, self.slide_time_bottom_rect)
        if self.match_finished:
            p2_score = self.board.score_red if self.p2_info['side'] == Color.RED else self.board.score_blue
            t2_text = str(p2_score)
            t2_color = (220, 50, 50)
        else:
            t2_text = self.timer_p2.get_time_string()
            t2_color = settings.BLACK
        t2_label = self.font_medium.render(t2_text, True, t2_color)
        self.screen.blit(t2_label, t2_label.get_rect(center=self.slide_time_bottom_rect.center))
        
        # Right Panel
        self.screen.blit(self.panel_right, self.panel_right_rect)
        
        # Detail Top
        self.screen.blit(self.panel_detail, self.panel_detail_top_rect)
        self.screen.blit(self.small_icon_human, self.small_icon1_rect)
        lbl_n1 = self.font_small.render("Player 1", True, settings.BLACK)
        self.screen.blit(lbl_n1, (self.small_icon1_rect.right + 10, self.small_icon1_rect.top + 10))
        self._draw_moves(self.p1_moves, self.small_icon1_rect.bottom + 15, self.panel_detail_top_rect.left + 30)
        
        # Detail Bottom
        self.screen.blit(self.panel_detail, self.panel_detail_bottom_rect)
        self.screen.blit(self.small_icon_human_2, self.small_icon2_rect)
        lbl_n2 = self.font_small.render("Player 2", True, settings.BLACK)
        self.screen.blit(lbl_n2, (self.small_icon2_rect.right + 10, self.small_icon2_rect.top + 10))
        self._draw_moves(self.p2_moves, self.small_icon2_rect.bottom + 15, self.panel_detail_bottom_rect.left + 30)
        
        # Board
        self.board_renderer.draw(self.screen, self.board)

        self.setting_menu.draw(self.sound_manager.is_sound_on())
        
        # Bottom Buttons
        self.screen.blit(self.btn_surrender, self.btn_surrender_rect)
        if self.match_finished:
            self.screen.blit(self.btn_invite_replay, self.btn_invite_replay_rect)

        if self.show_winner_overlay:
            # Draw Game Over Overlay
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            font_big = pygame.font.SysFont(settings.FONT_NAME, 72, bold=True)
            msg = font_big.render(f"Chúc mừng người chơi {self.winner} thắng", True, (255, 215, 0))
            self.screen.blit(msg, msg.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))

            font_small = pygame.font.SysFont(settings.FONT_NAME, 32)
            msg2 = font_small.render("Nhấn chuột để tiếp tục xem bàn cờ", True, (255, 255, 255))
            self.screen.blit(msg2, msg2.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 60)))

        if self.show_swap_dialog:
            self.swap_dialog.draw()
        
    def _draw_moves(self, moves_list, start_y, start_x):
        # Draw up to 6 most recent moves
        max_moves = 7
        display_moves = moves_list[-max_moves:]
        y = start_y
        for move in display_moves:
            txt = self.font_move.render(move, True, (255, 255, 255))
            self.screen.blit(txt, (start_x, y + 40))
            y += 20

    def handle_event(self, event):
        if self.show_dialog:
            self.setup_dialog.handle_event(event)
            if self.setup_dialog.done:
                if self.setup_dialog.cancelled:
                    # Return to main menu
                    from ui.home_screen import HomeScreen
                    return HomeScreen(self.screen)
                else:
                    self.show_dialog = False
                    self.player_setup_completed = True
                    print("Player setup completed")
                    res = self.setup_dialog.result
                    self.p1_info = {'name': res['p1_name'], 'side': res['p1_side']}
                    self.p2_info = {'name': res['p2_name'], 'side': res['p2_side']}
                    self._init_game_ui()
            return self

        if self.show_winner_overlay:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.show_winner_overlay = False
                print("Winner overlay hidden")
            return self

        if self.show_swap_dialog:
            self.swap_dialog.handle_event(event)
            if self.swap_dialog.done:
                self.show_swap_dialog = False
                if self.swap_dialog.result:
                    self.p1_info['side'], self.p2_info['side'] = self.p2_info['side'], self.p1_info['side']
                    print("Sides swapped")
                self.reset_match_state()
            return self

        setting_action = self.setting_menu.handle_event(event)
        if setting_action == "toggle":
            self.sound_manager.play_button()
            return self

        if setting_action == "continue":
            self.sound_manager.play_button()
            return self

        if setting_action == "sound":
            self.sound_manager.play_button()
            self.sound_manager.toggle_sound()
            return self

        if setting_action == "home":
            self.sound_manager.play_button()
            from ui.home_screen import HomeScreen
            return HomeScreen(self.screen)

        if self.match_finished:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_invite_replay_rect.collidepoint(event.pos):
                    self.sound_manager.play_button()
                    self.show_swap_dialog = True
                    self.swap_dialog.reset()
            return self

        if self.setting_menu.is_open:
            return self

        # Normal game interaction
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                if self.btn_surrender_rect.collidepoint(mouse_pos):
                    self.sound_manager.play_button()
                    # Current player surrenders
                    winner_color = Color.BLUE if self.board.current_turn == Color.RED else Color.RED
                    self._end_game(winner_color)
                    return self

            if event.button in (1, 3):
                mouse_pos = event.pos
                board_pos = self.board_renderer.get_board_pos(*mouse_pos)
                if board_pos:
                    x, y = board_pos
                    if self.board.selected_piece:
                        piece = self.board.selected_piece
                        from_pos = piece.position
                        matching_moves = self.board.get_matching_moves(x, y)
                        preferred_type = None

                        if event.button == 1:
                            if any(move["type"] == MoveType.CAPTURE_REPLACE for move in matching_moves):
                                preferred_type = MoveType.CAPTURE_REPLACE
                        elif event.button == 3:
                            if any(move["type"] == MoveType.AIRSTRIKE_RETURN for move in matching_moves):
                                preferred_type = MoveType.AIRSTRIKE_RETURN

                        success = self.board.move_piece(x, y, preferred_type=preferred_type)
                        if success:
                            if preferred_type == MoveType.CAPTURE_REPLACE:
                                self.sound_manager.play_eat()
                            else:
                                self.sound_manager.play_move()
                            logs_to_add = self.board.combat_logs if self.board.combat_logs else [f"{piece.type.name}{from_pos} -> {(x, y)}"]
                            for log in logs_to_add:
                                if piece.color == self.p1_info['side']:
                                    self.p1_moves.append(log)
                                else:
                                    self.p2_moves.append(log)
                            self._sync_timers()
                        elif event.button == 1:
                            clicked_piece = self.board.get_piece_at(x, y)
                            self.board.select_piece(clicked_piece)
                    elif event.button == 1:
                        clicked_piece = self.board.get_piece_at(x, y)
                        self.board.select_piece(clicked_piece)
        return self
