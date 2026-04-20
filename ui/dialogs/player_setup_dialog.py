import pygame
import random
from core.piece import Color

class PlayerSetupDialog:
    def __init__(self, surface, font_name, width=600, height=500):
        self.surface = surface
        self.width = width
        self.height = height
        self.font_large = pygame.font.SysFont(font_name, 48, bold=True)
        self.font_medium = pygame.font.SysFont(font_name, 36)
        self.font_small = pygame.font.SysFont(font_name, 24)

        # Center dialog
        sw, sh = surface.get_size()
        self.rect = pygame.Rect((sw - width) // 2, (sh - height) // 2, width, height)

        self.p1_name = ""
        self.p2_name = ""
        self.p1_active = False
        self.p2_active = False

        self.p1_side = None # None means random
        self.p2_side = None # None means random

        self.error_message = ""

        # UI elements rects
        pad_x = 40
        pad_y = 80
        input_w = 200
        input_h = 40

        # Player 1 (Left)
        p1_x = self.rect.left + pad_x
        p1_y = self.rect.top + pad_y
        self.p1_input_rect = pygame.Rect(p1_x, p1_y + 40, input_w, input_h)
        self.p1_btn_blue = pygame.Rect(p1_x, p1_y + 100, 90, 40)
        self.p1_btn_red = pygame.Rect(p1_x + 110, p1_y + 100, 90, 40)
        self.p1_btn_random = pygame.Rect(p1_x, p1_y + 150, 200, 40)

        # Player 2 (Right)
        p2_x = self.rect.right - pad_x - input_w
        p2_y = self.rect.top + pad_y
        self.p2_input_rect = pygame.Rect(p2_x, p2_y + 40, input_w, input_h)
        self.p2_btn_blue = pygame.Rect(p2_x, p2_y + 100, 90, 40)
        self.p2_btn_red = pygame.Rect(p2_x + 110, p2_y + 100, 90, 40)
        self.p2_btn_random = pygame.Rect(p2_x, p2_y + 150, 200, 40)

        # Buttons (Bottom)
        btn_w = 150
        btn_h = 50
        self.btn_start = pygame.Rect(self.rect.centerx - btn_w - 20, self.rect.bottom - 80, btn_w, btn_h)
        self.btn_cancel = pygame.Rect(self.rect.centerx + 20, self.rect.bottom - 80, btn_w, btn_h)

        self.done = False
        self.cancelled = False
        self.result = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                pos = event.pos
                
                # Active inputs
                self.p1_active = self.p1_input_rect.collidepoint(pos)
                self.p2_active = self.p2_input_rect.collidepoint(pos)

                # Player 1 sides
                if self.p1_btn_blue.collidepoint(pos): self.p1_side = Color.BLUE
                elif self.p1_btn_red.collidepoint(pos): self.p1_side = Color.RED
                elif self.p1_btn_random.collidepoint(pos): self.p1_side = None

                # Player 2 sides
                if self.p2_btn_blue.collidepoint(pos): self.p2_side = Color.BLUE
                elif self.p2_btn_red.collidepoint(pos): self.p2_side = Color.RED
                elif self.p2_btn_random.collidepoint(pos): self.p2_side = None

                # Actions
                if self.btn_start.collidepoint(pos):
                    self._try_start()
                elif self.btn_cancel.collidepoint(pos):
                    self.cancelled = True
                    self.done = True

        elif event.type == pygame.KEYDOWN:
            if self.p1_active:
                if event.key == pygame.K_BACKSPACE:
                    self.p1_name = self.p1_name[:-1]
                elif len(self.p1_name) < 15 and event.unicode.isprintable():
                    self.p1_name += event.unicode
            elif self.p2_active:
                if event.key == pygame.K_BACKSPACE:
                    self.p2_name = self.p2_name[:-1]
                elif len(self.p2_name) < 15 and event.unicode.isprintable():
                    self.p2_name += event.unicode

    def _try_start(self):
        n1 = self.p1_name.strip()
        n2 = self.p2_name.strip()

        if not n1 or not n2:
            self.error_message = "Usernames cannot be empty!"
            return

        if n1.lower() == n2.lower():
            self.error_message = "Usernames must be different!"
            return

        if self.p1_side is not None and self.p1_side == self.p2_side:
            self.error_message = "Players cannot choose the same side!"
            return

        # Resolve random sides
        s1 = self.p1_side
        s2 = self.p2_side

        if s1 is None and s2 is None:
            s1 = random.choice([Color.BLUE, Color.RED])
            s2 = Color.RED if s1 == Color.BLUE else Color.BLUE
        elif s1 is None:
            s1 = Color.RED if s2 == Color.BLUE else Color.BLUE
        elif s2 is None:
            s2 = Color.RED if s1 == Color.BLUE else Color.BLUE

        self.result = {
            "p1_name": n1,
            "p1_side": s1,
            "p2_name": n2,
            "p2_side": s2
        }
        self.done = True

    def draw(self):
        # Draw overlay background
        overlay = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.surface.blit(overlay, (0, 0))

        # Draw dialog box
        pygame.draw.rect(self.surface, (240, 240, 240), self.rect, border_radius=15)
        pygame.draw.rect(self.surface, (100, 100, 100), self.rect, 3, border_radius=15)

        # Title
        title = self.font_large.render("PLAYER SETUP", True, (50, 50, 50))
        self.surface.blit(title, title.get_rect(center=(self.rect.centerx, self.rect.top + 30)))

        # Player 1 Section
        self._draw_player_section("Player 1", self.p1_input_rect, self.p1_name, self.p1_active,
                                  self.p1_btn_blue, self.p1_btn_red, self.p1_btn_random, self.p1_side)

        # Player 2 Section
        self._draw_player_section("Player 2", self.p2_input_rect, self.p2_name, self.p2_active,
                                  self.p2_btn_blue, self.p2_btn_red, self.p2_btn_random, self.p2_side)

        # Error message
        if self.error_message:
            err = self.font_small.render(self.error_message, True, (255, 0, 0))
            self.surface.blit(err, err.get_rect(center=(self.rect.centerx, self.btn_start.top - 20)))

        # Buttons
        self._draw_button(self.btn_start, "Start", (76, 175, 80), (255, 255, 255))
        self._draw_button(self.btn_cancel, "Cancel", (244, 67, 54), (255, 255, 255))

    def _draw_player_section(self, label, input_rect, name, active, btn_blue, btn_red, btn_rand, side):
        # Label
        lbl = self.font_medium.render(label, True, (50, 50, 50))
        self.surface.blit(lbl, (input_rect.left, input_rect.top - lbl.get_height() - 10))

        # Input box
        color = (0, 120, 215) if active else (150, 150, 150)
        pygame.draw.rect(self.surface, (255, 255, 255), input_rect)
        pygame.draw.rect(self.surface, color, input_rect, 2)
        txt = self.font_medium.render(name, True, (0, 0, 0))
        txt_y = input_rect.top + (input_rect.height - txt.get_height()) // 2
        self.surface.blit(txt, (input_rect.left + 10, txt_y))

        # Side buttons
        self._draw_toggle_button(btn_blue, "Blue", (100, 149, 237), side == Color.BLUE)
        self._draw_toggle_button(btn_red, "Red", (255, 99, 71), side == Color.RED)
        self._draw_toggle_button(btn_rand, "Random", (180, 180, 180), side is None)

    def _draw_button(self, rect, text, bg_color, text_color):
        pygame.draw.rect(self.surface, bg_color, rect, border_radius=8)
        lbl = self.font_medium.render(text, True, text_color)
        self.surface.blit(lbl, lbl.get_rect(center=rect.center))

    def _draw_toggle_button(self, rect, text, bg_color, is_selected):
        color = bg_color if is_selected else (220, 220, 220)
        pygame.draw.rect(self.surface, color, rect, border_radius=5)
        if is_selected:
            pygame.draw.rect(self.surface, (50, 50, 50), rect, 2, border_radius=5)
        lbl = self.font_small.render(text, True, (0, 0, 0))
        self.surface.blit(lbl, lbl.get_rect(center=rect.center))
