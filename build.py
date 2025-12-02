import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import PyInstaller.__main__

# --- Configuration ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
MATUGEN_DIR = os.path.join(PROJECT_DIR, "matugen")
DIST_DIR = os.path.join(PROJECT_DIR, "dist")

# Debian Package Config
DEB_APP_NAME = "materialyou-autothemer"
DEB_VERSION = "1.0.0"
DEB_ARCH = "amd64"
DEB_MAINTAINER = "Luxingzhi27 <luxingzhi27@example.com>"
DEB_DESCRIPTION = "Material You Theme Generator for Linux Desktop"
DEB_DEPENDS = "libc6, libglib2.0-0"


def clean_build_dirs():
    """Clean up build artifacts"""
    print("🧹 Cleaning up build directories...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)


def build_binaries():
    """Build the two binaries using PyInstaller"""
    print("🚀 Starting Build Process (Dual Binary Mode)...")

    # Ensure dist dir exists
    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    # Determine separator
    sep = ";" if sys.platform.startswith("win") else ":"

    # Prepare Matugen Binary
    matugen_bin_name = "matugen-bin"
    matugen_bin_path = os.path.join(PROJECT_DIR, matugen_bin_name)
    temp_bin_dir = os.path.join(PROJECT_DIR, "temp_bin_for_build")
    add_binary_arg = []

    if os.path.isfile(matugen_bin_path) and os.access(matugen_bin_path, os.X_OK):
        print(f"📦 Found local matugen binary: {matugen_bin_name}, bundling...")
        if os.path.exists(temp_bin_dir):
            shutil.rmtree(temp_bin_dir)
        os.makedirs(temp_bin_dir)
        # Rename to matugen so utils.py finds it in bin/matugen
        shutil.copy(matugen_bin_path, os.path.join(temp_bin_dir, "matugen"))
        add_binary_arg = [
            f"--add-binary={os.path.join(temp_bin_dir, 'matugen')}{sep}bin"
        ]
    else:
        print("⚠️  Local matugen-bin not found. App will rely on system PATH.")

    # Common Arguments
    common_args = [
        "--clean",
        "--onefile",
        f"--add-data={MATUGEN_DIR}{sep}matugen",
        "--paths=.",
        "--hidden-import=backend",
        "--hidden-import=backend.utils",
        "--hidden-import=backend.logger",
        "--hidden-import=backend.bridge",
        "--hidden-import=dbus",
        "--hidden-import=_dbus_bindings",
        "--hidden-import=_dbus_glib_bindings",
    ] + add_binary_arg

    # --- Build 1: GUI ---
    print("\n🔨 [1/2] Building GUI Frontend (MaterialYou-Autothemer)...")
    gui_args = [
        "frontend/gui.py",
        "--name=MaterialYou-Autothemer",
        "--windowed",
        f"--add-data={os.path.join(FRONTEND_DIR, 'ui')}{sep}frontend/ui",
        "--exclude-module=tkinter",
    ] + common_args

    # Use subprocess to isolate PyInstaller runs
    subprocess.run([sys.executable, "-m", "PyInstaller"] + gui_args, check=True)

    # --- Build 2: Service ---
    print("\n🔨 [2/2] Building Backend Service (MaterialYou-Service)...")
    service_args = [
        "backend/bridge.py",
        "--name=MaterialYou-Service",
        "--windowed",
        "--exclude-module=PySide6",
        "--exclude-module=shiboken6",
        "--exclude-module=tkinter",
    ] + common_args

    subprocess.run([sys.executable, "-m", "PyInstaller"] + service_args, check=True)

    # Cleanup temp dir
    if os.path.exists(temp_bin_dir):
        shutil.rmtree(temp_bin_dir)

    print("\n✅ Binaries Built Successfully!")
    print(f"GUI:     {os.path.join(DIST_DIR, 'MaterialYou-Autothemer')}")
    print(f"Service: {os.path.join(DIST_DIR, 'MaterialYou-Service')}")


def build_deb_package():
    """Package the binaries into a .deb file"""
    print("\n📦 Creating Debian Package...")

    deb_build_dir = Path(DIST_DIR) / "deb_package"
    if deb_build_dir.exists():
        shutil.rmtree(deb_build_dir)
    deb_build_dir.mkdir(parents=True)

    # 1. Install Binaries to /opt/materialyou-autothemer
    target_opt = deb_build_dir / "opt" / DEB_APP_NAME
    target_opt.mkdir(parents=True)

    src_gui = Path(DIST_DIR) / "MaterialYou-Autothemer"
    src_svc = Path(DIST_DIR) / "MaterialYou-Service"

    if not src_gui.exists() or not src_svc.exists():
        print("❌ Error: Binaries missing. Run build without --deb first?")
        return

    shutil.copy(src_gui, target_opt / "MaterialYou-Autothemer")
    shutil.copy(src_svc, target_opt / "MaterialYou-Service")

    # 2. Create DEBIAN/control
    debian_dir = deb_build_dir / "DEBIAN"
    debian_dir.mkdir()
    with open(debian_dir / "control", "w") as f:
        f.write(f"Package: {DEB_APP_NAME}\n")
        f.write(f"Version: {DEB_VERSION}\n")
        f.write(f"Section: utils\n")
        f.write(f"Priority: optional\n")
        f.write(f"Architecture: {DEB_ARCH}\n")
        f.write(f"Maintainer: {DEB_MAINTAINER}\n")
        f.write(f"Description: {DEB_DESCRIPTION}\n")
        f.write(f"Depends: {DEB_DEPENDS}\n")

    # 3. Desktop Entry
    apps_dir = deb_build_dir / "usr" / "share" / "applications"
    apps_dir.mkdir(parents=True)
    with open(apps_dir / f"{DEB_APP_NAME}.desktop", "w") as f:
        f.write(
            f"""[Desktop Entry]
Name=Material You Theme
Comment=Customize your desktop colors
Exec=/usr/bin/{DEB_APP_NAME}
Icon=preferences-desktop-color
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;Utility;
"""
        )

    # 4. Systemd Service
    # Points to the Service binary in /opt
    systemd_dir = deb_build_dir / "usr" / "lib" / "systemd" / "user"
    systemd_dir.mkdir(parents=True)
    with open(systemd_dir / f"{DEB_APP_NAME}.service", "w") as f:
        f.write(
            f"""[Unit]
Description=Material You Autothemer Backend Service
After=graphical-session.target

[Service]
Type=simple
Environment="APP_MODE=INSTALLED"
ExecStart=/opt/{DEB_APP_NAME}/MaterialYou-Service
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
"""
        )

    # 5. Wrapper Script
    bin_dir = deb_build_dir / "usr" / "bin"
    bin_dir.mkdir(parents=True)
    wrapper_path = bin_dir / DEB_APP_NAME
    with open(wrapper_path, "w") as f:
        f.write(
            f"""#!/bin/sh
export APP_MODE=INSTALLED
exec /opt/{DEB_APP_NAME}/MaterialYou-Autothemer "$@"
"""
        )
    os.chmod(wrapper_path, 0o755)

    # 6. Postinst Script
    with open(debian_dir / "postinst", "w") as f:
        f.write(
            f"""#!/bin/sh
if [ "$1" = "configure" ]; then
    echo "✅ {DEB_APP_NAME} installed."
    echo "To enable the background service, run:"
    echo "  systemctl --user enable --now {DEB_APP_NAME}"
fi
"""
        )
    os.chmod(debian_dir / "postinst", 0o755)

    # 7. Build .deb
    if not shutil.which("dpkg-deb"):
        print("⚠️  'dpkg-deb' not found. Skipping final .deb generation.")
        print(f"   Package structure created at: {deb_build_dir}")
        return

    deb_filename = f"{DEB_APP_NAME}_{DEB_VERSION}_{DEB_ARCH}.deb"
    subprocess.run(
        ["dpkg-deb", "--build", str(deb_build_dir), str(Path(DIST_DIR) / deb_filename)],
        check=True,
    )
    print(f"\n✅ Debian Package Created: {Path(DIST_DIR) / deb_filename}")


def main():
    parser = argparse.ArgumentParser(description="Build MaterialYou-Autothemer")
    parser.add_argument(
        "--deb", action="store_true", help="Build Debian package (.deb) after binaries"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Clean build directories only"
    )
    args = parser.parse_args()

    if args.clean:
        clean_build_dirs()
        return

    # Always clean before build to avoid artifacts
    clean_build_dirs()

    # Build Binaries
    build_binaries()

    # Build Deb if requested
    if args.deb:
        build_deb_package()


if __name__ == "__main__":
    main()
