import time

import pygame


class InputManager:
    # Xbox Series X controller mapping - comprehensive input surface
    
    # Face buttons (Beginner tier - 4 inputs)
    BUTTON_A = 0
    BUTTON_B = 1
    BUTTON_X = 3
    BUTTON_Y = 4
    
    # D-Pad directions (Intermediate tier - 4 inputs)
    # Note: D-pad comes via JOYHATMOTION, mapped as virtual buttons
    DPAD_UP = 100
    DPAD_DOWN = 101
    DPAD_LEFT = 102
    DPAD_RIGHT = 103
    
    # Shoulder buttons / Bumpers (Hard tier - 2 inputs)
    BUTTON_LB = 6  # Left Bumper / L_SHOULDER
    BUTTON_RB = 7  # Right Bumper / R_SHOULDER
    
    # Trigger buttons (Hard tier - 2 more, total 4)
    # Triggers are analog, mapped as virtual buttons when pressed
    TRIGGER_LT = 104  # Left Trigger (Axis 2)
    TRIGGER_RT = 105  # Right Trigger (Axis 5)
    
    # Stick click buttons (Champion tier - 2 inputs)
    BUTTON_L3 = 8   # Left Stick Click
    BUTTON_R3 = 9   # Right Stick Click
    
    # Analog stick directions (Expert tier - 8 inputs)
    # Left stick: 4 cardinal directions
    STICK_LEFT_UP = 110
    STICK_LEFT_DOWN = 111
    STICK_LEFT_LEFT = 112
    STICK_LEFT_RIGHT = 113
    
    # Right stick: 4 cardinal directions
    STICK_RIGHT_UP = 114
    STICK_RIGHT_DOWN = 115
    STICK_RIGHT_LEFT = 116
    STICK_RIGHT_RIGHT = 117
    
    # System buttons
    BUTTON_SELECT = 10
    BUTTON_START = 11
    BUTTON_XBOX = 12

    def __init__(self, deadzone=0.2, trigger_threshold=0.5, cooldown_duration=0.1):
        self.joysticks = {}
        self.button_states = {}
        self.input_cooldowns = {}
        self.deadzone = deadzone
        self.trigger_threshold = trigger_threshold
        self.cooldown_duration = cooldown_duration
        
        # Track analog stick state for direction mapping
        self.left_stick = (0.0, 0.0)
        self.right_stick = (0.0, 0.0)
        self.left_trigger = 0.0
        self.right_trigger = 0.0
        self.last_dpad = (0, 0)
        
        # Verify 8-directional mapping produces distinct button IDs
        self._verify_stick_mapping()

    def _attach_joystick(self, device_index):
        joystick = pygame.joystick.Joystick(device_index)
        joystick.init()
        self.joysticks[joystick.get_instance_id()] = joystick
        return joystick

    def _detach_joystick(self, instance_id):
        joystick = self.joysticks.pop(instance_id, None)
        if joystick is not None:
            joystick.quit()

    def update(self, events):
        processed_input = {
            "button_down": [],
            "button_up": [],
            "button_held": [],
            "dpad": (0, 0),
            "axis": (0.0, 0.0),
            "left_stick": (0.0, 0.0),
            "right_stick": (0.0, 0.0),
            "left_trigger": 0.0,
            "right_trigger": 0.0,
            "connected": [],
            "disconnected": [],
        }

        # Defensive: check for event queue overflow
        if len(events) > 100:
            print(f"WARNING: Event queue overflow detected ({len(events)} events). Flushing.")
            events = events[-100:]  # Keep only last 100 events

        for event in events:
            try:
                if event.type == pygame.JOYDEVICEADDED:
                    joystick = self._attach_joystick(event.device_index)
                    processed_input["connected"].append(joystick.get_instance_id())
                elif event.type == pygame.JOYDEVICEREMOVED:
                    instance_id = getattr(event, "instance_id", -1)
                    processed_input["disconnected"].append(instance_id)
                    self._detach_joystick(instance_id)
                    print(f"INFO: Joystick {instance_id} disconnected")
                elif event.type == pygame.JOYBUTTONDOWN:
                    instance_id = getattr(event, "instance_id", -1)
                    button_id = getattr(event, "button", None)
                    if button_id is not None and self._accept_button(instance_id, button_id):
                        self.button_states[(instance_id, button_id)] = True
                        processed_input["button_down"].append(button_id)
                elif event.type == pygame.JOYBUTTONUP:
                    instance_id = getattr(event, "instance_id", -1)
                    button_id = getattr(event, "button", None)
                    if button_id is not None:
                        self.button_states[(instance_id, button_id)] = False
                        processed_input["button_up"].append(button_id)
                elif event.type == pygame.JOYHATMOTION:
                    processed_input["dpad"] = event.value
                    self.last_dpad = event.value
                    # Map D-pad to virtual button events
                    self._map_dpad_to_buttons(event.value, processed_input)
                elif event.type == pygame.JOYAXISMOTION:
                    # Handle all analog axes: sticks and triggers
                    self._handle_axis_motion(event, processed_input)
                elif event.type == pygame.KEYDOWN:
                    self._apply_keyboard_down(event, processed_input)
                elif event.type == pygame.KEYUP:
                    self._apply_keyboard_up(event, processed_input)
            except Exception as e:
                print(f"WARNING: Error processing event {event.type}: {e}")
                continue

        for (instance_id, button_id), pressed in self.button_states.items():
            if pressed and button_id not in processed_input["button_held"]:
                processed_input["button_held"].append(button_id)

        return processed_input

    def _map_dpad_to_buttons(self, dpad_value, processed_input):
        """Map D-pad HAT motion to virtual button events for sequence generation."""
        dx, dy = dpad_value
        
        if dy == -1 and self._accept_button(-1, self.DPAD_UP):
            processed_input["button_down"].append(self.DPAD_UP)
            self.button_states[(-1, self.DPAD_UP)] = True
        elif dy == 1 and self._accept_button(-1, self.DPAD_DOWN):
            processed_input["button_down"].append(self.DPAD_DOWN)
            self.button_states[(-1, self.DPAD_DOWN)] = True
        
        if dx == -1 and self._accept_button(-1, self.DPAD_LEFT):
            processed_input["button_down"].append(self.DPAD_LEFT)
            self.button_states[(-1, self.DPAD_LEFT)] = True
        elif dx == 1 and self._accept_button(-1, self.DPAD_RIGHT):
            processed_input["button_down"].append(self.DPAD_RIGHT)
            self.button_states[(-1, self.DPAD_RIGHT)] = True
        
        # Clear D-pad buttons when neutral
        if dpad_value == (0, 0):
            for dpad_btn in [self.DPAD_UP, self.DPAD_DOWN, self.DPAD_LEFT, self.DPAD_RIGHT]:
                self.button_states[(-1, dpad_btn)] = False
    
    def _handle_axis_motion(self, event, processed_input):
        """Handle analog axes: sticks (0,1,3,4) and triggers (2,5)."""
        axis_index = event.axis
        value = event.value
        
        # Defensive: clamp trigger values to [-1.0, 1.0]
        value = max(-1.0, min(1.0, value))
        
        # Apply deadzone
        if abs(value) < self.deadzone:
            value = 0.0
        
        # Triggers (axes 2 and 5)
        if axis_index == 2:  # LT
            self.left_trigger = value
            processed_input["left_trigger"] = value
            # Map to virtual button when pressed
            if value > self.trigger_threshold and self._accept_button(-1, self.TRIGGER_LT):
                processed_input["button_down"].append(self.TRIGGER_LT)
                self.button_states[(-1, self.TRIGGER_LT)] = True
            elif value <= self.trigger_threshold:
                self.button_states[(-1, self.TRIGGER_LT)] = False
        
        elif axis_index == 5:  # RT
            self.right_trigger = value
            processed_input["right_trigger"] = value
            # Map to virtual button when pressed
            if value > self.trigger_threshold and self._accept_button(-1, self.TRIGGER_RT):
                processed_input["button_down"].append(self.TRIGGER_RT)
                self.button_states[(-1, self.TRIGGER_RT)] = True
            elif value <= self.trigger_threshold:
                self.button_states[(-1, self.TRIGGER_RT)] = False
        
        # Left stick (axes 0, 1)
        elif axis_index == 0:  # Left stick X
            self.left_stick = (value, self.left_stick[1])
            processed_input["left_stick"] = self.left_stick
            self._map_stick_directions(self.left_stick, "left", processed_input)
        
        elif axis_index == 1:  # Left stick Y
            self.left_stick = (self.left_stick[0], value)
            processed_input["left_stick"] = self.left_stick
            self._map_stick_directions(self.left_stick, "left", processed_input)
        
        # Right stick (axes 3, 4)
        elif axis_index == 3:  # Right stick X
            self.right_stick = (value, self.right_stick[1])
            processed_input["right_stick"] = self.right_stick
            self._map_stick_directions(self.right_stick, "right", processed_input)
        
        elif axis_index == 4:  # Right stick Y
            self.right_stick = (self.right_stick[0], value)
            processed_input["right_stick"] = self.right_stick
            self._map_stick_directions(self.right_stick, "right", processed_input)
    
    def _map_stick_directions(self, stick_pos, stick_name, processed_input):
        """Map analog stick to 4-directional virtual buttons."""
        x, y = stick_pos
        stick_deadzone = self.deadzone * 1.5  # Slightly higher threshold for stick directions
        
        if stick_name == "left":
            buttons = {
                "up": self.STICK_LEFT_UP,
                "down": self.STICK_LEFT_DOWN,
                "left": self.STICK_LEFT_LEFT,
                "right": self.STICK_LEFT_RIGHT,
            }
        else:  # right
            buttons = {
                "up": self.STICK_RIGHT_UP,
                "down": self.STICK_RIGHT_DOWN,
                "left": self.STICK_RIGHT_LEFT,
                "right": self.STICK_RIGHT_RIGHT,
            }
        
        # Map stick directions to button presses
        if y < -stick_deadzone and self._accept_button(-1, buttons["up"]):
            processed_input["button_down"].append(buttons["up"])
            self.button_states[(-1, buttons["up"])] = True
        elif y >= -stick_deadzone:
            self.button_states[(-1, buttons["up"])] = False
        
        if y > stick_deadzone and self._accept_button(-1, buttons["down"]):
            processed_input["button_down"].append(buttons["down"])
            self.button_states[(-1, buttons["down"])] = True
        elif y <= stick_deadzone:
            self.button_states[(-1, buttons["down"])] = False
        
        if x < -stick_deadzone and self._accept_button(-1, buttons["left"]):
            processed_input["button_down"].append(buttons["left"])
            self.button_states[(-1, buttons["left"])] = True
        elif x >= -stick_deadzone:
            self.button_states[(-1, buttons["left"])] = False
        
        if x > stick_deadzone and self._accept_button(-1, buttons["right"]):
            processed_input["button_down"].append(buttons["right"])
            self.button_states[(-1, buttons["right"])] = True
        elif x <= stick_deadzone:
            self.button_states[(-1, buttons["right"])] = False
    
    def _apply_keyboard_down(self, event, processed_input):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            processed_input["button_down"].append(self.BUTTON_START)
            self.button_states[(-1, self.BUTTON_START)] = True
        elif event.key in (pygame.K_b, pygame.K_BACKSPACE):
            processed_input["button_down"].append(self.BUTTON_B)
            self.button_states[(-1, self.BUTTON_B)] = True
        elif event.key == pygame.K_UP:
            processed_input["dpad"] = (0, -1)
        elif event.key == pygame.K_DOWN:
            processed_input["dpad"] = (0, 1)
        elif event.key == pygame.K_LEFT:
            processed_input["dpad"] = (-1, 0)
        elif event.key == pygame.K_RIGHT:
            processed_input["dpad"] = (1, 0)

    def _apply_keyboard_up(self, event, processed_input):
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.button_states[(-1, self.BUTTON_START)] = False
            processed_input["button_up"].append(self.BUTTON_START)
        elif event.key in (pygame.K_b, pygame.K_BACKSPACE):
            self.button_states[(-1, self.BUTTON_B)] = False
            processed_input["button_up"].append(self.BUTTON_B)

    def _accept_button(self, instance_id, button_id):
        now = time.monotonic()
        cooldown_key = (instance_id, button_id)
        last_input = self.input_cooldowns.get(cooldown_key, 0.0)
        if now - last_input < self.cooldown_duration:
            return False

        self.input_cooldowns[cooldown_key] = now
        return True

    def _update_axis(self, current_axis, axis_index, value):
        x, y = current_axis
        if abs(value) < self.deadzone:
            value = 0.0

        if axis_index == 0:
            x = value
        elif axis_index == 1:
            y = value

        return (x, y)

    def is_button_pressed(self, button_id):
        return any(
            pressed for (instance_id, current_button), pressed in self.button_states.items()
            if current_button == button_id and pressed
        )

    def _verify_stick_mapping(self):
        """Verify that 8-directional mapping produces exactly 8 distinct button IDs."""
        button_ids = [
            self.STICK_LEFT_UP, self.STICK_LEFT_DOWN, self.STICK_LEFT_LEFT, self.STICK_LEFT_RIGHT,
            self.STICK_RIGHT_UP, self.STICK_RIGHT_DOWN, self.STICK_RIGHT_LEFT, self.STICK_RIGHT_RIGHT,
        ]
        
        # Print verification table
        print("\n=== INPUT MAPPING VERIFICATION TABLE ===")
        print(f"{'Direction':<20} {'Button ID':<12}")
        print("-" * 32)
        print(f"{'Left Stick UP':<20} {self.STICK_LEFT_UP:<12}")
        print(f"{'Left Stick DOWN':<20} {self.STICK_LEFT_DOWN:<12}")
        print(f"{'Left Stick LEFT':<20} {self.STICK_LEFT_LEFT:<12}")
        print(f"{'Left Stick RIGHT':<20} {self.STICK_LEFT_RIGHT:<12}")
        print(f"{'Right Stick UP':<20} {self.STICK_RIGHT_UP:<12}")
        print(f"{'Right Stick DOWN':<20} {self.STICK_RIGHT_DOWN:<12}")
        print(f"{'Right Stick LEFT':<20} {self.STICK_RIGHT_LEFT:<12}")
        print(f"{'Right Stick RIGHT':<20} {self.STICK_RIGHT_RIGHT:<12}")
        print("-" * 32)
        
        # Verify distinct values
        if len(button_ids) == len(set(button_ids)):
            print(f"✓ All 8 button IDs are DISTINCT")
        else:
            print(f"✗ WARNING: Duplicate button IDs detected!")
            duplicates = [bid for bid in set(button_ids) if button_ids.count(bid) > 1]
            print(f"  Duplicates: {duplicates}")
        
        print("=====================================\n")
