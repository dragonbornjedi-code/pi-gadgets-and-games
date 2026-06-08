import time
import pygame


class InputManager:
    # Virtual button IDs for unified logic (independent of hardware)
    BUTTON_A = 0
    BUTTON_B = 1
    BUTTON_X = 2
    BUTTON_Y = 3
    BUTTON_LB = 4
    BUTTON_RB = 5
    TRIGGER_LT = 104
    TRIGGER_RT = 105
    BUTTON_L3 = 8
    BUTTON_R3 = 9
    BUTTON_START = 11
    BUTTON_SELECT = 10
    
    # Analog stick directions (mapped as virtual buttons)
    STICK_LEFT_UP = 110
    STICK_LEFT_DOWN = 111
    STICK_LEFT_LEFT = 112
    STICK_LEFT_RIGHT = 113
    STICK_RIGHT_UP = 114
    STICK_RIGHT_DOWN = 115
    STICK_RIGHT_LEFT = 116
    STICK_RIGHT_RIGHT = 117
    
    # D-Pad directions (mapped as virtual buttons)
    DPAD_UP = 100
    DPAD_DOWN = 101
    DPAD_LEFT = 102
    DPAD_RIGHT = 103

    # Controller Mappings
    MAPPING_XBOX = {
        "A": 0, "B": 1, "X": 2, "Y": 3,
        "LB": 4, "RB": 5, "L3": 8, "R3": 9,
        "START": 7, "SELECT": 6,
        "LT_AXIS": 2, "RT_AXIS": 5
    }
    
    MAPPING_PS5 = {
        "A": 0, "B": 1, "X": 2, "Y": 3,  # Adjusted to match common PS5 driver IDs if needed, but let's use the ones from research
        "LB": 4, "RB": 5, "L3": 10, "R3": 11,
        "START": 9, "SELECT": 8,
        "LT_AXIS": 2, "RT_AXIS": 5
    }
    
    # Actual IDs from the user's Pi research:
    # PS5: y=0, b=1, a=2, x=3, l1=4, r1=5, l2=6, r2=7, select=8, start=9, l3=10, r3=11
    MAPPING_PS5_RETROPIE = {
        "Y": 0, "B": 1, "A": 2, "X": 3,
        "LB": 4, "RB": 5, "LT": 6, "RT": 7, # These are buttons, not axes on some drivers!
        "SELECT": 8, "START": 9, "L3": 10, "R3": 11,
        "LT_AXIS": 2, "RT_AXIS": 5 # Defaults for axes
    }

    def __init__(self, deadzone=0.2, trigger_threshold=0.5, cooldown_duration=0.1):
        self.joysticks = {}
        self.joystick_types = {} # instance_id -> "xbox" or "ps5"
        self.button_states = {}
        self.input_cooldowns = {}
        self.deadzone = deadzone
        self.trigger_threshold = trigger_threshold
        self.cooldown_duration = cooldown_duration
        
        self.left_stick = (0.0, 0.0)
        self.right_stick = (0.0, 0.0)
        self.left_trigger = 0.0
        self.right_trigger = 0.0
        self.last_dpad = (0, 0)

    def _get_joystick_type(self, joystick):
        name = joystick.get_name().lower()
        if "dualsense" in name or "ps5" in name or "sony" in name:
            return "ps5"
        return "xbox"

    def _map_hardware_to_virtual(self, instance_id, hardware_btn_id):
        j_type = self.joystick_types.get(instance_id, "xbox")
        
        if j_type == "ps5":
            # Map based on MAPPING_PS5_RETROPIE
            mapping = self.MAPPING_PS5_RETROPIE
            if hardware_btn_id == mapping["A"]: return self.BUTTON_A
            if hardware_btn_id == mapping["B"]: return self.BUTTON_B
            if hardware_btn_id == mapping["X"]: return self.BUTTON_X
            if hardware_btn_id == mapping["Y"]: return self.BUTTON_Y
            if hardware_btn_id == mapping["LB"]: return self.BUTTON_LB
            if hardware_btn_id == mapping["RB"]: return self.BUTTON_RB
            if hardware_btn_id == mapping["START"]: return self.BUTTON_START
            if hardware_btn_id == mapping["SELECT"]: return self.BUTTON_SELECT
            if hardware_btn_id == mapping["L3"]: return self.BUTTON_L3
            if hardware_btn_id == mapping["R3"]: return self.BUTTON_R3
            if hardware_btn_id == mapping["LT"]: return self.TRIGGER_LT
            if hardware_btn_id == mapping["RT"]: return self.TRIGGER_RT
        else:
            # Default Xbox-ish mapping
            if hardware_btn_id == 0: return self.BUTTON_A
            if hardware_btn_id == 1: return self.BUTTON_B
            if hardware_btn_id == 2: return self.BUTTON_X
            if hardware_btn_id == 3: return self.BUTTON_Y
            if hardware_btn_id == 4: return self.BUTTON_LB
            if hardware_btn_id == 5: return self.BUTTON_RB
            if hardware_btn_id == 6: return self.BUTTON_SELECT
            if hardware_btn_id == 7: return self.BUTTON_START
            if hardware_btn_id == 8: return self.BUTTON_L3
            if hardware_btn_id == 9: return self.BUTTON_R3
            
        return hardware_btn_id # Fallback

    def _attach_joystick(self, device_index):
        joystick = pygame.joystick.Joystick(device_index)
        joystick.init()
        instance_id = joystick.get_instance_id()
        self.joysticks[instance_id] = joystick
        self.joystick_types[instance_id] = self._get_joystick_type(joystick)
        print(f"INFO: Attached {joystick.get_name()} (Type: {self.joystick_types[instance_id]})")
        return joystick

    def _detach_joystick(self, instance_id):
        self.joystick_types.pop(instance_id, None)
        joystick = self.joysticks.pop(instance_id, None)
        if joystick is not None:
            joystick.quit()

    def update(self, events):
        processed_input = {
            "button_down": [],
            "button_up": [],
            "button_held": [],
            "dpad": (0, 0),
            "left_stick": (0.0, 0.0),
            "right_stick": (0.0, 0.0),
            "left_trigger": 0.0,
            "right_trigger": 0.0,
            "connected": [],
            "disconnected": [],
        }

        if len(events) > 100:
            events = events[-100:]

        for event in events:
            try:
                if event.type == pygame.JOYDEVICEADDED:
                    joystick = self._attach_joystick(event.device_index)
                    processed_input["connected"].append(joystick.get_instance_id())
                elif event.type == pygame.JOYDEVICEREMOVED:
                    instance_id = getattr(event, "instance_id", -1)
                    processed_input["disconnected"].append(instance_id)
                    self._detach_joystick(instance_id)
                elif event.type == pygame.JOYBUTTONDOWN:
                    instance_id = getattr(event, "instance_id", -1)
                    hw_btn = getattr(event, "button", None)
                    if hw_btn is not None:
                        virt_btn = self._map_hardware_to_virtual(instance_id, hw_btn)
                        if self._accept_button(instance_id, virt_btn):
                            self.button_states[(instance_id, virt_btn)] = True
                            processed_input["button_down"].append(virt_btn)
                elif event.type == pygame.JOYBUTTONUP:
                    instance_id = getattr(event, "instance_id", -1)
                    hw_btn = getattr(event, "button", None)
                    if hw_btn is not None:
                        virt_btn = self._map_hardware_to_virtual(instance_id, hw_btn)
                        self.button_states[(instance_id, virt_btn)] = False
                        processed_input["button_up"].append(virt_btn)
                elif event.type == pygame.JOYHATMOTION:
                    processed_input["dpad"] = event.value
                    self._map_dpad_to_buttons(event.value, processed_input)
                elif event.type == pygame.JOYAXISMOTION:
                    self._handle_axis_motion(event, processed_input)
                elif event.type == pygame.KEYDOWN:
                    self._apply_keyboard_down(event, processed_input)
                elif event.type == pygame.KEYUP:
                    self._apply_keyboard_up(event, processed_input)
            except Exception as e:
                print(f"WARNING: Error processing event {event.type}: {e}")

        for (instance_id, btn_id), pressed in self.button_states.items():
            if pressed and btn_id not in processed_input["button_held"]:
                processed_input["button_held"].append(btn_id)

        return processed_input

    def _map_dpad_to_buttons(self, dpad_value, processed_input):
        dx, dy = dpad_value
        if dy == 1: self._trigger_virt_btn(self.DPAD_UP, processed_input)
        elif dy == -1: self._trigger_virt_btn(self.DPAD_DOWN, processed_input)
        if dx == -1: self._trigger_virt_btn(self.DPAD_LEFT, processed_input)
        elif dx == 1: self._trigger_virt_btn(self.DPAD_RIGHT, processed_input)
        
        if dpad_value == (0, 0):
            for b in [self.DPAD_UP, self.DPAD_DOWN, self.DPAD_LEFT, self.DPAD_RIGHT]:
                self.button_states[(-1, b)] = False

    def _trigger_virt_btn(self, btn_id, processed_input):
        if self._accept_button(-1, btn_id):
            processed_input["button_down"].append(btn_id)
            self.button_states[(-1, btn_id)] = True

    def _handle_axis_motion(self, event, processed_input):
        axis = event.axis
        val = max(-1.0, min(1.0, event.value))
        if abs(val) < self.deadzone: val = 0.0
        
        j_type = self.joystick_types.get(event.instance_id, "xbox")
        
        # Mapping axes (0,1 = Left Stick, 2 = LT, 3,4 = Right Stick, 5 = RT)
        if axis == 0: self.left_stick = (val, self.left_stick[1])
        elif axis == 1: self.left_stick = (self.left_stick[0], val)
        elif axis == 2: self.left_trigger = val
        elif axis == 3: self.right_stick = (val, self.right_stick[1])
        elif axis == 4: self.right_stick = (self.right_stick[0], val)
        elif axis == 5: self.right_trigger = val
        
        processed_input["left_stick"] = self.left_stick
        processed_input["right_stick"] = self.right_stick
        processed_input["left_trigger"] = self.left_trigger
        processed_input["right_trigger"] = self.right_trigger

        # Map stick directions to virtual buttons
        self._map_stick_directions(self.left_stick, "left", processed_input)
        self._map_stick_directions(self.right_stick, "right", processed_input)

    def _map_stick_directions(self, pos, side, processed_input):
        x, y = pos
        thresh = self.deadzone * 2.0
        btns = {
            "left": [self.STICK_LEFT_UP, self.STICK_LEFT_DOWN, self.STICK_LEFT_LEFT, self.STICK_LEFT_RIGHT],
            "right": [self.STICK_RIGHT_UP, self.STICK_RIGHT_DOWN, self.STICK_RIGHT_LEFT, self.STICK_RIGHT_RIGHT]
        }[side]
        
        if y < -thresh: self._trigger_virt_btn(btns[0], processed_input)
        else: self.button_states[(-1, btns[0])] = False
        
        if y > thresh: self._trigger_virt_btn(btns[1], processed_input)
        else: self.button_states[(-1, btns[1])] = False
        
        if x < -thresh: self._trigger_virt_btn(btns[2], processed_input)
        else: self.button_states[(-1, btns[2])] = False
        
        if x > thresh: self._trigger_virt_btn(btns[3], processed_input)
        else: self.button_states[(-1, btns[3])] = False

    def _apply_keyboard_down(self, event, processed_input):
        mapping = {
            pygame.K_RETURN: self.BUTTON_START,
            pygame.K_SPACE: self.BUTTON_START,
            pygame.K_b: self.BUTTON_B,
            pygame.K_ESCAPE: self.BUTTON_B,
            pygame.K_UP: self.DPAD_UP,
            pygame.K_DOWN: self.DPAD_DOWN,
            pygame.K_LEFT: self.DPAD_LEFT,
            pygame.K_RIGHT: self.DPAD_RIGHT,
            pygame.K_a: self.BUTTON_A,
            pygame.K_s: self.BUTTON_B,
            pygame.K_x: self.BUTTON_X,
            pygame.K_y: self.BUTTON_Y,
        }
        if event.key in mapping:
            btn = mapping[event.key]
            if btn >= 100: # DPAD
                processed_input["dpad"] = {self.DPAD_UP: (0, 1), self.DPAD_DOWN: (0, -1), self.DPAD_LEFT: (-1, 0), self.DPAD_RIGHT: (1, 0)}[btn]
            else:
                processed_input["button_down"].append(btn)
                self.button_states[(-1, btn)] = True

    def _apply_keyboard_up(self, event, processed_input):
        # Keyboard reset not strictly needed for this logic but good for completeness
        pass

    def _accept_button(self, instance_id, button_id):
        now = time.monotonic()
        key = (instance_id, button_id)
        if now - self.input_cooldowns.get(key, 0) < self.cooldown_duration:
            return False
        self.input_cooldowns[key] = now
        return True

    def is_button_pressed(self, button_id):
        return any(v for (iid, bid), v in self.button_states.items() if bid == button_id)
