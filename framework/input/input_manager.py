import pygame

class InputManager:
    def __init__(self):
        self.joysticks = {}
        self.button_states = {}
        self.input_cooldowns = {}
        self.cooldown_duration = 0.1 # seconds

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joy.init()
                self.joysticks[joy.get_id()] = joy
            elif event.type == pygame.JOYDEVICEREMOVED:
                if event.instance_id in self.joysticks:
                    self.joysticks[event.instance_id].quit()
                    del self.joysticks[event.instance_id]
        
    def is_button_pressed(self, button_id):
        # Implementation for polling buttons with debouncing/cooldowns
        pass
