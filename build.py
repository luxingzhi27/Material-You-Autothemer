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

# Package Config
APP_NAME = "materialyou-autothemer"
VERSION = "1.0.0"
MAINTAINER = "Luxingzhi27 <luxingzhi27@example.com>"
DESCRIPTION = "Material You Theme Generator for Linux Desktop"

# Debian Specific
DEB_ARCH = "amd64"
DEB_DEPENDS = "libc6, libglib2.0-0"

# RPM Specific
RPM_ARCH = "x86_64"


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
    target_opt = deb_build_dir / "opt" / APP_NAME
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
        f.write(f"Package: {APP_NAME}\n")
        f.write(f"Version: {VERSION}\n")
        f.write(f"Section: utils\n")
        f.write(f"Priority: optional\n")
        f.write(f"Architecture: {DEB_ARCH}\n")
        f.write(f"Maintainer: {MAINTAINER}\n")
        f.write(f"Description: {DESCRIPTION}\n")
        f.write(f"Depends: {DEB_DEPENDS}\n")

    # 3. Desktop Entry
    apps_dir = deb_build_dir / "usr" / "share" / "applications"
    apps_dir.mkdir(parents=True)
    with open(apps_dir / f"{APP_NAME}.desktop", "w") as f:
        f.write(
            f"""[Desktop Entry]
Name=Material You Theme
Comment=Customize your desktop colors
Exec=/usr/bin/{APP_NAME}
Icon=preferences-desktop-color
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;Utility;
"""
        )

    # 4. Systemd Service
    systemd_dir = deb_build_dir / "usr" / "lib" / "systemd" / "user"
    systemd_dir.mkdir(parents=True)
    with open(systemd_dir / f"{APP_NAME}.service", "w") as f:
        f.write(
            f"""[Unit]
Description=Material You Autothemer Backend Service
After=graphical-session.target

[Service]
Type=simple
Environment="APP_MODE=INSTALLED"
ExecStart=/opt/{APP_NAME}/MaterialYou-Service
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
"""
        )

    # 5. Wrapper Script
    bin_dir = deb_build_dir / "usr" / "bin"
    bin_dir.mkdir(parents=True)
    wrapper_path = bin_dir / APP_NAME
    with open(wrapper_path, "w") as f:
        f.write(
            f"""#!/bin/sh
export APP_MODE=INSTALLED
exec /opt/{APP_NAME}/MaterialYou-Autothemer "$@"
"""
        )
    os.chmod(wrapper_path, 0o755)

    # 6. Postinst Script
    with open(debian_dir / "postinst", "w") as f:
        f.write(
            f"""#!/bin/sh
if [ "$1" = "configure" ]; then
    echo "✅ {APP_NAME} installed."
    echo "To enable the background service, run:"
    echo "  systemctl --user enable --now {APP_NAME}"
fi
"""
        )
    os.chmod(debian_dir / "postinst", 0o755)

    # 7. Build .deb
    if not shutil.which("dpkg-deb"):
        print("⚠️  'dpkg-deb' not found. Skipping final .deb generation.")
        print(f"   Package structure created at: {deb_build_dir}")
        return

    deb_filename = f"{APP_NAME}_{VERSION}_{DEB_ARCH}.deb"
    subprocess.run(
        ["dpkg-deb", "--build", str(deb_build_dir), str(Path(DIST_DIR) / deb_filename)],
        check=True,
    )
    print(f"\n✅ Debian Package Created: {Path(DIST_DIR) / deb_filename}")


