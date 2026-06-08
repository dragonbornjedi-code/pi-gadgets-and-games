import random
import math
from dataclasses import dataclass
from enum import Enum

from framework.input.input_manager import InputManager


class GameMode(Enum):
    """7 distinct game modes for progressive cognitive training."""
    MEMORY_STANDARD = "Memory (Standard)"
    MEMORY_BACKWARDS = "Memory (Backwards)"
    SPEED_ATTACK = "Speed Attack"
    ENDURANCE_STANDARD = "Endurance (Standard)"
    ENDURANCE_BACKWARDS = "Endurance (Backwards)"
    MASTER_CHALLENGE = "Master Challenge"
    MASTER_REVERSE_CHALLENGE = "Master Reverse"


class Difficulty(Enum):
    """6-tier universal difficulty system scaling cognitive complexity."""
    BEGINNER = "Beginner"               # 4 buttons only
    INTERMEDIATE = "Intermediate"       # + D-pad (8 inputs total)
    HARD = "Hard"                       # + LT/RT (12 inputs total)
    EXPERT = "Expert"                   # + Joystick directions (20 inputs total)
    CHAMPION = "Champion"               # + L3/R3 (22 inputs total)
    GRAND_MASTER = "Grand Master"       # + Combos (unlimited)


# Difficulty input pools - progressively adds more input types
DIFFICULTY_INPUT_POOLS = {
    Difficulty.BEGINNER: [
        InputManager.BUTTON_A,
        InputManager.BUTTON_B,
        InputManager.BUTTON_X,
        InputManager.BUTTON_Y,
    ],
    
    Difficulty.INTERMEDIATE: [
        InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y,
        InputManager.DPAD_UP, InputManager.DPAD_DOWN, InputManager.DPAD_LEFT, InputManager.DPAD_RIGHT,
    ],
    
    Difficulty.HARD: [
        InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y,
        InputManager.DPAD_UP, InputManager.DPAD_DOWN, InputManager.DPAD_LEFT, InputManager.DPAD_RIGHT,
        InputManager.BUTTON_LB, InputManager.BUTTON_RB,
        InputManager.TRIGGER_LT, InputManager.TRIGGER_RT,
    ],
    
    Difficulty.EXPERT: [
        InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y,
        InputManager.DPAD_UP, InputManager.DPAD_DOWN, InputManager.DPAD_LEFT, InputManager.DPAD_RIGHT,
        InputManager.BUTTON_LB, InputManager.BUTTON_RB,
        InputManager.TRIGGER_LT, InputManager.TRIGGER_RT,
        InputManager.STICK_LEFT_UP, InputManager.STICK_LEFT_DOWN, InputManager.STICK_LEFT_LEFT, InputManager.STICK_LEFT_RIGHT,
        InputManager.STICK_RIGHT_UP, InputManager.STICK_RIGHT_DOWN, InputManager.STICK_RIGHT_LEFT, InputManager.STICK_RIGHT_RIGHT,
    ],
    
    Difficulty.CHAMPION: [
        InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y,
        InputManager.DPAD_UP, InputManager.DPAD_DOWN, InputManager.DPAD_LEFT, InputManager.DPAD_RIGHT,
        InputManager.BUTTON_LB, InputManager.BUTTON_RB,
        InputManager.TRIGGER_LT, InputManager.TRIGGER_RT,
        InputManager.STICK_LEFT_UP, InputManager.STICK_LEFT_DOWN, InputManager.STICK_LEFT_LEFT, InputManager.STICK_LEFT_RIGHT,
        InputManager.STICK_RIGHT_UP, InputManager.STICK_RIGHT_DOWN, InputManager.STICK_RIGHT_LEFT, InputManager.STICK_RIGHT_RIGHT,
        InputManager.BUTTON_L3, InputManager.BUTTON_R3,
    ],
    
    # Grand Master: includes all inputs (combos handled separately in logic)
    Difficulty.GRAND_MASTER: [
        InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y,
        InputManager.DPAD_UP, InputManager.DPAD_DOWN, InputManager.DPAD_LEFT, InputManager.DPAD_RIGHT,
        InputManager.BUTTON_LB, InputManager.BUTTON_RB,
        InputManager.TRIGGER_LT, InputManager.TRIGGER_RT,
        InputManager.STICK_LEFT_UP, InputManager.STICK_LEFT_DOWN, InputManager.STICK_LEFT_LEFT, InputManager.STICK_LEFT_RIGHT,
        InputManager.STICK_RIGHT_UP, InputManager.STICK_RIGHT_DOWN, InputManager.STICK_RIGHT_LEFT, InputManager.STICK_RIGHT_RIGHT,
        InputManager.BUTTON_L3, InputManager.BUTTON_R3,
    ],
}

