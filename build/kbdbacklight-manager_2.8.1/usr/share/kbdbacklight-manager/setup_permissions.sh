#!/bin/bash
# Klavye arka ışığı kontrolü için yetki ayarı (root gerektirmemesi için)

RULE_FILE="/etc/udev/rules.d/99-kbd-backlight.rules"

# Auto-detect device if possible (since this script runs AFTER deps are installed)
DETECTED=$(ls /sys/class/leds/ | grep -E 'kbd_backlight|kb_backlight|keyboard_backlight' | head -n 1)

if [ -z "$DETECTED" ]; then
    # Try broader search
    DETECTED=$(ls /sys/class/leds/ | grep -E 'kbd|backlight' | grep -v "screen" | head -n 1)
fi

DEVICE="${DETECTED:-asus::kbd_backlight}"
echo "Auto-detected device: $DEVICE"

# Validate that the device actually exists
if [ ! -d "/sys/class/leds/$DEVICE" ]; then
    echo "Error: Device /sys/class/leds/$DEVICE does not exist."
    exit 1
fi

echo "Creating udev rule for $DEVICE..."
echo "ACTION==\"add\", SUBSYSTEM==\"leds\", KERNEL==\"$DEVICE\", RUN+=\"/bin/chmod 666 /sys/class/leds/%k/brightness\"" | tee $RULE_FILE > /dev/null

echo "Reloading udev rules..."
udevadm control --reload-rules
udevadm trigger --subsystem-match=leds

echo "Applying permissions manually for the current session..."
chmod 666 "/sys/class/leds/$DEVICE/brightness"
echo "You may need to unplug/replug the device or restart the app for it to take effect."
echo "On a laptop, it should take effect immediately."
