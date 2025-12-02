# 🎨 MaterialYou-Autothemer

[English](#english) | [中文](#chinese)

<img src="pictures/屏幕截图_20251129_031809.png" width="48%" style="display:inline-block;"/><img src="pictures/屏幕截图_20251129_031939.png" width="48%" style="display:inline-block"/>

---

<a name="english"></a>
## 🇬🇧 English

> **Bring the beauty of Material Design 3 (Material You) to your Linux Desktop.**

**MaterialYou-Autothemer** is a powerful and elegant tool that automatically generates and applies Material You color schemes to your system based on your current wallpaper. It supports both **GNOME** and **KDE Plasma** desktop environments, offering a seamless and cohesive visual experience.

### ✨ Features

*   **Dynamic Theming**: Generates a complete Material Design 3 color palette from your wallpaper using [Matugen](https://github.com/InioX/matugen).
*   **Real-time Preview**: Visualize the generated palette, primary colors, and UI elements instantly before applying.
*   **Wallpaper Manager**: Browse local folders, preview images, and set your desktop wallpaper directly from the app.
*   **Customizable Flavors**: Choose from various generation algorithms:
    *   *Tonal Spot* (Default)
    *   *Vibrant*
    *   *Expressive*
    *   *Fruit Salad*
    *   *Rainbow*
    *   *And more...*
*   **Light & Dark Modes**: Fully supports system-wide light and dark theme switching.
*   **Cross-Desktop Support**:
    *   **GNOME**: Updates `adw-gtk3` and GTK4 settings.
    *   **KDE Plasma**: Generates and applies custom `.colors` schemes with proper metadata injection.
*   **Modern UI**: A polished, responsive interface built with **PySide6 (Qt/QML)** featuring custom window controls, animations, and tooltips.

### 📥 Installation

We provide multiple ways to install MaterialYou-Autothemer, depending on your Linux distribution and preference.

#### Method 1: Pre-built Binaries (Universal)
The easiest way to run the app on any Linux distribution without worrying about dependencies.

1.  Go to the [Releases](https://github.com/Luxingzhi27/Material-You-Autothemer/releases) page.
2.  Download the latest binary package (usually a zip or tar.gz containing `MaterialYou-Autothemer` and `MaterialYou-Service`).
3.  Extract the files to a folder of your choice.
4.  Run `MaterialYou-Autothemer`.
    *   *Note: The app will automatically register a background service for you on first run.*

#### Method 2: Debian/Ubuntu (.deb)
For Debian-based systems, you can install the `.deb` package.

1.  Download the `.deb` file from the [Releases](https://github.com/Luxingzhi27/Material-You-Autothemer/releases) page.
2.  Install it:
    ```bash
    sudo dpkg -i materialyou-autothemer_*.deb
    sudo apt-get install -f  # Fix dependencies if needed
    ```
3.  Enable the background service:
    ```bash
    systemctl --user enable --now materialyou-autothemer
    ```

#### Method 3: Arch Linux (Pacman)
For Arch Linux users, we recommend installing from source using `makepkg` for better system integration and performance.

1.  Clone this repository:
    ```bash
    git clone https://github.com/Luxingzhi27/Material-You-Autothemer.git
    cd Material-You-Autothemer
    ```
2.  Build and install the package:
    ```bash
    cd arch_pkg
    makepkg -si
    ```
3.  Enable the background service:
    ```bash
    systemctl --user enable --now materialyou-autothemer
    ```

### 🛠️ Building from Source

If you want to build the binaries yourself (e.g., for development or other distros):

1.  **Install Dependencies**:
    *   Python 3.10+
    *   `pip install PySide6 pyinstaller`
    *   `matugen` (binary in PATH or `matugen-bin` in project root)

2.  **Run Build Script**:
    ```bash
    python3 build.py
    ```
    This will generate the binaries in the `dist/` folder.

3.  **Install**:
    You can use the provided install script to install the built binaries to `/usr/local/bin`:
    ```bash
    sudo ./install.sh
    ```

### 🚀 Usage

1.  Open **Material You Theme** from your app launcher.
2.  **Select Wallpaper**:
    *   Click "Browse" to choose a folder containing your images.
    *   Click on any image in the grid to preview its color palette.
3.  **Configure Theme**:
    *   **Color Mode**: Switch between *Light* and *Dark* modes.
    *   **Flavor**: Select a flavor style (hover over buttons to see descriptions).
    *   **Preview**: Hover over the generated color circles to see their names and hex codes.
4.  **Apply**:
    *   Click the **Apply Theme and Wallpaper** button.
    *   Your system theme and wallpaper will update instantly.

---

<a name="chinese"></a>
## 🇨🇳 中文

> **将 Material Design 3 (Material You) 的美学带入您的 Linux 桌面。**

**MaterialYou-Autothemer** 是一个强大且优雅的工具，它可以根据您当前的壁纸自动生成并应用 Material You 配色方案到您的系统中。它支持 **GNOME** 和 **KDE Plasma** 桌面环境，提供无缝且统一的视觉体验。

### ✨ 功能特性

*   **动态主题**：使用 [Matugen](https://github.com/InioX/matugen) 根据您的壁纸生成完整的 Material Design 3 调色板。
*   **实时预览**：在应用之前，即时预览生成的调色板、主色调和 UI 元素。
*   **壁纸管理**：直接在应用中浏览本地文件夹、预览图片并设置桌面壁纸。
*   **多种风格 (Flavors)**：提供多种生成算法供选择：
    *   *Tonal Spot* (默认)
    *   *Vibrant* (鲜艳)
    *   *Expressive* (表现力)
    *   *Fruit Salad* (水果沙拉)
    *   *Rainbow* (彩虹)
    *   *更多...*
*   **深浅色模式**：完全支持系统级的深色和浅色主题切换。
*   **跨桌面支持**：
    *   **GNOME**：更新 `adw-gtk3` 和 GTK4 设置。
    *   **KDE Plasma**：生成并应用带有正确元数据的自定义 `.colors` 配色方案。
*   **现代 UI**：基于 **PySide6 (Qt/QML)** 构建的精致响应式界面，具有自定义窗口控件、动画效果和悬浮提示。

### 📥 安装指南

我们提供多种安装方式，请根据您的 Linux 发行版选择最适合的一种。

#### 方法 1：预构建二进制文件 (通用)
这是最简单的安装方式，无需担心依赖问题，适用于所有 Linux 发行版。

1.  前往 [Releases](https://github.com/Luxingzhi27/Material-You-Autothemer/releases) 页面。
2.  下载最新的二进制包（通常包含 `MaterialYou-Autothemer` 和 `MaterialYou-Service` 两个文件）。
3.  解压到任意文件夹。
4.  直接运行 `MaterialYou-Autothemer`。
    *   *注意：首次运行时，程序会自动为您注册后台服务。*

#### 方法 2：Debian/Ubuntu (.deb)
适用于 Debian 系用户。

1.  从 [Releases](https://github.com/Luxingzhi27/Material-You-Autothemer/releases) 页面下载 `.deb` 安装包。
2.  安装：
    ```bash
    sudo dpkg -i materialyou-autothemer_*.deb
    sudo apt-get install -f  # 修复可能缺失的依赖
    ```
3.  启用后台服务：
    ```bash
    systemctl --user enable --now materialyou-autothemer
    ```

#### 方法 3：Arch Linux (Pacman)
对于 Arch Linux 用户，我们推荐使用 `makepkg` 从源码安装，以获得最佳的系统集成和性能。

1.  克隆本仓库：
    ```bash
    git clone https://github.com/Luxingzhi27/Material-You-Autothemer.git
    cd Material-You-Autothemer
    ```
2.  构建并安装软件包：
    ```bash
    cd arch_pkg
    makepkg -si
    ```
3.  启用后台服务：
    ```bash
    systemctl --user enable --now materialyou-autothemer
    ```

### 🛠️ 从源码构建

如果您想自己构建二进制文件（例如用于开发或其他发行版）：

1.  **安装依赖**：
    *   Python 3.10+
    *   `pip install PySide6 pyinstaller`
    *   `matugen` (确保在 PATH 中，或者将 `matugen-bin` 放在项目根目录)

2.  **运行构建脚本**：
    ```bash
    python3 build.py
    ```
    构建完成后，二进制文件将位于 `dist/` 目录中。

3.  **安装**：
    您可以使用提供的安装脚本将构建好的二进制文件安装到 `/usr/local/bin`：
    ```bash
    sudo ./install.sh
    ```

### 🚀 使用说明

1.  从应用启动器打开 **Material You Theme**。
2.  **选择壁纸**：
    *   点击 "Browse" 选择包含图片的文件夹。
    *   点击网格中的任意图片以预览其调色板。
3.  **配置主题**：
    *   **颜色模式 (Color Mode)**：在 *Light* (浅色) 和 *Dark* (深色) 模式之间切换。
    *   **风格 (Flavor)**：选择一种风格样式（悬停在按钮上可查看描述）。
    *   **预览**：悬停在生成的颜色圆圈上以查看其名称和十六进制代码。
4.  **应用**：
    *   点击 **Apply Theme and Wallpaper** 按钮。
    *   您的系统主题和壁纸将立即更新。

### 🔧 架构说明

*   **前端**：使用 `PySide6` 和 `QML` 开发的 Python 应用程序，提供流畅的硬件加速 UI。
*   **后台服务**：由 `systemd --user` 管理的后台进程。它监听配置更改并处理将主题应用到特定桌面环境的繁重工作。
*   **配置**：设置存储在 `~/.config/MaterialYou-Autothemer/config.conf`。
*   **日志**：调试日志位于 `~/.cache/MaterialYou-Autothemer/logs/backend.log`。

### ❓ 故障排除

**主题没有应用？**
检查后台服务的状态：
```bash
systemctl --user status materialyou-autothemer.service
```

**需要更多详细信息？**
查看实时日志：
```bash
tail -f ~/.cache/MaterialYou-Autothemer/logs/backend.log
```

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.