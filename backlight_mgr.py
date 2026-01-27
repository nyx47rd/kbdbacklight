import subprocess
import gi
from gi.repository import GLib

try:
    from pynput import keyboard
except ImportError:
    keyboard = None

import utils

class BacklightManager:
    def __init__(self, settings, notify_callback=None):
        self.device = utils.find_backlight_device()
        self.max_brightness = utils.get_max_brightness(self.device)
        self.settings = settings
        self.notify_callback = notify_callback
        self.temp_timer_id = None
        self.global_listener = None
        self.effect_timer_id = None
        
        if self.settings.get("temp_light_enabled", False):
            self.start_global_listener()

    def get_brightness(self):
        try:
            output = subprocess.check_output(["brightnessctl", "--device=" + self.device, "get"], 
                                             universal_newlines=True)
            return int(output.strip())
        except Exception:
            return 0

    def set_brightness(self, value):
        try:
            # Clamp value
            value = max(0, min(self.max_brightness, value))
            subprocess.run(["brightnessctl", "--device=" + self.device, "set", str(value), "--quiet"], check=True)
            if self.notify_callback:
                self.notify_callback(value)
        except Exception as e:
            print(f"Set brightness error: {e}")

    def adjust_brightness(self, delta):
        curr = self.get_brightness()
        new = max(0, min(self.max_brightness, curr + delta))
        self.set_brightness(new)

    def activate_temp_light(self):
        if not self.settings.get("temp_light_enabled", False):
            return
            
        # Use a smart level for temp light: either max or a percentage of max
        # If max is 1 (on/off), use 1. If 3, use 2.
        level = max(1, self.max_brightness - 1) if self.max_brightness > 1 else self.max_brightness
        GLib.idle_add(self.set_brightness, level)
        
        if self.temp_timer_id:
            GLib.source_remove(self.temp_timer_id)
            
        duration = self.settings.get("temp_light_duration", 10)
        self.temp_timer_id = GLib.timeout_add_seconds(duration, self.deactivate_temp_light)

    def deactivate_temp_light(self):
        GLib.idle_add(self.set_brightness, 0)
        self.temp_timer_id = None
        return False

    def start_global_listener(self):
        if not keyboard or self.global_listener:
            return
        self.global_listener = keyboard.Listener(on_press=lambda k: self.activate_temp_light())
        self.global_listener.daemon = True
        self.global_listener.start()

    def stop_global_listener(self):
        if self.global_listener:
            self.global_listener.stop()
            self.global_listener = None

    def play_pattern(self, pattern, loop=True):
        """Plays a rhythm pattern. pattern is a list of (brightness, duration_ms) tuples."""
        self.stop_pattern()
        
        step_idx = [0] # Use list to make it mutable in nested scope
        
        def run_step():
            if not self.effect_timer_id:
                return False
            
            brightness, duration = pattern[step_idx[0]]
            self.set_brightness(brightness)
            
            step_idx[0] += 1
            if step_idx[0] >= len(pattern):
                if loop:
                    step_idx[0] = 0
                else:
                    self.effect_timer_id = None
                    return False
            
            self.effect_timer_id = GLib.timeout_add(duration, run_step)
            return False # Stop current timeout, new one is started above

        self.effect_timer_id = True # Flag as running
        run_step()

    def stop_pattern(self):
        if self.effect_timer_id and self.effect_timer_id is not True:
            GLib.source_remove(self.effect_timer_id)
        self.effect_timer_id = None
