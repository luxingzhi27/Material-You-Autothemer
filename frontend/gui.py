#!/usr/bin/env python3
import os
import signal
import sys
from pathlib import Path

# --- Path setup ---
if not getattr(sys, "frozen", False):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

try:
    from backend import utils
    from backend.bridge import GnomeEngine, KdeEngine
    from backend.logger import log
except ImportError:
    print("Error: Could not import backend modules.")
    sys.exit(1)


def run_gui():
    """
    Run the GUI application.
    """
    # Lazy import PySide6 to avoid overhead in service mode
    try:
        from PySide6.QtCore import Property, QObject, QThread, QUrl, Signal, Slot
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtWidgets import QApplication
    except ImportError:
        log.error("PySide6 not found. Cannot start GUI.")
        sys.exit(1)

    import configparser
    import json

    # Ensure configuration files exist in ~/.config
    utils.init_resources()

    APP_NAME = "MaterialYou-Autothemer"
    MATUGEN_CONFIG = utils.MATUGEN_CONFIG_PATH
    CONFIG_FILE = utils.CONFIG_FILE

    class PreviewWorker(QThread):
        resultReady = Signal(str)

        def __init__(self, wallpaper, mode, flavor):
            super().__init__()
            self.args = (wallpaper, mode, flavor)

        def run(self):
            # 调用 utils 中的通用方法
            json_str = utils.run_matugen(
                self.args[0],
                self.args[1],
                self.args[2],
                dry_run=True,
                config_path=MATUGEN_CONFIG,
            )
            self.resultReady.emit(json_str if json_str else "{}")

    class Backend(QObject):
        def __init__(self, parent=None):
            super().__init__(parent)  # 防止被 GC 回收
            self._color_mode = "dark"
            self._flavor = "tonal-spot"
            self._preview_colors = []
            self._wallpaper_folder = str(Path.home() / "Pictures")
            self._wallpaper_list = []
            self._current_wallpaper = ""
            self._preview_theme = {}

            self.worker = None
            self.load_config()

            # Initialize wallpaper
            self.scan_wallpapers()
            sys_wall = utils.get_current_wallpaper(self._color_mode)
            if sys_wall:
                self._current_wallpaper = sys_wall

            self.update_preview()

        colorModeChanged = Signal(str)
        flavorChanged = Signal(str)
        previewColorsChanged = Signal(list)
        wallpaperFolderChanged = Signal(str)
        wallpaperListChanged = Signal(list)
        currentWallpaperChanged = Signal(str)
        previewThemeChanged = Signal(dict)

        @Property(str, notify=colorModeChanged)
        def colorMode(self):
            return self._color_mode

        @colorMode.setter
        def colorMode(self, val):
            if self._color_mode != val:
                self._color_mode = val
                self.colorModeChanged.emit(val)
                self.update_preview()

        @Property(str, notify=flavorChanged)
        def flavor(self):
            return self._flavor

        @flavor.setter
        def flavor(self, val):
            if self._flavor != val:
                self._flavor = val
                self.flavorChanged.emit(val)
                self.update_preview()

        @Property(list, notify=previewColorsChanged)
        def previewColors(self):
            return self._preview_colors

        @Property(str, notify=wallpaperFolderChanged)
        def wallpaperFolder(self):
            return self._wallpaper_folder

        @wallpaperFolder.setter
        def wallpaperFolder(self, val):
            path = QUrl(val).toLocalFile() if val.startswith("file://") else val
            if self._wallpaper_folder != path:
                self._wallpaper_folder = path
                self.wallpaperFolderChanged.emit(path)
                self.scan_wallpapers()

        @Property(list, notify=wallpaperListChanged)
        def wallpaperList(self):
            return self._wallpaper_list

        @Property(str, notify=currentWallpaperChanged)
        def currentWallpaper(self):
            return self._current_wallpaper

        @currentWallpaper.setter
        def currentWallpaper(self, val):
            path = QUrl(val).toLocalFile() if val.startswith("file://") else val
            if self._current_wallpaper != path:
                self._current_wallpaper = path
                self.currentWallpaperChanged.emit(path)
                self.update_preview()

        @Property(dict, notify=previewThemeChanged)
        def previewTheme(self):
            return self._preview_theme

        def scan_wallpapers(self):
            self._wallpaper_list = []
            if os.path.isdir(self._wallpaper_folder):
                valid_exts = {".png", ".jpg", ".jpeg", ".webp", ".jxl"}
                try:
                    for f in os.listdir(self._wallpaper_folder):
                        if os.path.splitext(f)[1].lower() in valid_exts:
                            self._wallpaper_list.append(
                                os.path.join(self._wallpaper_folder, f)
                            )
                    self._wallpaper_list.sort()
                except Exception as e:
                    log.error(f"Error scanning wallpapers: {e}")
            self.wallpaperListChanged.emit(self._wallpaper_list)

        def get_wallpaper(self):
            if self._current_wallpaper and os.path.exists(self._current_wallpaper):
                return self._current_wallpaper
            # 优先读取缓存
            cached = utils.get_cached_wallpaper()
            if cached:
                return cached
            return utils.get_current_wallpaper(self._color_mode)

        @Slot()
        def update_preview(self):
            wallpaper = self.get_wallpaper()
            if not wallpaper:
                log.warning("No wallpaper found for preview.")
                return

            log.info(
                f"Updating preview: mode={self._color_mode}, flavor={self._flavor}"
            )

            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.worker.wait()

            self.worker = PreviewWorker(wallpaper, self._color_mode, self._flavor)
            self.worker.resultReady.connect(self.handle_result)
            self.worker.start()

        def handle_result(self, json_str):
            try:
                data = json.loads(json_str)
                c = data.get("colors", data)
                if not c:
                    return

                def get_hex(color_key):
                    val = c.get(color_key)
                    if not val:
                        return "#000000"
                    if isinstance(val, dict):
                        return val.get(self._color_mode, val.get("default", "#000000"))
                    if isinstance(val, str):
                        return val
                    return "#000000"

                preview_list = [
                    {"name": "Primary", "color": get_hex("primary")},
                    {"name": "Secondary", "color": get_hex("secondary")},
                    {"name": "Tertiary", "color": get_hex("tertiary")},
                    {"name": "Surface", "color": get_hex("surface")},
                    {"name": "Error", "color": get_hex("error")},
                ]
                self._preview_colors = preview_list
                self.previewColorsChanged.emit(preview_list)

                # Extract full theme for UI
                theme_colors = {}
                keys = [
                    "primary",
                    "on_primary",
                    "primary_container",
                    "on_primary_container",
                    "secondary",
                    "on_secondary",
                    "secondary_container",
                    "on_secondary_container",
                    "tertiary",
                    "on_tertiary",
                    "tertiary_container",
                    "on_tertiary_container",
                    "error",
                    "on_error",
                    "error_container",
                    "on_error_container",
                    "background",
                    "on_background",
                    "surface",
                    "on_surface",
                    "surface_variant",
                    "on_surface_variant",
                    "outline",
                    "outline_variant",
                    "inverse_surface",
                    "inverse_on_surface",
                    "inverse_primary",
                ]
                for k in keys:
                    theme_colors[k] = get_hex(k)
                self._preview_theme = theme_colors
                self.previewThemeChanged.emit(theme_colors)

            except Exception as e:
                log.error(f"Preview Logic Error: {e}")

        @Slot()
        def apply_theme(self):
            try:
                utils.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                config = configparser.ConfigParser()
                config["General"] = {
                    "colorMode": self._color_mode,
                    "flavor": self._flavor,
                    "wallpaperFolder": self._wallpaper_folder,
                }
                with open(CONFIG_FILE, "w") as f:
                    config.write(f)
                log.info("Configuration saved.")

                # Apply wallpaper if selected
                if self._current_wallpaper:
                    self.set_system_wallpaper(self._current_wallpaper)

            except Exception as e:
                log.error(f"Failed to apply theme: {e}")

        def set_system_wallpaper(self, path):
            try:
                if utils.is_gnome_session():
                    cmd = f"gsettings set org.gnome.desktop.background picture-uri 'file://{path}'"
                    os.system(cmd)
                    cmd = f"gsettings set org.gnome.desktop.background picture-uri-dark 'file://{path}'"
                    os.system(cmd)
                elif utils.is_kde_session():
                    # Try plasma-apply-wallpaperimage
                    cmd = f"plasma-apply-wallpaperimage '{path}'"
                    os.system(cmd)
            except Exception as e:
                log.error(f"Failed to set wallpaper: {e}")

        def load_config(self):
            self._color_mode, self._flavor, self._wallpaper_folder = utils.read_config()

    # --- Start GUI ---
    app = QApplication(sys.argv)
    app.setOrganizationName("Luxingzhi27")
    app.setApplicationName("Matugen Controller")

    backend = Backend(app)

    # --- Auto-start Background Service ---
    # 确保后台服务已安装并运行
    utils.ensure_service_running()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("pythonBackend", backend)

    # 适配 QML 路径 (源码 vs 打包)
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
        qml_file = base_path / "frontend" / "ui" / "main.qml"
    else:
        qml_file = Path(os.path.dirname(__file__)) / "ui" / "main.qml"

    engine.load(QUrl.fromLocalFile(str(qml_file)))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
