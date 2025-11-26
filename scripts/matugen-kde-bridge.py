#!/usr/bin/env python3
import dbus
import time
import subprocess
import os
import logging
import configparser
import shutil
import sys

# --- 路径动态配置区域 ---

CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
CURRENT_SCRIPT_DIR = os.path.dirname(CURRENT_SCRIPT_PATH)
PLASMOID_BASE_DIR = os.path.dirname(CURRENT_SCRIPT_DIR)

MATUGEN_DIR = os.path.join(PLASMOID_BASE_DIR, "matugen")
MATUGEN_CONFIG = os.path.join(MATUGEN_DIR, "config.toml")

USER_CONFIG_FILE = os.path.expanduser("~/.config/matugen-kde/config.conf")
MATUGEN_BIN = "matugen"

# 配色方案的标准安装路径
COLOR_SCHEME_DIR = os.path.expanduser("~/.local/share/color-schemes")
THEME_NAME_MAIN = "MaterialYou"
THEME_NAME_ALT = "MaterialYouAlt"
THEME_FILE_MAIN = os.path.join(COLOR_SCHEME_DIR, f"{THEME_NAME_MAIN}.colors")
THEME_FILE_ALT = os.path.join(COLOR_SCHEME_DIR, f"{THEME_NAME_ALT}.colors")

CHECK_INTERVAL = 2.0