BUTTON_LABELS = {
    InputManager.BUTTON_A: "A",
    InputManager.BUTTON_B: "B",
    InputManager.BUTTON_X: "X",
    InputManager.BUTTON_Y: "Y",
    InputManager.BUTTON_LB: "LB",
    InputManager.BUTTON_RB: "RB",
    InputManager.TRIGGER_LT: "LT",
    InputManager.TRIGGER_RT: "RT",
    InputManager.DPAD_UP: "↑",
    InputManager.DPAD_DOWN: "↓",
    InputManager.DPAD_LEFT: "←",
    InputManager.DPAD_RIGHT: "→",
    InputManager.BUTTON_L3: "L3",
    InputManager.BUTTON_R3: "R3",
    InputManager.STICK_LEFT_UP: "L↑",
    InputManager.STICK_LEFT_DOWN: "L↓",
    InputManager.STICK_LEFT_LEFT: "L←",
    InputManager.STICK_LEFT_RIGHT: "L→",
    InputManager.STICK_RIGHT_UP: "R↑",
    InputManager.STICK_RIGHT_DOWN: "R↓",
    InputManager.STICK_RIGHT_LEFT: "R←",
    InputManager.STICK_RIGHT_RIGHT: "R→",
}

# Hardware color mapping for cross-fade rendering
BUTTON_COLORS = {
    InputManager.BUTTON_A: (99, 230, 32),
    InputManager.BUTTON_B: (230, 30, 30),
    InputManager.BUTTON_X: (30, 136, 230),
    InputManager.BUTTON_Y: (245, 197, 0),
    InputManager.BUTTON_LB: (150, 200, 150),
    InputManager.BUTTON_RB: (200, 150, 150),
    InputManager.TRIGGER_LT: (100, 180, 255),
    InputManager.TRIGGER_RT: (255, 200, 100),
    InputManager.DPAD_UP: (180, 220, 180),
    InputManager.DPAD_DOWN: (180, 220, 180),
    InputManager.DPAD_LEFT: (180, 220, 180),
    InputManager.DPAD_RIGHT: (180, 220, 180),
    InputManager.BUTTON_L3: (150, 150, 200),
    InputManager.BUTTON_R3: (200, 150, 150),
}


@dataclass(frozen=True)
class ModeConfig:
    """Configuration for each game mode/difficulty combination."""
    initial_sequence_length: int
    cross_fade_frames: int
    time_limit: float
    max_rounds: int
    score_step: int
    grows_sequence: bool
    timer_reward_pct: float
    enable_combos: bool


# 7 modes × 6 difficulties = 42 configurations
MODE_CONFIG = {}

# Helper to fill config matrix
def _add_configs(mode, configs_dict):
    for difficulty, config in configs_dict.items():
        MODE_CONFIG[(mode, difficulty)] = config

# Memory (Standard)
_add_configs(GameMode.MEMORY_STANDARD, {
    Difficulty.BEGINNER: ModeConfig(3, 30, 0, 5, 20, True, 0, False),
    Difficulty.INTERMEDIATE: ModeConfig(3, 28, 0, 6, 24, True, 0, False),
    Difficulty.HARD: ModeConfig(3, 26, 0, 7, 28, True, 0, False),
    Difficulty.EXPERT: ModeConfig(2, 24, 0, 8, 32, True, 0, False),
    Difficulty.CHAMPION: ModeConfig(2, 22, 0, 9, 36, True, 0, False),
    Difficulty.GRAND_MASTER: ModeConfig(2, 20, 0, 10, 40, True, 0, True),
})

