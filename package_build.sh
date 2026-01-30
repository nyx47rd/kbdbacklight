#!/bin/bash
export PATH=/usr/bin:/bin:/usr/local/bin:$PATH

# Configuration
PKG_NAME="kbdbacklight-manager"
PKG_VERSION="2.8.3"
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
Package: kbdbacklight-manager
Version: 2.8.3
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-gi, python3-pynput, brightnessctl, gir1.2-gtk-3.0, gir1.2-xapp-1.0
Maintainer: Gemini & nyx47rd
Description: Keyboard Backlight Manager
 A universal keyboard backlight management tool for Linux.
 Supports ASUS, MSI, HP and more.
Installed-Size: $(du -ks build | cut -f 1)
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
