#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

APP_NAME="MaterialYou-Autothemer"
SERVICE_NAME="MaterialYou-Service"

echo -e "${BLUE}>>> Material You Autothemer Installer${NC}"
echo "This script installs the application using pre-built packages."
echo "Please ensure you have downloaded the correct package for your system from the Releases page."
echo ""

# --- 1. Arch Linux ---
if [ -f /etc/arch-release ]; then
    echo -e "${GREEN}✅ Detected Arch Linux.${NC}"

    PKG_FILE=$(find . -maxdepth 1 -name "*.pkg.tar.zst" | head -n 1)

    if [ -n "$PKG_FILE" ]; then
        echo "📦 Found package: $PKG_FILE"
        echo "Installing..."
        sudo pacman -U "$PKG_FILE"
        echo -e "${GREEN}✅ Installation Complete!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Error: Arch package (*.pkg.tar.zst) not found.${NC}"
        echo "Please download the package from the Releases page and place it in this directory."
        exit 1
    fi
fi

# --- 2. Debian/Ubuntu ---
if [ -f /etc/debian_version ]; then
    echo -e "${GREEN}✅ Detected Debian/Ubuntu based system.${NC}"

    DEB_FILE=$(find . -maxdepth 1 -name "*.deb" | head -n 1)

    if [ -n "$DEB_FILE" ]; then
        echo "📦 Found package: $DEB_FILE"
        echo "Installing..."

        if command -v apt &> /dev/null; then
            sudo apt install "./$DEB_FILE" -y
        else
            sudo dpkg -i "$DEB_FILE"
            sudo apt-get install -f -y
        fi

        echo -e "${GREEN}✅ Installation Complete!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Error: Debian package (*.deb) not found.${NC}"
        echo "Please download the .deb package from the Releases page and place it in this directory."
        exit 1
    fi
fi

# --- 3. Fedora/RHEL/CentOS/OpenSUSE (RPM) ---
if [ -f /etc/redhat-release ] || [ -f /etc/SuSE-release ] || [ -f /etc/fedora-release ]; then
    echo -e "${GREEN}✅ Detected RPM-based system.${NC}"

    RPM_FILE=$(find . -maxdepth 1 -name "*.rpm" | head -n 1)

    if [ -n "$RPM_FILE" ]; then
        echo "📦 Found package: $RPM_FILE"
        echo "Installing..."

        if command -v dnf &> /dev/null; then
            sudo dnf install "./$RPM_FILE" -y
        elif command -v zypper &> /dev/null; then
            sudo zypper install "./$RPM_FILE"
        else
            sudo rpm -ivh "$RPM_FILE"
        fi

        echo -e "${GREEN}✅ Installation Complete!${NC}"
        exit 0
    else
        echo -e "${RED}❌ Error: RPM package (*.rpm) not found.${NC}"
        echo "Please download the .rpm package from the Releases page and place it in this directory."
        exit 1
    fi
fi

# --- 4. Generic Linux (Binaries) ---
echo "Detected Generic Linux System."

if [ -f "$APP_NAME" ] && [ -f "$SERVICE_NAME" ]; then
    echo -e "${GREEN}📦 Found binaries: $APP_NAME, $SERVICE_NAME${NC}"
else
    # Check inside a dist folder just in case
    if [ -f "dist/$APP_NAME" ] && [ -f "dist/$SERVICE_NAME" ]; then
         cd dist
         echo -e "${GREEN}📦 Found binaries in dist/${NC}"
    else
        echo -e "${RED}❌ Error: Binaries not found.${NC}"
        echo "Please download the binary archive from the Releases page,"
        echo "extract it here, and ensure '$APP_NAME' and '$SERVICE_NAME' are present."
        exit 1
    fi
fi

INSTALL_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"

echo "📂 Installing to $INSTALL_DIR..."

# Request root once
echo -e "${BLUE}🔒 Requesting root permissions...${NC}"
sudo -v

sudo cp "$APP_NAME" "$INSTALL_DIR/$APP_NAME"
sudo cp "$SERVICE_NAME" "$INSTALL_DIR/$SERVICE_NAME"
sudo chmod +x "$INSTALL_DIR/$APP_NAME"
sudo chmod +x "$INSTALL_DIR/$SERVICE_NAME"

echo "🔗 Creating desktop shortcut..."
TMP_DESKTOP=$(mktemp)
cat <<EOF > "$TMP_DESKTOP"
[Desktop Entry]
Name=Material You Theme
Comment=Customize your desktop colors
Exec=$APP_NAME
Icon=preferences-desktop-color
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;Utility;
EOF

sudo mv "$TMP_DESKTOP" "$DESKTOP_DIR/materialyou-autothemer.desktop"
sudo chmod 644 "$DESKTOP_DIR/materialyou-autothemer.desktop"

echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "------------------------------------------------"
echo "1. Launch 'Material You Theme' from your application menu."
echo "2. The background service will be automatically registered and started"
echo "   when you run the application for the first time."
echo "------------------------------------------------"