# --- 配置结束 ---

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class StateManager:
    def __init__(self):
        self.last_wallpaper = None
        self.last_config_mtime = 0
        self.mode = "dark"
        self.flavor = "tonal-spot"

    def get_current_wallpaper(self):
        try:
            bus = dbus.SessionBus()
            plasma_obj = bus.get_object("org.kde.plasmashell", "/PlasmaShell")
            plasma = dbus.Interface(plasma_obj, dbus_interface="org.kde.PlasmaShell")
            script = """
            var allDesktops = desktops();
            var wallpaper = "";
            for (i=0; i<allDesktops.length; i++) {
                d = allDesktops[i];
                d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
                if (d.readConfig("Image")) {
                    wallpaper = d.readConfig("Image");
                    break;
                }
            }
            print(wallpaper);
            """
            result = plasma.evaluateScript(script)
            path = str(result).strip()
            if path.startswith("file://"):
                path = path[7:]
            return path
        except Exception:
            return None

    def check_config_changed(self):
        if not os.path.exists(USER_CONFIG_FILE):
            return False
        try:
            mtime = os.path.getmtime(USER_CONFIG_FILE)
            if mtime > self.last_config_mtime:
                self.last_config_mtime = mtime
                config = configparser.ConfigParser()
                config.read(USER_CONFIG_FILE)
                if "General" in config:
                    new_mode = config["General"].get("colorMode", "dark").strip('"')
                    new_flavor = config["General"].get("flavor", "tonal-spot").strip('"')
                    if new_mode != self.mode or new_flavor != self.flavor:
                        self.mode = new_mode
                        self.flavor = new_flavor
                        logging.info(f"Config changed: Mode={self.mode}, Flavor={self.flavor}")
                        return True
            return False
        except Exception as e:
            logging.error(f"Config read error: {e}")
            return False

    def refresh_plasma_theme(self):
        """
        强制刷新 Plasma 配色
        """
        if not os.path.exists(THEME_FILE_MAIN):
            logging.error(f"Main theme file not found: {THEME_FILE_MAIN}")
            return

        try:
            with open(THEME_FILE_MAIN, 'r') as f:
                content = f.read()

            content_alt = content.replace("Name=MaterialYou", f"Name={THEME_NAME_ALT}")

            with open(THEME_FILE_ALT, 'w') as f:
                f.write(content_alt)

            subprocess.run(["plasma-apply-colorscheme", THEME_NAME_ALT],
                           stdout=subprocess.DEVNULL, check=True)

            time.sleep(0.2)

            subprocess.run(["plasma-apply-colorscheme", THEME_NAME_MAIN],
                           stdout=subprocess.DEVNULL, check=True)

            subprocess.run(["qdbus", "org.kde.kded5", "/kded", "reconfigure"],
                           stderr=subprocess.DEVNULL)

            logging.info("Plasma theme refreshed successfully.")

        except Exception as e:
            logging.error(f"Failed to refresh plasma theme: {e}")

    def resolve_wallpaper_path(self, path):
        """
        【核心修复】
        如果路径是目录（KDE 壁纸包），根据当前模式（Light/Dark）解析出具体的图片路径。
        """
        if not os.path.isdir(path):
            return path

        logging.info(f"Detected wallpaper package at: {path}")

        # 1. 确定搜索路径优先级
        search_paths = []

        # 如果当前是暗色模式，优先找 images_dark
        if self.mode == "dark":
            search_paths.append(os.path.join(path, "contents", "images_dark"))

        # 默认找 images
        search_paths.append(os.path.join(path, "contents", "images"))

        # 最后找根目录
        search_paths.append(path)

        # 2. 遍历查找有效图片
        valid_extensions = ('.png', '.jpg', '.jpeg', '.webp', '.jxl', '.svg')

        for p in search_paths:
            if os.path.exists(p) and os.path.isdir(p):
                try:
                    files = os.listdir(p)
                    # 过滤图片
                    images = [f for f in files if f.lower().endswith(valid_extensions)]

                    if images:
                        # 简单策略：排序后取第一个。
                        # kde-material-you-colors 会取“最小”的图片以加快处理速度，
                        # Matugen 性能很好，这里我们取最像主图的（通常分辨率最高的在前面或后面）
                        # 这里为了稳定，我们简单按文件名排序取第一个。
                        images.sort()
                        full_path = os.path.join(p, images[0])
                        logging.info(f"Resolved wallpaper image: {full_path}")
                        return full_path
                except OSError:
                    continue

        # 如果实在找不到，返回原路径让 matugen 报错
        return path

    def run_update(self, raw_wallpaper_path):
        if not raw_wallpaper_path or not os.path.exists(raw_wallpaper_path):
            return

        if not os.path.exists(MATUGEN_CONFIG):
            logging.error("Matugen config not found")
            return

        # 【调用解析函数】
        wallpaper_path = self.resolve_wallpaper_path(raw_wallpaper_path)

        logging.info(f"Running Matugen... Wall: {os.path.basename(wallpaper_path)}")

        try:
            type_arg = f"scheme-{self.flavor}" if not self.flavor.startswith("scheme-") else self.flavor

            # 1. 运行 Matugen
            cmd = [
                MATUGEN_BIN,
                "image",
                wallpaper_path,
                "--config", MATUGEN_CONFIG,
                "--mode", self.mode,
                "--type", type_arg
            ]
            subprocess.run(cmd, check=True)

            # 2. 刷新 Plasma
            self.refresh_plasma_theme()

        except subprocess.CalledProcessError as e:
            logging.error(f"Update failed with exit code {e.returncode}")
        except FileNotFoundError:
            logging.error(f"Matugen binary '{MATUGEN_BIN}' not found.")

def main():
    logging.info(f"Matugen KDE Bridge Started.")
    manager = StateManager()
    os.makedirs(os.path.dirname(USER_CONFIG_FILE), exist_ok=True)

    while True:
        try:
            wallpaper_changed = False
            config_changed = False

            current_wallpaper = manager.get_current_wallpaper()
            if current_wallpaper and current_wallpaper != manager.last_wallpaper:
                # 即使路径还是原来的（比如还是 .../Coast/），但可能内容变了？
                # KDE 的机制是换壁纸才会变路径。
                # 这里简单判断路径变更。
                if os.path.exists(current_wallpaper):
                    logging.info(f"Wallpaper change detected: {current_wallpaper}")
                    manager.last_wallpaper = current_wallpaper
                    wallpaper_changed = True

            if manager.check_config_changed():
                config_changed = True

            if (wallpaper_changed or config_changed) and manager.last_wallpaper:
                time.sleep(0.2)
                manager.run_update(manager.last_wallpaper)

        except KeyboardInterrupt:
            logging.info("Stopping bridge...")
            break
        except Exception as e:
            logging.error(f"Loop error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
