import pygame
from config.constants import WIDTH, HEIGHT, FPS
from ui.game_screen import GameScreen


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cờ tư lệnh - Sidebar UI")
    clock = pygame.time.Clock()

    game_screen = GameScreen(screen)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game_screen.handle_event(event)

        game_screen.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
