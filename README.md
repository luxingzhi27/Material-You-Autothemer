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

Installation is simple! Just download the appropriate package for your distribution from our **[Releases Page](https://github.com/Luxingzhi27/Material-You-Autothemer/releases)** and run the provided install script.

#### 🐧 Arch Linux
1.  Download the `.pkg.tar.zst` file from Releases.
2.  Place it in the project folder.
3.  Run the install script:
    ```bash
    sudo ./install.sh
    ```
    *(Alternatively, you can manually install it via `sudo pacman -U filename.pkg.tar.zst`)*

#### 🌀 Debian / Ubuntu
1.  Download the `.deb` file from Releases.
2.  Place it in the project folder.
3.  Run the install script:
    ```bash
    sudo ./install.sh
    ```

#### 🎩 Fedora / OpenSUSE / CentOS (RPM)
1.  Download the `.rpm` file from Releases.
2.  Place it in the project folder.
3.  Run the install script:
    ```bash
    sudo ./install.sh
    ```

#### 📦 Other Distributions (Generic)
1.  Download the binary archive (usually a `.zip` or `.tar.gz` containing `MaterialYou-Autothemer` and `MaterialYou-Service`).
2.  Extract the files into the project folder.
3.  Run the install script:
    ```bash
    sudo ./install.sh
    ```

### 🛠️ Building from Source (Developers)

If you want to build the packages yourself, you will need **Python 3.10+** and the following dependencies:
```bash
pip install PySide6 PyInstaller
```
*Note: You also need `matugen` installed or the `matugen-bin` binary in the project root.*

To build:
```bash
# Build binaries only
python3 build.py

# Build binaries and Debian package
python3 build.py --deb

# Build binaries and RPM package
python3 build.py --rpm
```

**Note for Arch Users:** To build an RPM on Arch Linux, you must install `rpm-tools` first.

### 🚀 Usage

1.  Open **Material You Theme** from your app launcher.
    *   *The background service will automatically start on first launch.*
2.  **Select Wallpaper**:
    *   Click "Browse" to choose a folder containing your images.
    *   Click on any image in the grid to preview its color palette.
3.  **Configure Theme**:
    *   **Color Mode**: Switch between *Light* and *Dark* modes.
    *   **Flavor**: Select a flavor style.
4.  **Apply**:
    *   Click the **Apply Theme and Wallpaper** button.

---

<a name="chinese"></a>
## 🇨🇳 中文

> **将 Material Design 3 (Material You) 的美学带入您的 Linux 桌面。**

**MaterialYou-Autothemer** 是一个强大且优雅的工具，它可以根据您当前的壁纸自动生成并应用 Material You 配色方案到您的系统中。它支持 **GNOME** 和 **KDE Plasma** 桌面环境，提供无缝且统一的视觉体验。

### ✨ 功能特性

*   **动态主题**：使用 [Matugen](https://github.com/InioX/matugen) 根据您的壁纸生成完整的 Material Design 3 调色板。
*   **实时预览**：在应用之前，即时预览生成的调色板、主色调和 UI 元素。
*   **壁纸管理**：直接在应用中浏览本地文件夹、预览图片并设置桌面壁纸。
*   **多种风格 (Flavors)**：提供多种生成算法供选择（Tonal Spot, Vibrant, Expressive 等）。
*   **深浅色模式**：完全支持系统级的深色和浅色主题切换。
*   **跨桌面支持**：GNOME (adw-gtk3) 与 KDE Plasma。
*   **现代 UI**：基于 **PySide6 (Qt/QML)** 构建的精致响应式界面。

### 📥 安装指南

请前往 **[Releases 页面](https://github.com/Luxingzhi27/Material-You-Autothemer/releases)** 下载对应您发行版的安装包，然后运行安装脚本。

#### 🐧 Arch Linux
1.  下载 `.pkg.tar.zst` 文件。
2.  将其放入项目文件夹。
3.  运行安装脚本：
    ```bash
    sudo ./install.sh
    ```

#### 🌀 Debian / Ubuntu
1.  下载 `.deb` 文件。
2.  将其放入项目文件夹。
3.  运行安装脚本：
    ```bash
    sudo ./install.sh
    ```

#### 🎩 Fedora / OpenSUSE (RPM)
1.  下载 `.rpm` 文件。
2.  将其放入项目文件夹。
3.  运行安装脚本：
    ```bash
    sudo ./install.sh
    ```

#### 📦 其他发行版 (通用)
1.  下载二进制压缩包（包含 `MaterialYou-Autothemer` 和 `MaterialYou-Service`）。
2.  解压到项目文件夹。
3.  运行安装脚本：
    ```bash
    sudo ./install.sh
    ```

### 🛠️ 从源码构建 (开发者)

如果您需要自己构建包，需要安装 Python 3.10+ 以及 `PySide6` 和 `PyInstaller`。

```bash
# 仅构建二进制文件
python3 build.py

# 构建 Debian 包 (.deb)
python3 build.py --deb

# 构建 RPM 包 (.rpm)
python3 build.py --rpm
```

**Arch 用户提示**：如果您想在 Arch Linux 上构建 RPM 包，请确保先安装 `rpm-tools`。

### 🚀 使用说明

1.  从应用启动器打开 **Material You Theme**。
2.  **选择壁纸**：浏览文件夹并选择图片。
3.  **配置主题**：调整深色/浅色模式及生成风格。
4.  **应用**：点击 **Apply Theme and Wallpaper** 按钮。

### 🔧 架构说明

*   **前端**：使用 `PySide6` 和 `QML` 开发。
*   **后台服务**：由 `systemd --user` 管理的后台进程。
*   **配置**：`~/.config/MaterialYou-Autothemer/config.conf`。
*   **日志**：`~/.cache/MaterialYou-Autothemer/logs/backend.log`。

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.