# Memory (Backwards)
_add_configs(GameMode.MEMORY_BACKWARDS, {
    Difficulty.BEGINNER: ModeConfig(3, 30, 0, 5, 25, True, 0, False),
    Difficulty.INTERMEDIATE: ModeConfig(3, 28, 0, 6, 30, True, 0, False),
    Difficulty.HARD: ModeConfig(3, 26, 0, 7, 34, True, 0, False),
    Difficulty.EXPERT: ModeConfig(2, 24, 0, 8, 38, True, 0, False),
    Difficulty.CHAMPION: ModeConfig(2, 22, 0, 9, 42, True, 0, False),
    Difficulty.GRAND_MASTER: ModeConfig(2, 20, 0, 10, 45, True, 0, True),
})

# Speed Attack
_add_configs(GameMode.SPEED_ATTACK, {
    Difficulty.BEGINNER: ModeConfig(3, 25, 60.0, 0, 15, False, 0, False),
    Difficulty.INTERMEDIATE: ModeConfig(3, 22, 60.0, 0, 18, False, 0, False),
    Difficulty.HARD: ModeConfig(3, 20, 60.0, 0, 21, False, 0, False),
    Difficulty.EXPERT: ModeConfig(4, 18, 60.0, 0, 24, False, 0, False),
    Difficulty.CHAMPION: ModeConfig(4, 16, 60.0, 0, 27, False, 0, False),
    Difficulty.GRAND_MASTER: ModeConfig(5, 14, 60.0, 0, 30, False, 0, True),
})

# Endurance (Standard)
_add_configs(GameMode.ENDURANCE_STANDARD, {
    Difficulty.BEGINNER: ModeConfig(3, 28, 30.0, 0, 16, False, 0.5, False),
    Difficulty.INTERMEDIATE: ModeConfig(3, 26, 30.0, 0, 19, False, 0.5, False),
    Difficulty.HARD: ModeConfig(4, 24, 30.0, 0, 22, False, 0.5, False),
    Difficulty.EXPERT: ModeConfig(4, 22, 30.0, 0, 25, False, 0.5, False),
    Difficulty.CHAMPION: ModeConfig(5, 20, 30.0, 0, 28, False, 0.5, False),
    Difficulty.GRAND_MASTER: ModeConfig(5, 18, 30.0, 0, 31, False, 0.5, True),
})

# Endurance (Backwards)
_add_configs(GameMode.ENDURANCE_BACKWARDS, {
    Difficulty.BEGINNER: ModeConfig(3, 28, 30.0, 0, 18, False, 0.5, False),
    Difficulty.INTERMEDIATE: ModeConfig(3, 26, 30.0, 0, 21, False, 0.5, False),
    Difficulty.HARD: ModeConfig(4, 24, 30.0, 0, 24, False, 0.5, False),
    Difficulty.EXPERT: ModeConfig(4, 22, 30.0, 0, 27, False, 0.5, False),
    Difficulty.CHAMPION: ModeConfig(5, 20, 30.0, 0, 30, False, 0.5, False),
    Difficulty.GRAND_MASTER: ModeConfig(5, 18, 30.0, 0, 33, False, 0.5, True),
})

# Master Challenge
_add_configs(GameMode.MASTER_CHALLENGE, {
    Difficulty.BEGINNER: ModeConfig(2, 28, 30.0, 0, 25, True, 0.5, False),
    Difficulty.INTERMEDIATE: ModeConfig(2, 26, 30.0, 0, 30, True, 0.5, False),
    Difficulty.HARD: ModeConfig(2, 24, 30.0, 0, 35, True, 0.5, False),
    Difficulty.EXPERT: ModeConfig(2, 22, 30.0, 0, 40, True, 0.5, False),
    Difficulty.CHAMPION: ModeConfig(2, 20, 30.0, 0, 45, True, 0.5, False),
    Difficulty.GRAND_MASTER: ModeConfig(2, 18, 30.0, 0, 50, True, 0.5, True),
})

