#!/bin/bash

APP_NAME="MaterialYou-Autothemer"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
DESKTOP_FILE_DIR="$HOME/.local/share/applications"
SYSTEMD_DIR="$HOME/.config/systemd/user"
SERVICE_NAME="materialyou-autothemer.service"
CACHE_DIR="$HOME/.cache/$APP_NAME"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}>>> Installing $APP_NAME...${NC}"

# --- 1. 清理旧安装 ---
echo "🧹 Cleaning up previous installation..."

# 停止服务
if systemctl --user is-active --quiet $SERVICE_NAME; then
    systemctl --user stop $SERVICE_NAME
fi
systemctl --user disable $SERVICE_NAME 2>/dev/null

# 删除文件
rm -f "$SYSTEMD_DIR/$SERVICE_NAME"
rm -rf "$INSTALL_DIR"
rm -rf "$CACHE_DIR"
rm -f "$DESKTOP_FILE_DIR/materialyou-autothemer.desktop"
rm -f "$DESKTOP_FILE_DIR/matugen-controller.desktop"

# 清理当前目录的 python 缓存，防止旧逻辑干扰
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null

# --- 2. 检查依赖 ---
echo "🔍 Checking dependencies..."
DEPS=("python3" "matugen")
if [[ "$XDG_CURRENT_DESKTOP" =~ "GNOME" ]]; then DEPS+=("sassc"); fi

for dep in "${DEPS[@]}"; do
    if ! command -v $dep &> /dev/null; then
        echo -e "${RED}Error: Required dependency '$dep' is missing.${NC}"
        exit 1
    fi
done

if ! python3 -c "import PySide6" &> /dev/null; then
    echo -e "${RED}Warning: PySide6 not found. Please install via package manager.${NC}"
fi

# --- 3. 复制文件 ---
echo "📂 Copying files to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

if [ ! -d "backend" ] || [ ! -d "frontend" ] || [ ! -d "matugen" ]; then
    echo -e "${RED}Error: Source directories (backend, frontend, matugen) missing!${NC}"
    exit 1
fi

cp -r backend frontend matugen "$INSTALL_DIR/"

chmod +x "$INSTALL_DIR/backend/bridge.py"
chmod +x "$INSTALL_DIR/frontend/gui.py"

# --- 4. 桌面快捷方式 ---
echo "🔗 Creating desktop shortcut..."
cat <<EOF > "$DESKTOP_FILE_DIR/materialyou-autothemer.desktop"
[Desktop Entry]
Name=Material You Theme
Comment=Customize your desktop colors
# 使用 sh -c 确保环境变量正确
Exec=sh -c "cd $INSTALL_DIR && python3 frontend/gui.py"
Icon=preferences-desktop-color
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;Utility;
EOF

# --- 5. 后台服务 ---
echo "⚙️ Configuring background service..."
mkdir -p "$SYSTEMD_DIR"

cat <<EOF > "$SYSTEMD_DIR/$SERVICE_NAME"
[Unit]
Description=Matugen Backend Service
After=graphical-session.target

[Service]
Type=simple
Environment="PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin"
# 设置 PYTHONPATH 确保能找到 utils
Environment="PYTHONPATH=$INSTALL_DIR"
ExecStart=/usr/bin/python3 $INSTALL_DIR/backend/bridge.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now $SERVICE_NAME

echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "------------------------------------------------"
echo -e "1. Launch **Material You Theme** from your application menu."
echo -e "2. Check service logs if needed: journalctl --user -u $SERVICE_NAME -f"
echo "------------------------------------------------"
