DEFAULT_SETTINGS = {
    "last_brightness": 3,
    "autostart": False,
    "temp_light_enabled": False,
    "temp_light_duration": 10,
    "is_installed": False,
    "language": "tr"
}

import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/kbdbacklight")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

def load_settings():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = DEFAULT_SETTINGS.copy()
                merged.update(settings)
                return merged
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Save settings error: {e}")

def update_autostart(enabled, script_path):
    autostart_dir = os.path.expanduser("~/.config/autostart")
    if not os.path.exists(autostart_dir):
        os.makedirs(autostart_dir)
    
    desktop_file = os.path.join(autostart_dir, "kbd-backlight.desktop")
    if enabled:
        content = f"""[Desktop Entry]
Type=Application
Exec=python3 {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Klavye Işığı Paneli
Comment=Klavye arka ışığını yönetin
Icon=display-brightness-symbolic
"""
        with open(desktop_file, "w") as f:
            f.write(content)
    else:
        if os.path.exists(desktop_file):
            os.remove(desktop_file)
