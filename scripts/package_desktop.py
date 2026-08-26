"""Build platform-native ChemBalance release assets with PyInstaller.

The script is intentionally called on the target operating system by GitHub
Actions.  PyInstaller bundles native executables; it is not a cross-compiler.

Examples:
    python scripts/package_desktop.py --platform windows-x64
    python scripts/package_desktop.py --platform macos-arm64
    python scripts/package_desktop.py --platform linux-x64

Output is written to ``dist/release`` as an archive and a companion SHA-256 file.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DIST_DIRECTORY = PROJECT_ROOT / "dist"
RELEASE_DIRECTORY = DIST_DIRECTORY / "release"
APP_NAME = "ChemBalance"


class PackagingError(RuntimeError):
    """Raised when packaging is requested for an incompatible host platform."""


def run(command: list[str]) -> None:
    """Run a packaging command from the repository root and stop on errors."""
    print("+", " ".join(command))
    subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def sha256(path: Path) -> str:
    """Return a file checksum using bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_checksum(path: Path) -> Path:
    """Create a standard ``sha256sum``-compatible companion checksum file."""
    checksum_path = path.with_name(path.name + ".sha256")
    checksum_path.write_text(f"{sha256(path)}  {path.name}\n", encoding="ascii")
    return checksum_path


def expected_host(platform_key: str) -> tuple[str, str | None]:
    """Return the expected OS and optional CPU architecture for a release target."""
    mapping = {
        "windows-x64": ("Windows", "x86_64"),
        "macos-x64": ("Darwin", "x86_64"),
        "macos-arm64": ("Darwin", "arm64"),
        "linux-x64": ("Linux", "x86_64"),
    }
    return mapping[platform_key]


def verify_host(platform_key: str) -> None:
    """Fail early if a workflow tries to package the wrong native target."""
    expected_system, expected_machine = expected_host(platform_key)
    current_system = platform.system()
    current_machine = platform.machine().lower()
    aliases = {"amd64": "x86_64", "aarch64": "arm64"}
    current_machine = aliases.get(current_machine, current_machine)
    if current_system != expected_system:
        raise PackagingError(
            f"Target '{platform_key}' must be built on {expected_system}, not {current_system}."
        )
    if expected_machine and current_machine != expected_machine:
        raise PackagingError(
            f"Target '{platform_key}' requires {expected_machine}, not {current_machine}."
        )


def clean_previous_outputs() -> None:
    """Remove only generated build artifacts before creating a fresh package."""
    for path in (PROJECT_ROOT / "build", DIST_DIRECTORY, PROJECT_ROOT / f"{APP_NAME}.spec"):
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()
    RELEASE_DIRECTORY.mkdir(parents=True, exist_ok=True)


def build_application() -> Path:
    """Use PyInstaller to create the native application bundle."""
    run([
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        APP_NAME,
        "app.py",
    ])
    app_bundle = DIST_DIRECTORY / (f"{APP_NAME}.app" if platform.system() == "Darwin" else APP_NAME)
    if not app_bundle.exists():
        raise PackagingError(f"Expected bundle '{app_bundle}' was not created.")
    return app_bundle


def zip_bundle(source: Path, archive: Path) -> None:
    """Write a reproducible-ish ZIP archive preserving relative bundle paths."""
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        if source.is_dir():
            for file_path in sorted(source.rglob("*")):
                if file_path.is_file():
                    output.write(file_path, file_path.relative_to(source.parent))
        else:
            output.write(source, source.name)


def tar_bundle(source: Path, archive: Path) -> None:
    """Write a gzipped tar archive for Linux distribution."""
    with tarfile.open(archive, "w:gz") as output:
        output.add(source, arcname=source.name, recursive=True)


def create_archive(platform_key: str, bundle: Path) -> Path:
    """Create the distribution archive appropriate for each platform."""
    if platform_key == "windows-x64":
        archive = RELEASE_DIRECTORY / "ChemBalance-windows-x64.zip"
        zip_bundle(bundle, archive)
    elif platform_key.startswith("macos-"):
        archive = RELEASE_DIRECTORY / f"ChemBalance-{platform_key}.zip"
        zip_bundle(bundle, archive)
    else:
        archive = RELEASE_DIRECTORY / "ChemBalance-linux-x64.tar.gz"
        tar_bundle(bundle, archive)
    return archive


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a native ChemBalance release archive.")
    parser.add_argument(
        "--platform",
        required=True,
        choices=("windows-x64", "macos-x64", "macos-arm64", "linux-x64"),
        help="Native platform release target.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    verify_host(arguments.platform)
    clean_previous_outputs()
    bundle = build_application()
    archive = create_archive(arguments.platform, bundle)
    checksum = write_checksum(archive)
    print(f"Created archive: {archive}")
    print(f"Created checksum: {checksum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
