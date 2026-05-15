import argparse
from pathlib import Path
import sys

import pygame

try:
    import psutil
    MEMORY_MONITORING_AVAILABLE = True
except ImportError:
    MEMORY_MONITORING_AVAILABLE = False
    print("WARNING: psutil not available. Memory monitoring disabled.")

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from framework.gamestate.state_manager import GameStateManager
from framework.input.input_manager import InputManager
from framework.rendering.display_manager import DisplayManager
from framework.timing.performance_manager import PerformanceManager


def parse_args():
    parser = argparse.ArgumentParser(description="pi-gadgets-and-games entrypoint")
    parser.add_argument("--windowed", action="store_true", help="Disable fullscreen mode")
    parser.add_argument("--scale", type=int, default=1, help="Preview scale factor for desktop launchers")
    parser.add_argument("--max-frames", type=int, default=0, help="Exit after N frames for validation")
    parser.add_argument("--fps", type=int, default=30, help="Target frame rate")
    return parser.parse_args()


def get_memory_mb():
    """Get current process memory usage in MB."""
    if not MEMORY_MONITORING_AVAILABLE:
        return 0
    try:
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        return 0


def main():
    args = parse_args()

    pygame.init()
    pygame.joystick.init()
    pygame.font.init()

    display = DisplayManager(480, 320, fullscreen=not args.windowed, scale=args.scale)
    inputs = InputManager()
    state_manager = GameStateManager(initial_state="TitleScreen")
    perf = PerformanceManager(target_fps=args.fps)

    running = True
    frame_count = 0
    memory_warning_issued = False

    while running:
        dt = perf.tick()
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        input_data = inputs.update(events)
        state_manager.update(input_data, dt)

        state_manager.draw(display.screen)
        display.update()

        frame_count += 1
        
        # Memory monitoring every 10 frames (Pi Zero 2W guard)
        if frame_count % 10 == 0 and MEMORY_MONITORING_AVAILABLE:
            mem_mb = get_memory_mb()
            if mem_mb > 120:
                print(f"ERROR: Memory exceeded 120MB ({mem_mb:.1f}MB). Graceful shutdown to TitleScreen.")
                state_manager.set_state("TitleScreen")
                running = False
            elif mem_mb > 80 and not memory_warning_issued:
                print(f"WARNING: Memory usage high ({mem_mb:.1f}MB). Monitor for issues.")
                memory_warning_issued = True
            elif mem_mb <= 75:
                memory_warning_issued = False
        
        if args.max_frames and frame_count >= args.max_frames:
            running = False

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
