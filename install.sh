#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}>>> Material You Autothemer Installer${NC}"

# --- 1. 检测发行版 ---
if [ -f /etc/arch-release ]; then
    echo -e "${GREEN}✅ Detected Arch Linux.${NC}"
    echo "----------------------------------------------------------------"
    echo "For Arch Linux, the recommended installation method is using 'makepkg'."
    echo "This will install the application from source using system Python libraries,"
    echo "which is faster and cleaner than the standalone binary."
    echo ""
    echo "👉 Please run the following commands:"
    echo -e "${BLUE}   cd arch_pkg${NC}"
    echo -e "${BLUE}   makepkg -si${NC}"
    echo "----------------------------------------------------------------"
    exit 0
fi

# --- 2. 其他发行版 (通用二进制安装) ---
echo "Detected Non-Arch System. Proceeding with Binary Installation..."

INSTALL_DIR="/usr/local/bin"
DESKTOP_DIR="/usr/share/applications"
APP_NAME="MaterialYou-Autothemer"
SERVICE_NAME="MaterialYou-Service"

# 检查是否需要构建
if [ ! -f "dist/$APP_NAME" ] || [ ! -f "dist/$SERVICE_NAME" ]; then
    echo "⚠️  Pre-built binaries not found in 'dist/'."
    echo "🔨 Running build script now (requires PyInstaller)..."

    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: python3 is required to build.${NC}"
        exit 1
    fi

    python3 build.py

    if [ $? -ne 0 ]; then
        echo -e "${RED}Build failed. Please check errors above.${NC}"
        exit 1
    fi
fi

echo "📂 Installing to $INSTALL_DIR..."

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo) to install to /usr/local/bin"
    exec sudo "$0" "$@"
    exit
fi

# 复制二进制文件
cp "dist/$APP_NAME" "$INSTALL_DIR/$APP_NAME"
cp "dist/$SERVICE_NAME" "$INSTALL_DIR/$SERVICE_NAME"
chmod +x "$INSTALL_DIR/$APP_NAME"
chmod +x "$INSTALL_DIR/$SERVICE_NAME"

# 创建桌面快捷方式
echo "🔗 Creating desktop shortcut..."
cat <<EOF > "$DESKTOP_DIR/materialyou-autothemer.desktop"
[Desktop Entry]
Name=Material You Theme
Comment=Customize your desktop colors
Exec=$APP_NAME
Icon=preferences-desktop-color
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;Utility;
EOF

echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "------------------------------------------------"
echo "1. Launch 'Material You Theme' from your application menu."
echo "2. The background service will be automatically registered and started"
echo "   when you run the application for the first time."
echo "------------------------------------------------"
