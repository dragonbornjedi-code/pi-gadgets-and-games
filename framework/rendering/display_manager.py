import pygame

class DisplayManager:
    def __init__(self, width=480, height=320):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
        self.dirty_rects = []

    def update(self):
        pygame.display.flip()
        
    def draw_rect(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)
        self.dirty_rects.append(rect)
