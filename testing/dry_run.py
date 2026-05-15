import random
from framework.gamestate.game_modes import GameplayEngine, GameMode, Difficulty

def run_dry_run():
    print("--- Starting Dry Run Simulation ---")
    engine = GameplayEngine(GameMode.ENDURANCE, Difficulty.STANDARD)
    
    # Simulate 100 ticks
    for i in range(100):
        engine.update(0.033)
        # Random combo simulation
        if random.random() < 0.1:
            print(f"Simulation: Combo success at tick {i}")
            
    print("--- Dry Run Complete ---")

if __name__ == "__main__":
    run_dry_run()
