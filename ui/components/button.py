import pygame
from config.constants import WHITE


class Button:
    def __init__(self, rect, text, font, fill_color, edge_color, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.fill_color = fill_color
        self.edge_color = edge_color
        self.text_color = text_color

    def draw(self, screen):
        shadow_rect = self.rect.move(0, 3)
        pygame.draw.rect(screen, (40, 60, 75), shadow_rect, border_radius=8)
        pygame.draw.rect(screen, self.fill_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.edge_color, self.rect, 2, border_radius=8)

        highlight = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.w - 6, max(10, self.rect.h // 2 - 2))
        s = pygame.Surface((highlight.w, highlight.h), pygame.SRCALPHA)
        s.fill((255, 255, 255, 28))
        screen.blit(s, highlight.topleft)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_click(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )
