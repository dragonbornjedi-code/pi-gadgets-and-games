import math

import pygame

from framework.gamestate.game_modes import Difficulty, GameMode, SimonSaysSession, BUTTON_LABELS, BUTTON_COLORS
from framework.input.input_manager import InputManager


def _make_font(size, bold=False):
    return pygame.font.SysFont("freesansbold", size, bold=bold)


def _button_text(button_id):
    return BUTTON_LABELS.get(button_id, str(button_id))


class GameState:
    def enter(self, context):
        self.context = context

    def update(self, input_data, dt):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError


class MenuState(GameState):
    title = ""
    subtitle = ""
    state_name = ""

    def __init__(self, options):
        self.options = list(options)
        self.selected_index = 0
        self.cooldown = 0.0

    def enter(self, context):
        super().enter(context)
        self.selected_index = 0
        self.cooldown = 0.0

    def update(self, input_data, dt):
        self.cooldown = max(0.0, self.cooldown - dt)
        dx, dy = input_data["dpad"]

        if self.cooldown <= 0 and dy != 0:
            if dy > 0:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            else:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            self.cooldown = 0.16

        if InputManager.BUTTON_B in input_data["button_down"]:
            return self.on_back()

        if InputManager.BUTTON_START in input_data["button_down"]:
            return self.on_confirm()

        return self.state_name

    def on_back(self):
        return "TitleScreen"

    def on_confirm(self):
        return self.__class__.__name__

    def draw(self, screen):
        screen.fill((7, 10, 16))
        width, height = screen.get_size()
        center_x = width // 2

        for offset in range(0, width, 18):
            shade = 18 + (offset % 42)
            pygame.draw.line(screen, (shade, 24, 38), (offset, 0), (0, min(height, offset // 2 + 40)), 1)

        title_font = _make_font(40, bold=True)
        subtitle_font = _make_font(16)
        option_font = _make_font(20, bold=True)
        hint_font = _make_font(14)

        screen.blit(title_font.render(self.title, True, (245, 248, 255)), (28, 26))
        screen.blit(subtitle_font.render(self.subtitle, True, (142, 164, 190)), (30, 74))

        panel = pygame.Rect(26, 112, width - 52, 144)
        pygame.draw.rect(screen, (15, 20, 32), panel, border_radius=18)
        pygame.draw.rect(screen, (88, 127, 255), panel, 2, border_radius=18)

        option_y = 136
        for index, option in enumerate(self.options):
            active = index == self.selected_index
            color = (255, 223, 111) if active else (205, 214, 231)
            prefix = "▶" if active else " "
            text = option_font.render(f"{prefix} {option}", True, color)
            screen.blit(text, (48, option_y))
            option_y += 30

        hint = hint_font.render("Start = select   |   B = back", True, (133, 145, 168))
        screen.blit(hint, hint.get_rect(center=(center_x, height - 28)))


class TitleScreenState(GameState):
    def update(self, input_data, dt):
        if InputManager.BUTTON_START in input_data["button_down"]:
            return "GameModeSelect"
        return "TitleScreen"

    def draw(self, screen):
        width, height = screen.get_size()
        screen.fill((6, 8, 14))

        for i in range(14):
            alpha = 40 + (i * 8)
            pygame.draw.arc(screen, (24, 40, 68), pygame.Rect(-60 + i * 28, 8 + i * 6, 260, 150), 0.4, 2.5, 2)

        title_font = _make_font(44, bold=True)
        body_font = _make_font(20)
        small_font = _make_font(14)

        title = title_font.render("Cognitive Reaction", True, (240, 244, 255))
        screen.blit(title, title.get_rect(center=(width // 2, height // 3 - 20)))

        subtitle = body_font.render("Retro cabinet mode. Press Start to enter the menu.", True, (153, 175, 204))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, height // 3 + 24)))

        glow = 6 + int(3 * math.sin(pygame.time.get_ticks() / 180.0))
        panel = pygame.Rect(width // 2 - 150, height // 2 - 18, 300, 88)
        pygame.draw.rect(screen, (18, 26, 42), panel, border_radius=18)
        pygame.draw.rect(screen, (255, 224, 102), panel, 2, border_radius=18)
        start_text = body_font.render("PRESS START", True, (255, 224, 102))
        screen.blit(start_text, start_text.get_rect(center=panel.center))
        pygame.draw.circle(screen, (255, 224, 102), (panel.left + 28, panel.centery), glow, 2)
        pygame.draw.circle(screen, (255, 224, 102), (panel.right - 28, panel.centery), glow, 2)

        footer = small_font.render("Action 11 = Start | Action 1 = B | Arrow keys work on desktop", True, (125, 138, 160))
        screen.blit(footer, footer.get_rect(center=(width // 2, height - 24)))


class GameModeSelectState(MenuState):
    title = "Choose Game Mode"
    subtitle = "Pick the style of round you want to play."
    state_name = "GameModeSelect"

    def __init__(self):
        # Extract mode values from the enum
        mode_options = [mode.value for mode in GameMode]
        super().__init__(mode_options)

    def enter(self, context):
        super().enter(context)
        current = context.get("mode", GameMode.ENDURANCE_STANDARD)
        if isinstance(current, GameMode):
            current_value = current.value
        else:
            current_value = str(current)
        if current_value in self.options:
            self.selected_index = self.options.index(current_value)

    def on_back(self):
        return "TitleScreen"

    def on_confirm(self):
        # Store the selected mode value; convert back to GameMode when needed
        selected_value = self.options[self.selected_index]
        # Find matching GameMode enum
        for mode in GameMode:
            if mode.value == selected_value:
                self.context["mode"] = mode
                break
        return "DifficultySelect"


class DifficultySelectState(MenuState):
    title = "Choose Difficulty"
    subtitle = "Select the intensity: 6 progressive tiers from Beginner to Grand Master."
    state_name = "DifficultySelect"
    
    # Description of each difficulty tier
    DIFFICULTY_DESCRIPTIONS = {
        "Beginner": "4 face buttons (A, B, X, Y)",
        "Intermediate": "+ D-pad directions (8 inputs total)",
        "Hard": "+ L/R shoulders & triggers (12 inputs)",
        "Expert": "+ Joystick directions (20 inputs)",
        "Champion": "+ L3 & R3 stick clicks (22 inputs)",
        "Grand Master": "+ Combo sequences (unlimited challenge)",
    }

    def __init__(self):
        # Extract difficulty values from the enum
        difficulty_options = [diff.value for diff in Difficulty]
        super().__init__(difficulty_options)

    def enter(self, context):
        super().enter(context)
        current = context.get("difficulty", Difficulty.BEGINNER)
        if isinstance(current, Difficulty):
            current_value = current.value
        else:
            current_value = str(current)
        if current_value in self.options:
            self.selected_index = self.options.index(current_value)

    def on_back(self):
        return "GameModeSelect"

    def on_confirm(self):
        # Find matching Difficulty enum
        selected_value = self.options[self.selected_index]
        for diff in Difficulty:
            if diff.value == selected_value:
                self.context["difficulty"] = diff
                break
        return "Gameplay"

    def draw(self, screen):
        super().draw(screen)
        small_font = _make_font(14)
        width, height = screen.get_size()
        
        # Show selected mode
        mode = self.context.get("mode", GameMode.ENDURANCE_STANDARD)
        mode_display = mode.value if isinstance(mode, GameMode) else str(mode)
        info = small_font.render(f"Mode: {mode_display}", True, (175, 193, 219))
        screen.blit(info, (28, 262))
        
        # Show description of selected difficulty
        selected_diff = self.options[self.selected_index]
        desc = self.DIFFICULTY_DESCRIPTIONS.get(selected_diff, "")
        desc_text = small_font.render(desc, True, (220, 210, 170))
        screen.blit(desc_text, (28, 282))


class PauseMenuState(MenuState):
    title = "Paused"
    subtitle = "Start resumes. B also resumes. Choose a different path if needed."
    state_name = "PauseMenu"

    def __init__(self):
        super().__init__(["Resume Round", "Retry Round", "Change Difficulty", "Change Game Mode", "Main Menu"])

    def on_back(self):
        return "Gameplay"

    def on_confirm(self):
        choice = self.options[self.selected_index]
        if choice == "Resume Round":
            return "Gameplay"
        if choice == "Retry Round":
            self.context["retry_round"] = True
            return "Gameplay"
        if choice == "Change Difficulty":
            return "DifficultySelect"
        if choice == "Change Game Mode":
            return "GameModeSelect"
        return "TitleScreen"


class RoundEndState(MenuState):
    title = "Round Complete"
    subtitle = "Pick what happens next."
    state_name = "RoundEnd"

    def __init__(self):
        super().__init__(["Retry Round", "Change Difficulty", "Change Game Mode", "Main Menu"])

    def on_back(self):
        return "DifficultySelect"

    def on_confirm(self):
        choice = self.options[self.selected_index]
        if choice == "Retry Round":
            self.context["retry_round"] = True
            return "Gameplay"
        if choice == "Change Difficulty":
            return "DifficultySelect"
        if choice == "Change Game Mode":
            return "GameModeSelect"
        return "TitleScreen"

    def draw(self, screen):
        super().draw(screen)
        small_font = _make_font(14)
        width, _ = screen.get_size()
        session = self.context.get("session")
        result = "Round finished"
        if session is not None:
            outcome = "Cleared" if session.completed else "Failed"
            mode_display = session.mode.value if isinstance(session.mode, GameMode) else str(session.mode)
            diff_display = session.difficulty.value if isinstance(session.difficulty, Difficulty) else str(session.difficulty)
            result = f"{outcome}: {mode_display} • {diff_display} • Score {session.score}"
        screen.blit(small_font.render(result, True, (180, 196, 220)), (28, 262))


class GameplayState(GameState):
    def enter(self, context):
        super().enter(context)
        try:
            if context.get("retry_round") and context.get("session") is not None:
                context["session"].restart()
            else:
                mode = context.get("mode", GameMode.ENDURANCE_STANDARD)
                difficulty = context.get("difficulty", Difficulty.BEGINNER)
                if mode is None or difficulty is None:
                    mode = GameMode.MEMORY_STANDARD
                    difficulty = Difficulty.BEGINNER
                context["session"] = SimonSaysSession(mode, difficulty)
            context["retry_round"] = False
        except Exception as e:
            # Defensive fallback: log error and use safest defaults
            import traceback
            traceback.print_exc()
            context["session"] = SimonSaysSession(GameMode.MEMORY_STANDARD, Difficulty.BEGINNER)
            context["retry_round"] = False

    def update(self, input_data, dt):
        session = self.context.get("session")
        if session is None:
            # Defensive fallback: session not initialized
            return "GameModeSelect"
        
        if InputManager.BUTTON_START in input_data["button_down"]:
            return "PauseMenu"

        session.update(input_data, dt)
        if session.failed or session.completed:
            return "RoundEnd"
        return "Gameplay"

    def draw(self, screen):
        session = self.context.get("session")
        if session is None:
            # Defensive fallback: cannot draw without session
            screen.fill((3, 6, 12))
            font = _make_font(20)
            text = font.render("ERROR: Session not initialized", True, (255, 0, 0))
            screen.blit(text, (50, 150))
            return
        width, height = screen.get_size()
        screen.fill((3, 6, 12))

        base = pygame.Rect(18, 18, width - 36, height - 36)
        pygame.draw.rect(screen, (10, 16, 28), base, border_radius=18)
        pygame.draw.rect(screen, (52, 86, 180), base, 2, border_radius=16)

        title_font = _make_font(20, bold=True)
        label_font = _make_font(16)
        body_font = _make_font(18)
        tiny_font = _make_font(13)

        # Header with mode and difficulty
        mode_display = session.mode.value if isinstance(session.mode, GameMode) else str(session.mode)
        diff_display = session.difficulty.value if isinstance(session.difficulty, Difficulty) else str(session.difficulty)
        header = title_font.render(f"{mode_display}  /  {diff_display}", True, (176, 205, 255))
        screen.blit(header, (34, 30))
        
        score = body_font.render(f"Score {session.score}", True, (255, 242, 202))
        screen.blit(score, (34, 58))
        
        status = label_font.render(session.feedback, True, (210, 218, 234))
        screen.blit(status, (34, 84))

        # Visual button display with mirror cross-fade during playback
        self._draw_button_display(screen, session, width)
        
        # Progress indicator
        progress = tiny_font.render(session.progress_label(), True, (141, 156, 184))
        screen.blit(progress, (36, 230))

        # Phase indicator
        phase_text = ""
        if session.phase == "showing":
            phase_text = "WATCHING..."
        elif session.phase == "input":
            phase_text = "YOUR TURN"
        
        # Check if backwards mode for special indicator
        if session.mode in (GameMode.MEMORY_BACKWARDS, GameMode.ENDURANCE_BACKWARDS, 
                           GameMode.MASTER_REVERSE_CHALLENGE):
            phase_text += " [BACKWARDS!]"
        
        if phase_text:
            phase_label = tiny_font.render(phase_text, True, (255, 200, 87))
            screen.blit(phase_label, (36, height - 30))
        else:
            hint = tiny_font.render("Press Start to pause. B is disabled during active play.", True, (110, 122, 146))
            screen.blit(hint, (36, height - 30))
    
    def _draw_button_display(self, screen, session, width):
        """Draw the button display area during playback and input."""
        button_box = pygame.Rect(34, 112, width - 68, 108)
        pygame.draw.rect(screen, (18, 26, 44), button_box, border_radius=16)
        pygame.draw.rect(screen, (255, 224, 102), button_box, 2, border_radius=16)

        if session.phase == "showing" and session.playback_active:
            # During playback: show current control, then blank pause
            self._draw_cross_fade(screen, session, button_box)
        elif session.phase == "input":
            # During input: show all buttons available (grayed out)
            self._draw_all_buttons_available(screen, button_box)
        else:
            # Default: show prompt
            prompt_font = _make_font(28, bold=True)
            prompt = prompt_font.render(session.prompt_label or "—", True, (255, 224, 102))
            screen.blit(prompt, prompt.get_rect(center=button_box.center))
    
    def _draw_cross_fade(self, screen, session, button_box):
        """Draw simplified playback: show current control, then blank pause."""
        current_button = session.playback_button

        if current_button is None:
            return

        # Show control for display window; leave blank for remaining gap window.
        if session.playback_frame < session.playback_display_frames:
            self._draw_button_with_alpha(screen, current_button, button_box, 255)
    
    def _draw_button_with_alpha(self, screen, button_id, button_box, alpha):
        """Draw a button with specified alpha (transparency)."""
        color = BUTTON_COLORS.get(button_id, (255, 255, 255))
        button_surface = pygame.Surface((button_box.width, button_box.height), pygame.SRCALPHA)
        button_color_with_alpha = (*color, alpha)
        face_buttons = {
            InputManager.BUTTON_A,
            InputManager.BUTTON_B,
            InputManager.BUTTON_X,
            InputManager.BUTTON_Y,
        }

        # Keep ABXY as the classic circle style.
        if button_id in face_buttons:
            label = BUTTON_LABELS.get(button_id, "?")
            pygame.draw.circle(
                button_surface,
                button_color_with_alpha,
                (button_box.width // 2, button_box.height // 2),
                min(button_box.width, button_box.height) // 3,
            )
            label_font = _make_font(40, bold=True)
            label_text = label_font.render(label, True, (255, 255, 255))
            label_pos = label_text.get_rect(center=(button_box.width // 2, button_box.height // 2))
            button_surface.blit(label_text, label_pos)
            screen.blit(button_surface, button_box.topleft)
            return

        # Non-ABXY controls use a text card to avoid ambiguous compact symbols.
        title, subtitle = self._control_prompt(button_id)
        card_rect = pygame.Rect(24, 14, button_box.width - 48, button_box.height - 28)
        pygame.draw.rect(button_surface, (24, 34, 56, alpha), card_rect, border_radius=14)
        pygame.draw.rect(button_surface, button_color_with_alpha, card_rect, 3, border_radius=14)

        title_font = _make_font(32, bold=True)
        subtitle_font = _make_font(20, bold=True)
        title_text = title_font.render(title, True, (245, 248, 255))
        subtitle_text = subtitle_font.render(subtitle, True, (255, 224, 102))
        button_surface.blit(title_text, title_text.get_rect(center=(button_box.width // 2, button_box.height // 2 - 16)))
        button_surface.blit(subtitle_text, subtitle_text.get_rect(center=(button_box.width // 2, button_box.height // 2 + 18)))
        screen.blit(button_surface, button_box.topleft)

    def _control_prompt(self, button_id):
        """Return a clear 2-line prompt for each control."""
        prompts = {
            InputManager.DPAD_UP: ("D-PAD", "UP"),
            InputManager.DPAD_DOWN: ("D-PAD", "DOWN"),
            InputManager.DPAD_LEFT: ("D-PAD", "LEFT"),
            InputManager.DPAD_RIGHT: ("D-PAD", "RIGHT"),
            InputManager.TRIGGER_LT: ("LEFT TRIGGER", "LT"),
            InputManager.TRIGGER_RT: ("RIGHT TRIGGER", "RT"),
            InputManager.BUTTON_LB: ("LEFT BUMPER", "LB"),
            InputManager.BUTTON_RB: ("RIGHT BUMPER", "RB"),
            InputManager.STICK_LEFT_UP: ("LEFT STICK", "UP"),
            InputManager.STICK_LEFT_DOWN: ("LEFT STICK", "DOWN"),
            InputManager.STICK_LEFT_LEFT: ("LEFT STICK", "LEFT"),
            InputManager.STICK_LEFT_RIGHT: ("LEFT STICK", "RIGHT"),
            InputManager.STICK_RIGHT_UP: ("RIGHT STICK", "UP"),
            InputManager.STICK_RIGHT_DOWN: ("RIGHT STICK", "DOWN"),
            InputManager.STICK_RIGHT_LEFT: ("RIGHT STICK", "LEFT"),
            InputManager.STICK_RIGHT_RIGHT: ("RIGHT STICK", "RIGHT"),
            InputManager.BUTTON_L3: ("LEFT STICK", "PRESS (L3)"),
            InputManager.BUTTON_R3: ("RIGHT STICK", "PRESS (R3)"),
        }
        return prompts.get(button_id, ("CONTROL", BUTTON_LABELS.get(button_id, str(button_id))))
    
    def _draw_all_buttons_available(self, screen, button_box):
        """Draw all 4 buttons grayed out during the input phase."""
        buttons = [InputManager.BUTTON_A, InputManager.BUTTON_B, 
                   InputManager.BUTTON_X, InputManager.BUTTON_Y]
        
        # Grid layout: 2x2
        grid_cols = 2
        cell_width = button_box.width // grid_cols
        cell_height = button_box.height // 2
        
        for idx, button_id in enumerate(buttons):
            row = idx // grid_cols
            col = idx % grid_cols
            cell_x = button_box.x + col * cell_width
            cell_y = button_box.y + row * cell_height
            cell_rect = pygame.Rect(cell_x, cell_y, cell_width, cell_height)
            
            # Draw button circle (grayed out)
            color = BUTTON_COLORS.get(button_id, (255, 255, 255))
            gray_color = tuple(int(c * 0.4) for c in color)  # 40% brightness
            pygame.draw.circle(screen, gray_color, cell_rect.center, cell_width // 4)
            
            # Draw button label
            label = BUTTON_LABELS.get(button_id, "?")
            label_font = _make_font(24, bold=True)
            label_text = label_font.render(label, True, (150, 150, 150))
            screen.blit(label_text, label_text.get_rect(center=cell_rect.center))


class GameStateManager:
    def __init__(self, initial_state="TitleScreen"):
        self.context = {
            "mode": GameMode.ENDURANCE_STANDARD, 
            "difficulty": Difficulty.BEGINNER,  # Updated default
            "session": None, 
            "retry_round": False
        }
        self.states = {
            "TitleScreen": TitleScreenState(),
            "GameModeSelect": GameModeSelectState(),
            "DifficultySelect": DifficultySelectState(),
            "Gameplay": GameplayState(),
            "PauseMenu": PauseMenuState(),
            "RoundEnd": RoundEndState(),
        }
        self.current_state_name = initial_state if initial_state in self.states else "TitleScreen"
        self.current_state = self.states[self.current_state_name]
        self.current_state.enter(self.context)

    def update(self, input_data, dt):
        next_state = self.current_state.update(input_data, dt)
        if next_state != self.current_state_name:
            self.set_state(next_state)

    def set_state(self, new_state):
        if new_state not in self.states:
            return
        self.current_state_name = new_state
        self.current_state = self.states[new_state]
        self.current_state.enter(self.context)

    def draw(self, screen):
        self.current_state.draw(screen)
