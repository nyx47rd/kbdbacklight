#!/bin/bash
export PATH=/usr/bin:/bin:/usr/local/bin:$PATH

# Configuration
PKG_NAME="kbdbacklight-manager"
PKG_VERSION="2.6.0"
PKG_DIR="build/${PKG_NAME}_${PKG_VERSION}"
INSTALL_DIR="${PKG_DIR}/usr/share/${PKG_NAME}"
BIN_DIR="${PKG_DIR}/usr/bin"
APP_DIR="${PKG_DIR}/usr/share/applications"

# Clean previous builds
rm -rf build
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BIN_DIR}"
mkdir -p "${APP_DIR}"
mkdir -p "${PKG_DIR}/DEBIAN"

# Copy source files
cp main.py "${INSTALL_DIR}/"
cp kbd_backlight_app.py "${INSTALL_DIR}/"
cp backlight_mgr.py "${INSTALL_DIR}/"
cp config.py "${INSTALL_DIR}/"
cp utils.py "${INSTALL_DIR}/"
cp i18n.py "${INSTALL_DIR}/"
cp installer_ui.py "${INSTALL_DIR}/"
cp setup_permissions.sh "${INSTALL_DIR}/"

# Create executable entry
cat <<EOF > "${BIN_DIR}/kbdbacklight"
#!/bin/bash
python3 /usr/share/${PKG_NAME}/main.py "\$@"
EOF
chmod +x "${BIN_DIR}/kbdbacklight"

# Create desktop entry
cp kbd-backlight.desktop "${APP_DIR}/kbdbacklight-manager.desktop"

# Create Control file
cat <<EOF > "${PKG_DIR}/DEBIAN/control"
Package: ${PKG_NAME}
Version: ${PKG_VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-keybinder-3.0, gir1.2-xapp-1.0, brightnessctl, python3-pynput
Maintainer: Antigravity & Deepmind Team
Description: Universal Keyboard Backlight Manager for Linux
 A modern, GTK-based tool to manage keyboard backlight with global shortcuts
 and a system-wide temporary backlight feature. Compatible with Linux Mint.
EOF

# Create Post-install script
cat <<EOF > "${PKG_DIR}/DEBIAN/postinst"
#!/bin/bash
chmod +x /usr/share/${PKG_NAME}/setup_permissions.sh
# Run permission setup automatically
/usr/share/${PKG_NAME}/setup_permissions.sh
exit 0
EOF
chmod +x "${PKG_DIR}/DEBIAN/postinst"

# Build the package
dpkg-deb --build "${PKG_DIR}"

echo "Debian package created: build/${PKG_NAME}_${PKG_VERSION}.deb"
