import pygame
import sys
from config import settings
from ui.home_screen import HomeScreen

def main():
    pygame.init()
    # Create window (resizable)
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Cờ Tư Lệnh")
    clock = pygame.time.Clock()
    
    # Create a logical surface fixed to 1920x1080
    logical_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    
    current_screen = HomeScreen(logical_surface)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Map mouse events from actual window to logical surface
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                window_w, window_h = screen.get_size()
                aspect_ratio = settings.WIDTH / settings.HEIGHT
                window_ratio = window_w / window_h
                
                if window_ratio > aspect_ratio:
                    new_h = window_h
                    new_w = int(aspect_ratio * new_h)
                    offset_x = (window_w - new_w) // 2
                    offset_y = 0
                else:
                    new_w = window_w
                    new_h = int(new_w / aspect_ratio)
                    offset_x = 0
                    offset_y = (window_h - new_h) // 2
                
                if new_w > 0 and new_h > 0:
                    scale_x = settings.WIDTH / new_w
                    scale_y = settings.HEIGHT / new_h
                    
                    # Check if mouse is within the logical area
                    mx, my = event.pos
                    if offset_x <= mx <= offset_x + new_w and offset_y <= my <= offset_y + new_h:
                        logical_event = pygame.event.Event(event.type, **event.dict)
                        logical_x = int((mx - offset_x) * scale_x)
                        logical_y = int((my - offset_y) * scale_y)
                        logical_event.pos = (logical_x, logical_y)
                        
                        if event.type == pygame.MOUSEMOTION and hasattr(event, 'rel'):
                            logical_event.rel = (int(event.rel[0] * scale_x), int(event.rel[1] * scale_y))
                        
                        next_screen = current_screen.handle_event(logical_event)
                    else:
                        next_screen = None
                else:
                    next_screen = None
            else:
                next_screen = current_screen.handle_event(event)
                
            if next_screen:
                current_screen = next_screen
            
        # Update logical state if screen has update method
        if hasattr(current_screen, 'update'):
            current_screen.update()

        # Draw on the logical surface
        current_screen.draw()
        
        # Scale logical surface to current window size preserving aspect ratio
        window_w, window_h = screen.get_size()
        aspect_ratio = settings.WIDTH / settings.HEIGHT
        window_ratio = window_w / window_h
        
        if window_ratio > aspect_ratio:
            new_h = window_h
            new_w = int(aspect_ratio * new_h)
            offset_x = (window_w - new_w) // 2
            offset_y = 0
        else:
            new_w = window_w
            new_h = int(new_w / aspect_ratio)
            offset_x = 0
            offset_y = (window_h - new_h) // 2
            
        scaled_surface = pygame.transform.smoothscale(logical_surface, (new_w, new_h))
        
        # Clear screen with black for letterboxing
        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (offset_x, offset_y))
        
        pygame.display.flip()
        clock.tick(settings.FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
