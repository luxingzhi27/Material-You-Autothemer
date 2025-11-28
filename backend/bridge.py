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

import utils  # 导入同级 utils.py


class GnomeEngine:
    def __init__(self):
        import gi

        gi.require_version("Gio", "2.0")
        from gi.repository import Gio, GLib

        self.Gio = Gio
        self.loop = GLib.MainLoop()
        self.settings_bg = Gio.Settings.new("org.gnome.desktop.background")
        self.settings_interface = Gio.Settings.new("org.gnome.desktop.interface")

        # 监听配置和壁纸
        conf_file = Gio.File.new_for_path(str(utils.CONFIG_FILE))
        self.monitor = conf_file.monitor_file(Gio.FileMonitorFlags.NONE, None)
        self.monitor.connect("changed", self.on_change)
        self.settings_bg.connect("changed::picture-uri", self.on_change)
        self.settings_bg.connect("changed::picture-uri-dark", self.on_change)

    def on_change(self, *args):
        self.update()

    def update(self):
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
    utils.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if "gnome" in utils.get_desktop_env():
        GnomeEngine().start()
    else:
        KdeEngine().start()
