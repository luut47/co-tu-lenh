import pygame
import sys
from config import settings
from ui.home_screen import HomeScreen

def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption("Cờ Tư Lệnh")
    clock = pygame.time.Clock()
    
    homescreen = HomeScreen(screen)
    
    # Save a screenshot for verification (remove this later or keep for debugging)
    # pygame.image.save(screen, "screenshot_test.png")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            homescreen.handle_event(event)
            
        homescreen.draw()
        pygame.display.flip()
        clock.tick(settings.FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
