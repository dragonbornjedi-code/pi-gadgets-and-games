import json
import os

class HighScoreManager:
    def __init__(self, save_path="games/cognitive_reaction/assets/saves/highscores.json"):
        self.save_path = save_path
        self.scores = {"Endurance": [], "Speed": [], "Memory": []}
        self.load()

    def load(self):
        if os.path.exists(self.save_path):
            with open(self.save_path, 'r') as f:
                self.scores = json.load(f)

    def save(self):
        # Atomic write
        temp_path = self.save_path + ".tmp"
        with open(temp_path, 'w') as f:
            json.dump(self.scores, f)
        os.replace(temp_path, self.save_path)

    def add_score(self, mode, name, score):
        self.scores[mode].append({"name": name, "score": score})
        self.scores[mode] = sorted(self.scores[mode], key=lambda x: x['score'], reverse=True)[:3]
        self.save()
