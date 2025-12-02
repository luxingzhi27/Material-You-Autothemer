#!/usr/bin/env python3
import configparser
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from backend.logger import log
except ImportError:
    import logging

    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

# --- 基础配置 ---
APP_NAME = "MaterialYou-Autothemer"

# 强制使用 XDG 标准路径 (Arch Linux/Single File 模式需求)
# 无论是否打包，配置都存放在 ~/.config/MaterialYou-Autothemer
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.conf"
CACHE_DIR = Path.home() / ".cache" / APP_NAME
STATE_FILE = CACHE_DIR / "state.json"
LOCK_FILE = CACHE_DIR / "service.lock"
TEMP_WALLPAPER = Path(tempfile.gettempdir()) / "matugen-temp-wallpaper.png"

# Matugen 配置路径 (用户希望放在 .config 下以便修改)
MATUGEN_CONFIG_DIR = CONFIG_DIR / "matugen"
MATUGEN_CONFIG_PATH = MATUGEN_CONFIG_DIR / "config.toml"


def init_resources():
    """
    初始化资源文件：
    如果是第一次运行（或者配置文件不存在），将打包在内的 matugen 配置文件
    释放到用户的 ~/.config/MaterialYou-Autothemer/matugen 目录下。
    这样用户就可以自定义修改配置了。
    """
    if MATUGEN_CONFIG_PATH.exists():
        return

    log.info("Initializing configuration files...")

    # 1. 确定源路径
    source_matugen_dir = None

    if getattr(sys, "frozen", False):
        # PyInstaller --onefile 模式：资源在临时目录 _MEIPASS 中
        base_path = Path(sys._MEIPASS)
        source_matugen_dir = base_path / "matugen"
    else:
        # 源码模式
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        source_matugen_dir = project_root / "matugen"

    # 2. 复制文件
    if source_matugen_dir and source_matugen_dir.exists():
        try:
            MATUGEN_CONFIG_DIR.parent.mkdir(parents=True, exist_ok=True)
            # 复制整个 matugen 文件夹（包含 config.toml 和 templates）
            if not MATUGEN_CONFIG_DIR.exists():
                shutil.copytree(
                    source_matugen_dir, MATUGEN_CONFIG_DIR, dirs_exist_ok=True
                )
                log.info(f"Copied default config to {MATUGEN_CONFIG_DIR}")
        except Exception as e:
            log.error(f"Failed to initialize resources: {e}")
    else:
        log.warning("Could not find default matugen configuration to copy.")


def get_matugen_command():
    """获取 matugen 可执行文件路径"""
    # 1. 检查 PyInstaller 临时目录 (单文件模式下，二进制文件会被解压到这里)
    if getattr(sys, "frozen", False):
        # 优先检查 bin 子目录 (避免与 matugen 配置文件夹冲突)
        bundled_bin = Path(sys._MEIPASS) / "bin" / "matugen"
        if bundled_bin.is_file() and os.access(bundled_bin, os.X_OK):
            return str(bundled_bin)

        meipass_bin = Path(sys._MEIPASS) / "matugen"
        # 必须确保是文件且可执行
        if meipass_bin.is_file() and os.access(meipass_bin, os.X_OK):
            return str(meipass_bin)

    # 2. 检查系统 PATH
    if shutil.which("matugen"):
        return "matugen"

    # 3. 检查当前目录 (开发环境)
    if os.path.isfile("./matugen") and os.access("./matugen", os.X_OK):
        return "./matugen"

    return "matugen"  # 期望在 PATH 中


