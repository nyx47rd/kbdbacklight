import os
import subprocess
import gi

def is_linux_mint():
    if not os.path.exists("/etc/linuxmint/info"):
        return False
    return True

def find_backlight_device():
    """Finds the first keyboard backlight device using brightnessctl."""
    try:
        output = subprocess.check_output(["brightnessctl", "--list", "--machine-readable"], 
                                         universal_newlines=True)
        for line in output.splitlines():
            parts = line.split(',')
            if len(parts) >= 2:
                device_name = parts[0]
                device_class = parts[1]
                if device_class == "leds" and ("kbd" in device_name or "backlight" in device_name):
                    return device_name
    except Exception:
        pass
    return "asus::kbd_backlight"

def get_max_brightness(device):
    """Gets the maximum brightness level for the given device."""
    try:
        output = subprocess.check_output(["brightnessctl", "--device=" + device, "m"], 
                                         universal_newlines=True)
        return int(output.strip())
    except Exception:
        return 3 # Default fallback

def get_installed_dependencies():
    deps = {
        "brightnessctl": False,
        "python3-pynput": False,
        "gir1.2-keybinder-3.0": False,
        "gir1.2-xapp-1.0": False
    }
    
    # Check brightnessctl
    try:
        subprocess.run(["brightnessctl", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deps["brightnessctl"] = True
    except FileNotFoundError:
        pass
        
    # Check python packages via apt-cache (since they are system-managed)
    for pkg in ["python3-pynput", "gir1.2-keybinder-3.0", "gir1.2-xapp-1.0"]:
        res = subprocess.run(["dpkg", "-l", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            deps[pkg] = True
            
    return deps

def check_permissions():
    device = find_backlight_device()
    brightness_file = f"/sys/class/leds/{device}/brightness"
    if not os.path.exists(brightness_file):
        return False
    return os.access(brightness_file, os.W_OK)

def get_compatible_devices():
    return [
        "ASUS ROG Serisi",
        "ASUS Zephyrus Serisi",
        "ASUS TUF Gaming Serisi",
        "ASUS Zenbook Serisi",
        "Bazı MSI ve HP Modelleri (asus::kbd_backlight sürücüsünü kullananlar)"
    ]

def reset_system():
    udev_file = "/etc/udev/rules.d/99-kbd-backlight.rules"
    pkg_name = "kbdbacklight-manager"
    # Create a removal script to run with pkexec: remove rules AND uninstall package
    # We use ; instead of && so that if uninstall fails (e.g. manual install), we still remove rules
    script = f"apt remove -y {pkg_name}; rm -f {udev_file}; udevadm control --reload-rules"
    try:
        subprocess.run(["pkexec", "sh", "-c", script], check=False)
        # Remove local settings
        config_dir = os.path.expanduser("~/.config/kbdbacklight")
        import shutil
        if os.path.exists(config_dir):
            shutil.rmtree(config_dir)
        # Remove autostart entry
        autostart = os.path.expanduser("~/.config/autostart/kbd-backlight.desktop")
        if os.path.exists(autostart):
            os.remove(autostart)
        
        # NOTE: We no longer touch gsettings to avoid interrupting other user shortcuts.
        # Users can manually clean their custom keybindings if needed.
            
        return True
    except Exception as e:
        print(f"Reset error: {e}")
        return False