def build_rpm_package():
    """Package the binaries into an .rpm file"""
    print("\n📦 Creating RPM Package...")

    if not shutil.which("rpmbuild"):
        print("❌ Error: 'rpmbuild' not found. Please install rpm-build/rpm-tools.")
        return

    rpm_root = Path(DIST_DIR) / "rpm_build"
    if rpm_root.exists():
        shutil.rmtree(rpm_root)
    rpm_root.mkdir(parents=True)

    # Initialize local RPM database to avoid /var/lib/rpm errors on non-RPM systems
    db_path = rpm_root / "rpmdb"
    db_path.mkdir()
    try:
        subprocess.run(
            ["rpm", "--initdb", "--dbpath", str(db_path.absolute())], check=True
        )
    except Exception as e:
        print(f"⚠️  Warning: Failed to init local rpmdb: {e}")

    # RPM Directory Structure
    for d in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
        (rpm_root / d).mkdir()

    # 1. Prepare Sources (binaries and support files)
    # We create a tarball of the content that needs to go into the RPM
    # The structure inside the tarball should facilitate installation in %install
    src_gui = Path(DIST_DIR) / "MaterialYou-Autothemer"
    src_svc = Path(DIST_DIR) / "MaterialYou-Service"

    if not src_gui.exists() or not src_svc.exists():
        print("❌ Error: Binaries missing. Run build without --rpm first?")
        return

    # Create a staging dir for the tarball
    staging_dir = rpm_root / f"{APP_NAME}-{VERSION}"
    staging_dir.mkdir()
    shutil.copy(src_gui, staging_dir / "MaterialYou-Autothemer")
    shutil.copy(src_svc, staging_dir / "MaterialYou-Service")

    # Create Wrapper Script
    with open(staging_dir / f"{APP_NAME}.sh", "w") as f:
        f.write(
            f"""#!/bin/sh
export APP_MODE=INSTALLED
exec /opt/{APP_NAME}/MaterialYou-Autothemer "$@"
"""
        )
    os.chmod(staging_dir / f"{APP_NAME}.sh", 0o755)

    # Create Desktop File
    with open(staging_dir / f"{APP_NAME}.desktop", "w") as f:
        f.write(
            f"""[Desktop Entry]
Name=Material You Theme
Comment=Customize your desktop colors
Exec=/usr/bin/{APP_NAME}
Icon=preferences-desktop-color
Terminal=false
Type=Application
Categories=Settings;DesktopSettings;Utility;
"""
        )

    # Create Systemd Unit
    with open(staging_dir / f"{APP_NAME}.service", "w") as f:
        f.write(
            f"""[Unit]
Description=Material You Autothemer Backend Service
After=graphical-session.target

[Service]
Type=simple
Environment="APP_MODE=INSTALLED"
ExecStart=/opt/{APP_NAME}/MaterialYou-Service
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=default.target
"""
        )

    # Create tarball
    tar_name = f"{APP_NAME}-{VERSION}.tar.gz"
    subprocess.run(
        [
            "tar",
            "-czf",
            str(rpm_root / "SOURCES" / tar_name),
            "-C",
            str(rpm_root),
            f"{APP_NAME}-{VERSION}",
        ],
        check=True,
    )

    # 2. Create SPEC file
    spec_content = f"""
%global debug_package %{{nil}}

Name:           {APP_NAME}
Version:        {VERSION}
Release:        1
Summary:        {DESCRIPTION}
License:        MIT
URL:            https://github.com/Luxingzhi27/Material-You-Autothemer
Source0:        %{{name}}-%{{version}}.tar.gz

Requires:       glib2
BuildArch:      x86_64

%description
{DESCRIPTION}

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/opt/%{{name}}
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/lib/systemd/user

install -m 755 MaterialYou-Autothemer $RPM_BUILD_ROOT/opt/%{{name}}/
install -m 755 MaterialYou-Service $RPM_BUILD_ROOT/opt/%{{name}}/
install -m 755 %{{name}}.sh $RPM_BUILD_ROOT/usr/bin/%{{name}}
install -m 644 %{{name}}.desktop $RPM_BUILD_ROOT/usr/share/applications/
install -m 644 %{{name}}.service $RPM_BUILD_ROOT/usr/lib/systemd/user/

%files
/opt/%{{name}}/MaterialYou-Autothemer
/opt/%{{name}}/MaterialYou-Service
/usr/bin/%{{name}}
/usr/share/applications/%{{name}}.desktop
/usr/lib/systemd/user/%{{name}}.service

%post
echo "✅ {APP_NAME} installed."
echo "To enable the background service, run:"
echo "  systemctl --user enable --now {APP_NAME}"

%changelog
* Fri Nov 29 2024 {MAINTAINER} - 1.0.0-1
- Initial release
"""

    spec_path = rpm_root / "SPECS" / f"{APP_NAME}.spec"
    with open(spec_path, "w") as f:
        f.write(spec_content)

    # 3. Build RPM
    print("🔨 Running rpmbuild...")
    # define _topdir to point to our local directory
    cmd = [
        "rpmbuild",
        "--define",
        f"_topdir {rpm_root.absolute()}",
        "--define",
        f"_dbpath {db_path.absolute()}",
        "--nodeps",
        "-bb",
        str(spec_path),
    ]
    subprocess.run(cmd, check=True)

    # 4. Copy artifact
    built_rpm = list((rpm_root / "RPMS" / "x86_64").glob("*.rpm"))[0]
    final_rpm = Path(DIST_DIR) / built_rpm.name
    shutil.copy(built_rpm, final_rpm)
    print(f"\n✅ RPM Package Created: {final_rpm}")


def main():
    parser = argparse.ArgumentParser(description="Build MaterialYou-Autothemer")
    parser.add_argument(
        "--deb", action="store_true", help="Build Debian package (.deb) after binaries"
    )
    parser.add_argument(
        "--rpm", action="store_true", help="Build RPM package (.rpm) after binaries"
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

    # Build RPM if requested
    if args.rpm:
        build_rpm_package()


if __name__ == "__main__":
    main()