# Master Reverse Challenge
_add_configs(GameMode.MASTER_REVERSE_CHALLENGE, {
    Difficulty.BEGINNER: ModeConfig(2, 28, 30.0, 0, 30, True, 0.5, False),
    Difficulty.INTERMEDIATE: ModeConfig(2, 26, 30.0, 0, 35, True, 0.5, False),
    Difficulty.HARD: ModeConfig(2, 24, 30.0, 0, 40, True, 0.5, False),
    Difficulty.EXPERT: ModeConfig(2, 22, 30.0, 0, 45, True, 0.5, False),
    Difficulty.CHAMPION: ModeConfig(2, 20, 30.0, 0, 50, True, 0.5, False),
    Difficulty.GRAND_MASTER: ModeConfig(2, 18, 30.0, 0, 55, True, 0.5, True),
})


class SimonSaysSession:
    """Core game engine supporting 7 modes × 6 difficulties = 42 configurations."""
    
    def __init__(self, mode, difficulty):
        self.mode = mode
        self.difficulty = difficulty
        self.config = MODE_CONFIG[(mode, difficulty)]
        self.input_pool = DIFFICULTY_INPUT_POOLS[difficulty]
        
        # Game state
        self.sequence = []
        self.user_input = []
        self.round_count = 0
        self.score = 0
        self.time_remaining = self.config.time_limit
        self.phase = "showing"
        self.feedback = "Get ready"
        self.completed = False
        self.failed = False
        self.failure_reason = ""
        
        # Playback state
        self.playback_index = 0
        self.playback_frame = 0
        self.playback_active = False
        self.playback_display_frames = self.config.cross_fade_frames
        self.playback_gap_frames = 15  # Fixed gap of 15 frames (~0.25s) between signals
        
        # Dynamic tempo scaling
        self.successful_rounds = 0
        self.current_cross_fade_frames = self.config.cross_fade_frames
        self.min_cross_fade_frames = 10
        
        self._build_sequence()
    
    def _build_sequence(self):
        """Build sequence from the appropriate input pool for this difficulty."""
        try:
            if self.config.grows_sequence:
                length = self.config.initial_sequence_length + self.successful_rounds
            else:
                length = self.config.initial_sequence_length
            
            if not self.input_pool or len(self.input_pool) == 0:
                self.sequence = [InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y]
            else:
                self.sequence = [random.choice(self.input_pool) for _ in range(length)]
        except Exception as e:
            print(f"WARNING: _build_sequence failed: {e}. Using fallback.")
            self.sequence = [InputManager.BUTTON_A, InputManager.BUTTON_B, InputManager.BUTTON_X, InputManager.BUTTON_Y]
        
        self.user_input = []
        self.playback_index = 0
        self.playback_frame = 0
        self.playback_active = True
        self.phase = "showing"
        self.feedback = "Watch the pattern"
    
    def _update_tempo(self):
        """Apply dynamic tempo scaling with guards."""
        scale_factor = 0.95 ** (self.successful_rounds // 3)
        self.current_cross_fade_frames = max(
            self.min_cross_fade_frames,
            int(self.config.cross_fade_frames * scale_factor)
        )
    
    def _validate_input(self, button_id):
        """Check if input matches expected sequence."""
        if not self.sequence:
            return False
        
        if len(self.user_input) >= len(self.sequence):
            return False
        
        expected_button = self.sequence[len(self.user_input)]
        
        if self.mode in (GameMode.MEMORY_BACKWARDS, GameMode.ENDURANCE_BACKWARDS, 
                         GameMode.MASTER_REVERSE_CHALLENGE):
            expected_button = self.sequence[len(self.sequence) - 1 - len(self.user_input)]
        
        return button_id == expected_button
    
    def update(self, input_data, dt):
        """Update game state each frame."""
        if self.completed or self.failed:
            return
        
        if self.config.time_limit > 0:
            self.time_remaining -= dt
            if self.time_remaining <= 0:
                self.time_remaining = 0
                self.failed = True
                self.failure_reason = "Time expired"
                self.feedback = "Time's up!"
                return
        
        # Handle "showing" phase: play back the sequence
        if self.phase == "showing":
            if self.playback_active:
                self.playback_frame += 1
                total_cycle = self.current_cross_fade_frames + self.playback_gap_frames
                
                if self.playback_frame >= total_cycle:
                    self.playback_frame = 0
                    self.playback_index += 1
                    if self.playback_index >= len(self.sequence):
                        self.playback_active = False
                        self.phase = "input"
                        self.feedback = "Your turn!"
            return
        
        # Handle "input" phase: accept player input
        if self.phase == "input":
            for button_id in input_data["button_down"]:
                if self._validate_input(button_id):
                    self.user_input.append(button_id)
                    self.score += self.config.score_step
                    if len(self.user_input) >= len(self.sequence):
                        self._round_complete()
                        return
                else:
                    self.failed = True
                    self.failure_reason = "Wrong input"
                    self.feedback = "Mistake! Try again."
                    return
    
    def _round_complete(self):
        """Handle successful round completion."""
        self.successful_rounds += 1
        self.round_count += 1
        
        if self.config.max_rounds > 0 and self.successful_rounds >= self.config.max_rounds:
            self.completed = True
            self.feedback = "Pattern complete!"
            return
        
        if self.config.timer_reward_pct > 0:
            reward = self.time_remaining * self.config.timer_reward_pct
            self.time_remaining += reward
        
        self._update_tempo()
        self._build_sequence()
    
    def restart(self):
        """Reset for a new session."""
        self.__init__(self.mode, self.difficulty)
    
    @property
    def prompt_label(self):
        """Return the sequence as a label string."""
        return " ".join(BUTTON_LABELS.get(b, str(b)) for b in self.sequence)
    
    @property
    def playback_button(self):
        """Get button currently being displayed."""
        if self.playback_active and self.playback_index < len(self.sequence):
            # Only return the button if we are in the 'visible' part of the cycle
            if self.playback_frame < self.current_cross_fade_frames:
                return self.sequence[self.playback_index]
        return None
    
    @property
    def playback_alpha(self):
        """Current button alpha (fading out)."""
        if not self.playback_active or self.playback_index >= len(self.sequence):
            return 0
        if self.playback_frame >= self.current_cross_fade_frames:
            return 0
            
        progress = min(1.0, self.playback_frame / self.current_cross_fade_frames)
        return max(0, min(255, int(255 * (1 - progress))))

    @property
    def playback_display_frames(self):
        """How long the current control is shown before the blank gap."""
        extra_frames = self.playback_extra_display_frames if self.config.time_limit == 0 else 0
        return max(1, self.current_cross_fade_frames + extra_frames)

    @property
    def playback_total_frames(self):
        """Total per-control playback window: visible + blank gap."""
        gap_frames = self.playback_blank_frames if self.config.time_limit == 0 else 0
        return self.playback_display_frames + gap_frames
    
    @property
    def next_playback_alpha(self):
        """Next button alpha (fading in)."""
        if self.playback_index + 1 >= len(self.sequence):
            return 0
        
        progress = min(1.0, self.playback_frame / self.current_cross_fade_frames)
        next_alpha = max(0, min(255, int(255 * progress)))
        
        return next_alpha
    
    def progress_label(self):
        """Return progress indicator."""
        if self.config.time_limit > 0:
            return f"Time: {self.time_remaining:0.1f}s | Round {self.successful_rounds + 1}"
        if self.config.grows_sequence:
            return f"Round {self.successful_rounds + 1}"
        if self.config.max_rounds > 0:
            return f"Path {self.successful_rounds + 1}/{self.config.max_rounds}"
        return f"Score {self.score}"


class GameplayEngine:
    """Compatibility shim."""
    def __init__(self, mode, difficulty):
        self.session = SimonSaysSession(mode, difficulty)
    
    def update(self, input_data, dt):
        self.session.update(input_data, dt)
        return not (self.session.failed or self.session.completed)
