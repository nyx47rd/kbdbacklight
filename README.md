# Keyboard Backlight Manager (v2.7.1)

A modern, universal keyboard backlight management tool for Linux laptops. Optimized for Linux Mint and ASUS laptops, but compatible with any device supported by `brightnessctl`.

![App Screenshot](https://raw.githubusercontent.com/ysr/kbdbacklight/main/icons/keyboard-light.png) <!-- Placeholder for actual screenshot -->

## 🌟 Features
- **Universal Hardware Support**: Automatically detects keyboard backlight devices (ASUS, MSI, HP, etc.).
- **Rhythm Sequencer**: Create custom light patterns with a 16-step sequencer (1 second per step).
- **SOS Mode**: Emergency / Visual effect Morse code pattern.
- **Smart Installer**: Interactive wizard for easy setup and permission handling.
- **Temporary Light**: Backlight turns on briefly when any key is pressed (configurable duration).
- **System Tray Integration**: Control brightness and patterns from the system tray.
- **Dual Layer Shortcuts**: Supports both application-level and system-wide custom keybindings.
- **Multilingual Support**: Available in **English** and **Turkish**.

## 🚀 Installation

### Using Debian (.deb) Package (Recommended)
1. Download the latest `.deb` from the [Releases](https://github.com/ysr/kbdbacklight/releases) page.
2. Install it using:
   ```bash
   sudo apt install ./kbdbacklight-manager_2.6.0.deb
   ```
3. Launch "Keyboard Backlight Panel" from your application menu.

### From Source
1. Install dependencies:
   ```bash
   sudo apt update
   sudo apt install brightnessctl python3-gi python3-pynput gir1.2-keybinder-3.0 gir1.2-xapp-1.0
   ```
2. Clone the repository and run:
   ```bash
   python3 main.py
   ```

## 🛠 Project Structure
- `kbd_backlight_app.py`: Main GTK application logic.
- `backlight_mgr.py`: Logic for hardware interaction and rhythm engine.
- `installer_ui.py`: The beautiful interactive setup wizard.
- `i18n.py`: Internationalization module (TR/EN).
- `utils.py`: Hardware detection and system utilities.

## 🤝 Contribution
Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License
Released under the **MIT License**. See [LICENSE](LICENSE) for details.

---
Developed with ❤️ by **nyx47rd & Deepmind Team**
