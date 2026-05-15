import pygame
import sys
from framework.input.input_manager import InputManager
from framework.rendering.display_manager import DisplayManager

def main():
    pygame.init()
    display = DisplayManager()
    inputs = InputManager()
    
    running = True
    while running:
        inputs.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        display.update()
    
    pygame.quit()

if __name__ == "__main__":
    main()
