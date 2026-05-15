import time

class ComboDetector:
    def __init__(self, window_ms=50):
        self.window_ms = window_ms
        self.history = []

    def register_input(self, input_id):
        self.history.append((input_id, time.time() * 1000))
        # Prune old inputs
        now = time.time() * 1000
        self.history = [h for h in self.history if now - h[1] < self.window_ms]

    def check_combo(self, combo_sequence):
        # Implementation for detecting simultaneous or sequential inputs
        return False