def ensure_service_running():
    """
    检查并自动安装/启动 Systemd 用户服务。
    服务会指向同目录下的 MaterialYou-Service 可执行文件。
    """
    is_frozen = getattr(sys, "frozen", False)
    is_system_install = os.environ.get("APP_MODE") == "INSTALLED_SYSTEM"

    # 仅在 Linux 下运行
    # 必须是打包环境 (PyInstaller) 或者系统安装模式 (Pacman)
    if not sys.platform.startswith("linux") or (
        not is_frozen and not is_system_install
    ):
        return

    service_dir = Path.home() / ".config" / "systemd" / "user"
    service_file = service_dir / "materialyou-autothemer.service"

    # 获取当前可执行文件所在的目录
    # 如果是系统安装模式，sys.executable 是 /usr/bin/python3，parent 是 /usr/bin
    # 这正好是我们存放 wrapper 脚本的地方
    exe_dir = Path(sys.executable).parent.resolve()

    # 查找后端服务可执行文件 (解耦后的独立二进制 或 Wrapper 脚本)
    backend_exe = exe_dir / "MaterialYou-Service"

    if not backend_exe.exists():
        log.warning(
            f"Backend service executable not found at {backend_exe}. Skipping service registration."
        )
        return

    backend_exe_path = str(backend_exe)

    # 服务文件内容
    service_content = f"""[Unit]
Description=Material You Autothemer Backend Service
After=graphical-session.target

[Service]
Type=simple
ExecStart="{backend_exe_path}"
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
"""

    try:
        service_dir.mkdir(parents=True, exist_ok=True)

        # 检查是否需要更新服务文件 (路径变动或文件不存在)
        need_update = True
        if service_file.exists():
            with open(service_file, "r") as f:
                if f.read() == service_content:
                    need_update = False

        if need_update:
            log.info("Installing/Updating systemd service...")
            with open(service_file, "w") as f:
                f.write(service_content)

            subprocess.run(["systemctl", "--user", "daemon-reload"], check=False)
            subprocess.run(
                ["systemctl", "--user", "enable", "materialyou-autothemer"], check=False
            )
            subprocess.run(
                ["systemctl", "--user", "restart", "materialyou-autothemer"],
                check=False,
            )
            log.info("Service installed and restarted.")
        else:
            # 确保服务正在运行
            subprocess.run(
                ["systemctl", "--user", "start", "materialyou-autothemer"], check=False
            )

    except Exception as e:
        log.error(f"Failed to setup systemd service: {e}")


def acquire_lock():
    """尝试获取文件锁，用于确保只有一个后台服务在运行"""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        # 注意：这里我们保持文件打开状态，直到进程结束
        # 必须将 fp 存储在全局或持久对象中，否则被 GC 回收后锁会释放
        global _lock_fp
        _lock_fp = open(LOCK_FILE, "w")
        fcntl.lockf(_lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except IOError:
        return False


def get_desktop_env():
    return os.environ.get("XDG_CURRENT_DESKTOP", "").lower()


def read_config():
    """读取用户配置"""
    mode = "dark"
    flavor = "tonal-spot"
    wallpaper_folder = str(Path.home() / "Pictures")
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        if "General" in config:
            mode = config["General"].get("colorMode", "dark").replace('"', "")
            flavor = config["General"].get("flavor", "tonal-spot").replace('"', "")
            wallpaper_folder = (
                config["General"]
                .get("wallpaperFolder", str(Path.home() / "Pictures"))
                .replace('"', "")
            )
    except Exception as e:
        log.warning(f"Failed to read config: {e}")
    return mode, flavor, wallpaper_folder


def save_state(wallpaper_path):
    """保存当前处理好的壁纸路径到缓存，供前端快速读取"""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, "w") as f:
            json.dump({"current_wallpaper": str(wallpaper_path)}, f)
    except Exception as e:
        log.warning(f"Failed to save state: {e}")


def get_cached_wallpaper():
    """尝试读取缓存的壁纸路径"""
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                path = data.get("current_wallpaper", "")
                if path and os.path.exists(path):
                    return path
    except:
        pass
    return None


def resolve_kde_wallpaper(path, mode="dark"):
    """[KDE] 解析动态壁纸包"""
    if not path or not os.path.isdir(path):
        return path

    search_paths = []
    if mode == "dark":
        search_paths.append(os.path.join(path, "contents", "images_dark"))
    search_paths.append(os.path.join(path, "contents", "images"))
    search_paths.append(path)

    valid_exts = (".png", ".jpg", ".jpeg", ".webp", ".jxl", ".svg")
    for p in search_paths:
        if os.path.exists(p) and os.path.isdir(p):
            try:
                files = os.listdir(p)
                images = [f for f in files if f.lower().endswith(valid_exts)]
                if images:
                    images.sort()
                    return os.path.join(p, images[0])
            except OSError:
                continue
    return path


