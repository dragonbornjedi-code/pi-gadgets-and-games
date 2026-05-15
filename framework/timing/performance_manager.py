import time
import pygame

class PerformanceManager:
    def __init__(self, target_fps=30):
        self.target_fps = target_fps
        self.clock = pygame.time.Clock()
        self.frame_times = []
        
    def tick(self):
        dt = self.clock.tick(self.target_fps)
        self.frame_times.append(dt)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
            
        # Spike detection (e.g., if frame takes > 50ms)
        if dt > 50:
            print(f"⚠️ Warning: Frame spike detected: {dt}ms")
            
        return dt / 1000.0 # Return dt in seconds

    def get_avg_fps(self):
        if not self.frame_times: return 0
        avg_ms = sum(self.frame_times) / len(self.frame_times)
        return 1000 / avg_ms if avg_ms > 0 else 0
