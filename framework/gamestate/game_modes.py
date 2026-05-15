class GameMode:
    ENDURANCE = "Endurance"
    SPEED = "Speed"
    MEMORY = "Memory"

class Difficulty:
    STANDARD = "Standard"
    ADVANCED = "Advanced"
    MASTER = "Master"

class GameplayEngine:
    def __init__(self, mode, difficulty):
        self.mode = mode
        self.difficulty = difficulty
        self.score = 0
        self.active = True

    def update(self, dt):
        pass