def ensure_compatible_image(image_path):
    """[通用] JXL 转换与缓存"""
    if not image_path or not os.path.exists(image_path):
        return image_path
    if not image_path.lower().endswith(".jxl"):
        return image_path

    if not shutil.which("djxl"):
        log.warning("JXL wallpaper detected but 'djxl' not found.")
        return image_path

    try:
        # 仅当源文件更新时才转换
        if not TEMP_WALLPAPER.exists() or os.path.getmtime(
            image_path
        ) > os.path.getmtime(TEMP_WALLPAPER):
            log.info(f"Converting JXL to PNG: {image_path}")
            subprocess.run(["djxl", image_path, str(TEMP_WALLPAPER)], check=True)
        return str(TEMP_WALLPAPER)
    except Exception as e:
        log.error(f"JXL conversion failed: {e}")
        return image_path


def get_current_wallpaper(mode="dark"):
    """[通用] 获取并预处理当前壁纸"""
    desktop = get_desktop_env()
    raw_path = ""

    try:
        if "gnome" in desktop:
            import gi

            gi.require_version("Gio", "2.0")
            from gi.repository import Gio

            settings = Gio.Settings.new("org.gnome.desktop.background")
            key = "picture-uri-dark" if mode == "dark" else "picture-uri"
            raw_path = settings.get_string(key).replace("file://", "").strip("'")

        elif "kde" in desktop:
            # 使用 python-dbus 替代外部命令
            import dbus

            bus = dbus.SessionBus()
            plasma = dbus.Interface(
                bus.get_object("org.kde.plasmashell", "/PlasmaShell"),
                "org.kde.PlasmaShell",
            )
            script = """
            var allDesktops = desktops();
            var wallpaper = "";
            for (i=0; i<allDesktops.length; i++) {
                d = allDesktops[i];
                d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                if (d.readConfig("Image")) { wallpaper = d.readConfig("Image"); break; }
            }
            print(wallpaper);
            """
            res = str(plasma.evaluateScript(script))
            raw_path = resolve_kde_wallpaper(res.strip().replace("file://", ""), mode)

    except Exception as e:
        log.error(f"Wallpaper fetch error: {e}")
        return None

    return ensure_compatible_image(raw_path)


def run_matugen(
    image_path, mode, flavor, dry_run=False, config_path=MATUGEN_CONFIG_PATH
):
    """[通用] 运行 Matugen"""
    if not image_path or not os.path.exists(image_path):
        return None

    type_arg = f"scheme-{flavor}" if not flavor.startswith("scheme-") else flavor

    matugen_bin = get_matugen_command()

    cmd = [
        matugen_bin,
        "image",
        image_path,
        "--config",
        str(config_path),
        "--mode",
        mode,
        "--type",
        type_arg,
    ]

    if dry_run:
        cmd.extend(["--json", "hex", "--dry-run"])

    log.debug(f"Running Matugen: {' '.join(cmd)}")

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if dry_run:
            log.debug(f"Matugen output: {res.stdout}")
            return res.stdout

        # [KDE] Create MaterialYouAlt color scheme
        if "kde" in get_desktop_env():
            try:
                colors_dir = Path.home() / ".local/share/color-schemes"
                src = colors_dir / "MaterialYou.colors"
                dst = colors_dir / "MaterialYouAlt.colors"

                if src.exists():
                    kde_type = "Dark" if mode == "dark" else "Light"

                    # Update original MaterialYou.colors
                    conf_src = configparser.ConfigParser(interpolation=None)
                    conf_src.optionxform = str
                    conf_src.read(src)

                    if not conf_src.has_section("General"):
                        conf_src.add_section("General")

                    conf_src.set("General", "Type", kde_type)

                    with open(src, "w") as f:
                        conf_src.write(f, space_around_delimiters=False)

                    # Create MaterialYouAlt
                    shutil.copy(src, dst)

                    conf = configparser.ConfigParser(interpolation=None)
                    conf.optionxform = str
                    conf.read(dst)

                    if not conf.has_section("General"):
                        conf.add_section("General")

                    conf.set("General", "ColorScheme", "MaterialYouAlt")
                    conf.set("General", "Name", "MaterialYouAlt")

                    with open(dst, "w") as f:
                        conf.write(f, space_around_delimiters=False)

                    log.info(
                        "Updated MaterialYou.colors and created MaterialYouAlt.colors for KDE"
                    )
            except Exception as e:
                log.error(f"Failed to create MaterialYouAlt: {e}")

        return True
    except subprocess.CalledProcessError as e:
        log.error(f"Matugen failed with code {e.returncode}")
        log.error(f"STDERR: {e.stderr}")
        if e.stdout:
            log.error(f"STDOUT: {e.stdout}")
        return None
