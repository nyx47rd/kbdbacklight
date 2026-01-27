import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/kbdbacklight")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
AUTOSTART_FILE = os.path.expanduser("~/.config/autostart/kbd-backlight.desktop")

DEFAULT_SETTINGS = {
    "last_brightness": 3,
    "autostart": False,
    "shortcut_up": "Atanmadı",
    "shortcut_down": "Atanmadı",
    "temp_light_enabled": False,
    "temp_light_duration": 10,
    "is_installed": False,
    "language": "tr"
}

def load_settings():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                settings = json.load(f)
                # Ensure all default keys exist
                for k, v in DEFAULT_SETTINGS.items():
                    if k not in settings:
                        settings[k] = v
                return settings
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(settings, f)

def update_autostart(active, script_path):
    if active:
        os.makedirs(os.path.dirname(AUTOSTART_FILE), exist_ok=True)
        content = f"""[Desktop Entry]
Type=Application
Exec=python3 {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Keyboard Backlight Manager
Comment=Manage keyboard backlight brightness
"""
        with open(AUTOSTART_FILE, 'w') as f:
            f.write(content)
        os.chmod(AUTOSTART_FILE, 0o755)
    else:
        if os.path.exists(AUTOSTART_FILE):
            os.remove(AUTOSTART_FILE)
