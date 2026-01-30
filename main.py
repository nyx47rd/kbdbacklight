#!/usr/bin/env python3
import sys
import subprocess
import utils
import config
from installer_ui import InstallerWindow
from kbd_backlight_app import KbdBacklightApp
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def start_main_app():
    # Kill any existing instances first and run
    subprocess.run(["pkill", "-f", "kbd_backlight_app.py"])
    app = KbdBacklightApp()
    # Gtk.Application.run() starts its own main loop
    app.run(sys.argv)

def main():
    # If called without args, we might need the installer
    if len(sys.argv) == 1:
        settings = config.load_settings()
        
        # Priority check: If marked as installed, launch setup ONLY if critically broken
        # But to avoid loop, we default to launching app if 'is_installed' is true.
        if settings.get("is_installed", False):
            start_main_app()
            return

        deps = utils.get_installed_dependencies()
        # Initial install check
        needs_installer = not all(deps.values()) or not utils.check_permissions()
        
        if needs_installer:
            installer = InstallerWindow(on_complete_callback=start_main_app)
            installer.connect("destroy", Gtk.main_quit)
            Gtk.main()
            return

    start_main_app()

if __name__ == "__main__":
    main()
