#!/usr/bin/env python3
import configparser
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
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.conf"
CACHE_DIR = Path.home() / ".cache" / APP_NAME
STATE_FILE = CACHE_DIR / "state.json"
TEMP_WALLPAPER = Path(tempfile.gettempdir()) / "matugen-temp-wallpaper.png"
MATUGEN_CONFIG_PATH = (
    Path.home() / ".local" / "share" / APP_NAME / "matugen" / "config.toml"
)


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

    cmd = [
        "matugen",
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
