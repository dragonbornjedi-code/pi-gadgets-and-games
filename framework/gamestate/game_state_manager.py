import pygame

class GameStateManager:
    def __init__(self):
        self.state = "TITLE" # TITLE, PAUSE, GAMEPLAY, GAMEOVER, HIGHSCORE

    def set_state(self, new_state):
        self.state = new_state
        print(f"State changed to: {self.state}")

class HighScoreState:
    def __init__(self):
        self.scores = {}

class GameplayState:
    def __init__(self):
        self.score = 0
        self.combo = 0
