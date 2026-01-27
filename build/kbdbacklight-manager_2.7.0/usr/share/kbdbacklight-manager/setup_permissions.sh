#!/bin/bash
# Klavye arka ışığı kontrolü için yetki ayarı (root gerektirmemesi için)

RULE_FILE="/etc/udev/rules.d/99-kbd-backlight.rules"

echo "Creating udev rule for asus::kbd_backlight..."
echo 'ACTION=="add", SUBSYSTEM=="leds", KERNEL=="asus::kbd_backlight", MODE="0666"' | sudo tee $RULE_FILE > /dev/null

echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=leds

echo "Applying permissions manually for the current session..."
sudo chmod 666 /sys/class/leds/asus::kbd_backlight/brightness
echo "You may need to unplug/replug the device or restart the app for it to take effect."
echo "On a laptop, it should take effect immediately."
