import os

import pygame


class DisplayManager:
    def __init__(self, width=480, height=320, fullscreen=True, scale=1):
        self.width = width
        self.height = height
        self.scale = max(1, int(scale))
        self.dirty_rects = []

        flags = 0
        if fullscreen and os.environ.get("SDL_VIDEODRIVER") != "dummy":
            flags |= pygame.FULLSCREEN

        try:
            self.window = pygame.display.set_mode((width * self.scale, height * self.scale), flags)
        except pygame.error:
            self.window = pygame.display.set_mode((width * self.scale, height * self.scale))

        self.screen = pygame.Surface((width, height))
        
        # Convert screen surface for optimized blitting on Pi Zero 2W
        try:
            self.screen = self.screen.convert()
        except pygame.error:
            # Fall back to non-converted if convert() fails
            print("WARNING: Could not convert display surface. Using non-optimized mode.")

    def update(self):
        if self.scale != 1:
            pygame.transform.scale(self.screen, self.window.get_size(), self.window)
        else:
            self.window.blit(self.screen, (0, 0))
        pygame.display.flip()

    def draw_rect(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)
        self.dirty_rects.append(rect)
