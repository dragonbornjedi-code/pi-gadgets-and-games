import pygame
import sys
from framework.input.input_manager import InputManager
from framework.rendering.display_manager import DisplayManager

def main():
    pygame.init()
    pygame.joystick.init()
    
    display = DisplayManager()
    inputs = InputManager()
    font = pygame.font.SysFont(None, 24)
    
    joy = pygame.joystick.Joystick(0)
    joy.init()
    
    running = True
    while running:
        # Minimal event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        display.screen.fill((0, 0, 0))
        
        # Draw status
        text = font.render(f"Controller: {joy.get_name()}", True, (255, 255, 255))
        display.screen.blit(text, (10, 20))
        
        # Check buttons 0-15
        y = 50
        for i in range(joy.get_numbuttons()):
            if joy.get_button(i):
                btn_text = font.render(f"Button {i} ACTIVE", True, (0, 255, 0))
                display.screen.blit(btn_text, (10, y))
                y += 20
        
        display.update()
        pygame.time.wait(33) # 30 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
