"""
Build script for creating Transcribair executable.
Handles PyInstaller build with proper configuration and FFmpeg bundling.
"""
import subprocess
import sys
from pathlib import Path
import shutil
import os

from install_ffmpeg import FFmpegInstaller


def check_requirements():
    """Check if required tools are installed."""
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("✗ PyInstaller not found")
        print("  Install with: pip install pyinstaller")
        return False

    return True


def install_ffmpeg():
    """Install FFmpeg if not already available."""
    installer = FFmpegInstaller()

    if installer.is_installed():
        return installer.get_ffmpeg_path()

    print("\nFFmpeg is required for building Transcribair.")
    response = input("Install FFmpeg automatically? [Y/n]: ").strip().lower()

    if response in ['', 'y', 'yes']:
        if installer.install():
            return installer.get_ffmpeg_path()
        else:
            print("\n✗ FFmpeg installation failed!")
            return None
    else:
        print("\n✗ Build requires FFmpeg to be installed.")
        return None


def build_executable(ffmpeg_path: str):
    """Build the executable using PyInstaller."""
    print("\nBuilding Transcribair executable...")
    print("-" * 50)

    # Clean previous builds
    dist_dir = Path("dist")
    build_dir = Path("build")

    if dist_dir.exists():
        print("Cleaning previous dist directory...")
        shutil.rmtree(dist_dir)

    if build_dir.exists():
        print("Cleaning previous build directory...")
        shutil.rmtree(build_dir)

    # Update spec file to include FFmpeg binaries
    update_spec_with_ffmpeg(ffmpeg_path)

    # Run PyInstaller
    print("\nRunning PyInstaller...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "build.spec", "--clean"],
        capture_output=False
    )

    if result.returncode == 0:
        print("\n" + "=" * 50)
        print("✓ Build successful!")
        print("=" * 50)
        print(f"\nExecutable location: {dist_dir / 'Transcribair.exe'}")
        print("\nNote: FFmpeg is bundled in the executable.")
        print("      First run will download the selected Whisper model.")
        print("      Models are cached in: %USERPROFILE%\\.transcribair\\models")
    else:
        print("\n✗ Build failed!")
        return False

    return True


def update_spec_with_ffmpeg(ffmpeg_path: str):
    """Update build.spec to include FFmpeg binaries."""
    spec_file = Path("build.spec")

    # Find FFmpeg executables
    ffmpeg_dir = Path(ffmpeg_path)
    ffmpeg_files = []

    for exe in ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']:
        exe_path = ffmpeg_dir / exe
        if exe_path.exists():
            ffmpeg_files.append((str(exe_path), 'ffmpeg'))

    if not ffmpeg_files:
        print("⚠ Warning: No FFmpeg executables found to bundle")
        return

    # Read current spec
    with open(spec_file, 'r') as f:
        spec_content = f.read()

    # Update binaries section
    binaries_str = str(ffmpeg_files).replace("'", '"')
    spec_content = spec_content.replace(
        "binaries=[],",
        f"binaries={binaries_str},"
    )

    # Write updated spec
    with open(spec_file, 'w') as f:
        f.write(spec_content)

    print(f"✓ Bundling {len(ffmpeg_files)} FFmpeg executables")


def main():
    """Main build process."""
    print("Transcribair Build Script")
    print("=" * 50)

    if not check_requirements():
        print("\nPlease install missing requirements and try again.")
        sys.exit(1)

    # Install/locate FFmpeg
    ffmpeg_path = install_ffmpeg()
    if not ffmpeg_path:
        print("\nBuild cancelled - FFmpeg is required.")
        sys.exit(1)

    # Build executable with bundled FFmpeg
    if build_executable(ffmpeg_path):
        print("\nBuild complete!")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
