#!/usr/bin/env python3
import configparser
import os
import sys
import time

try:
    from backend.logger import log
except ImportError:
    try:
        import logger

        log = logger.log
    except ImportError:
        import logging

        log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

try:
    from backend import utils
except ImportError:
    import utils


class GnomeEngine:
    def __init__(self):
        import gi

        gi.require_version("Gio", "2.0")
        from gi.repository import Gio, GLib

        self.Gio = Gio
        self.loop = GLib.MainLoop()
        self.settings_bg = Gio.Settings.new("org.gnome.desktop.background")
        self.settings_interface = Gio.Settings.new("org.gnome.desktop.interface")
        self.updating_ui = False  # 防止 UI 刷新触发循环更新

        # 1. 监听配置文件变化 -> 触发 Matugen
        conf_file = Gio.File.new_for_path(str(utils.CONFIG_FILE))
        self.monitor = conf_file.monitor_file(Gio.FileMonitorFlags.NONE, None)
        self.monitor.connect("changed", self.on_config_changed)

        # 2. 监听系统设置变化 -> 更新配置文件
        self.settings_bg.connect("changed::picture-uri", self.on_system_changed)
        self.settings_interface.connect("changed::color-scheme", self.on_system_changed)

    def on_system_changed(self, settings, key):
        """系统设置变化时，同步状态到配置文件"""
        if self.updating_ui:
            return

        log.info(f"System setting changed: {key}")

        # 获取当前系统颜色模式
        scheme = self.settings_interface.get_string("color-scheme")
        mode = "dark" if "dark" in scheme else "light"

        try:
            # 读取现有配置
            config = configparser.ConfigParser()
            config.read(utils.CONFIG_FILE)

            if not config.has_section("General"):
                config.add_section("General")

            # 强制更新配置文件 (即使值相同，写入操作也会更新 mtime，从而触发 on_config_changed)
            # 注意：ConfigParser 默认行为可能不会写入未变更的值，但 open('w') 会刷新文件
            config["General"]["colorMode"] = mode

            # 确保目录存在
            utils.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

            with open(utils.CONFIG_FILE, "w") as f:
                config.write(f)

        except Exception as e:
            log.error(f"Failed to sync system changes to config: {e}")

    def on_config_changed(self, file, other_file, event_type):
        """配置文件变化时，运行 Matugen"""
        # 过滤事件，避免重复触发 (CHANGES_DONE_HINT 通常是写入完成)
        if event_type == self.Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            self.run_matugen_process()

    def run_matugen_process(self):
        mode, flavor, _ = utils.read_config()
        wallpaper = utils.get_current_wallpaper(mode)

        if wallpaper:
            utils.save_state(wallpaper)  # 缓存给前端用
            if utils.run_matugen(wallpaper, mode, flavor):
                self.refresh_ui(mode)

    def refresh_ui(self, mode):
        """
        使用优化后的简洁逻辑刷新 GNOME UI
        """
        self.updating_ui = True  # 标记开始刷新，忽略系统信号
        try:
            # 1. 计算主题名称
            gtk_theme = "adw-gtk3" if mode == "light" else f"adw-gtk3-{mode}"
            color_scheme = f"prefer-{mode}"
            opposite = "prefer-light" if mode == "dark" else "prefer-dark"

            # 2. GTK Theme (仅在不同时设置)
            if self.settings_interface.get_string("gtk-theme") != gtk_theme:
                self.settings_interface.set_string("gtk-theme", gtk_theme)

            # 3. 强制刷新 Color Scheme (跳变)
            self.settings_interface.set_string("color-scheme", opposite)
            # 这一步切回目标值，触发系统重绘
            self.settings_interface.set_string("color-scheme", color_scheme)

            log.info(f"GNOME UI refreshed to {mode}")
        finally:
            # 稍微延迟释放锁，防止信号延迟到达 (可选，这里直接释放通常也行)
            self.updating_ui = False

    def start(self):
        log.info("🚀 GNOME Engine Started")
        self.update()
        self.loop.run()


class KdeEngine:
    def __init__(self):
        self.last_wall = None
        self.last_mtime = 0

    def start(self):
        log.info("🚀 KDE Engine Started")
        while True:
            try:
                mode, flavor, _ = utils.read_config()
                # 检查配置变化
                config_changed = False
                if os.path.exists(utils.CONFIG_FILE):
                    mtime = os.path.getmtime(utils.CONFIG_FILE)
                    if mtime > self.last_mtime:
                        self.last_mtime = mtime
                        config_changed = True

                # 检查壁纸变化
                wall = utils.get_current_wallpaper(mode)

                if wall and (wall != self.last_wall or config_changed):
                    time.sleep(0.5)
                    wall = utils.get_current_wallpaper(mode)  # 再确认一次
                    if wall:
                        utils.save_state(wall)
                        if utils.run_matugen(wall, mode, flavor):
                            self.refresh_ui()
                            self.last_wall = wall
            except Exception as e:
                log.error(f"Loop error: {e}")
            time.sleep(2.0)

    def refresh_ui(self):
        import subprocess

        try:
            subprocess.run(
                ["plasma-apply-colorscheme", "MaterialYouAlt"],
                stdout=subprocess.DEVNULL,
            )
            time.sleep(0.5)
            subprocess.run(
                ["plasma-apply-colorscheme", "MaterialYou"], stdout=subprocess.DEVNULL
            )
            log.info("KDE UI refreshed")
        except Exception as e:
            log.error(f"Failed to refresh KDE UI: {e}")


if __name__ == "__main__":
    # 确保配置资源存在 (Matugen config 等)
    utils.init_resources()

    # 尝试获取锁，确保只有一个服务实例运行
    if not utils.acquire_lock():
        log.error("Service is already running (Lock file occupied). Exiting.")
        sys.exit(0)

    utils.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    log.info("Starting Material You Autothemer Backend Service...")
    if "gnome" in utils.get_desktop_env():
        GnomeEngine().start()
    else:
        KdeEngine().start()
