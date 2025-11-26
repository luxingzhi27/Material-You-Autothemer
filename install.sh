#!/bin/bash

# --- 配置变量 ---
PLASMOID_NAME="com.github.luxingzhi27.matugen_autothemer"
INSTALL_DIR="$HOME/.local/share/plasma/plasmoids/$PLASMOID_NAME"
# 脚本的绝对路径（由 Systemd 使用）
BRIDGE_SCRIPT_PATH="$INSTALL_DIR/scripts/matugen-kde-bridge.py"
# Systemd 服务名称
SERVICE_NAME="matugen-autothemer.service"
SERVICE_FILE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE_PATH="$SERVICE_FILE_DIR/$SERVICE_NAME"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting installation for $PLASMOID_NAME...${NC}"

# --- 0. 停止旧服务 (如果存在) ---
if systemctl --user is-active --quiet "$SERVICE_NAME"; then
    echo "Stopping existing service..."
    systemctl --user stop "$SERVICE_NAME"
fi

# --- 1. 清理旧的安装文件 ---
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing existing installation files..."
    rm -rf "$INSTALL_DIR"
fi

# --- 2. 创建安装目录 ---
echo "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# --- 3. 复制所有项目文件 ---
echo "Copying project files..."
# 使用 rsync 排除不需要的文件
rsync -av --exclude='.git' --exclude='install.sh' . "$INSTALL_DIR/"

# --- 4. 设置脚本权限 ---
if [ -f "$BRIDGE_SCRIPT_PATH" ]; then
    chmod +x "$BRIDGE_SCRIPT_PATH"
    echo "Set executable permission for bridge script."
else
    echo "Error: Bridge script not found at $BRIDGE_SCRIPT_PATH"
    exit 1
fi

# --- 5. 配置 Systemd 服务 ---
echo "Configuring Systemd service..."
mkdir -p "$SERVICE_FILE_DIR"

# 动态生成 service 文件
# 我们添加了 PATH 环境变量，以防 matugen 安装在 ~/.local/bin 下而 Systemd 找不到
cat <<EOF > "$SERVICE_FILE_PATH"
[Unit]
Description=Matugen Auto-Themer Bridge for KDE
# 确保在 Plasma 启动后运行
After=plasma-plasmashell.service

[Service]
Type=simple
# 确保 matugen 二进制文件能被找到 (通常在 ~/.local/bin 或 /usr/bin)
Environment="PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin"
# 指定解释器和脚本路径
ExecStart=$BRIDGE_SCRIPT_PATH
# 失败自动重启
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
EOF

echo "Service file created at: $SERVICE_FILE_PATH"

# 重载配置并启用服务
systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME"
echo "Starting service..."
systemctl --user start "$SERVICE_NAME"

# --- 6. 尝试刷新 Plasma 缓存 ---
echo "Refreshing Plasma cache..."
if command -v kpackagetool6 &> /dev/null; then
    kpackagetool6 --type Plasma/Applet --generate-cache &> /dev/null
elif command -v kpackagetool5 &> /dev/null; then
    kpackagetool5 --type Plasma/Applet --generate-cache &> /dev/null
fi

# --- 7. 完成提示 ---
echo ""
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "------------------------------------------------"
echo -e "1. The Plasmoid has been installed to:"
echo -e "   $INSTALL_DIR"
echo ""
echo -e "2. The background service has been registered and started:"
echo -e "   ${GREEN}$SERVICE_NAME${NC}"
echo -e "   You can check its status with: systemctl --user status $SERVICE_NAME"
echo -e "   You can view logs with: journalctl --user -u $SERVICE_NAME -f"
echo ""
echo -e "3. Add the widget to your panel (Right Click -> Add Widgets... -> Search for 'Matugen')."
echo "------------------------------------------------"
