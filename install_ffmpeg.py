"""
Automated FFmpeg installer for Transcribair.
Downloads and installs FFmpeg automatically on Windows.
"""
import os
import sys
import zipfile
import shutil
import urllib.request
from pathlib import Path
import platform


class FFmpegInstaller:
    """Handles FFmpeg installation across platforms."""

    # FFmpeg download URLs
    FFMPEG_URLS = {
        'Windows': 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
        'Linux': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
        'Darwin': 'https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip'  # macOS
    }

    def __init__(self, auto_install=False):
        self.system = platform.system()
        self.install_dir = Path.home() / ".transcribair" / "ffmpeg"
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.auto_install = auto_install

    def is_installed(self) -> bool:
        """Check if FFmpeg is already available."""
        # Check in PATH
        if shutil.which("ffmpeg"):
            print("✓ FFmpeg already installed in system PATH")
            return True

        # Check in our install directory
        ffmpeg_exe = self.install_dir / ("ffmpeg.exe" if self.system == "Windows" else "ffmpeg")
        if ffmpeg_exe.exists():
            print(f"✓ FFmpeg found in {self.install_dir}")
            self._add_to_path()
            return True

        return False

    def install(self):
        """Download and install FFmpeg."""
        if self.is_installed():
            return True

        print(f"\nInstalling FFmpeg for {self.system}...")
        print("-" * 50)

        if self.system not in self.FFMPEG_URLS:
            print(f"✗ Automatic installation not supported for {self.system}")
            print("  Please install FFmpeg manually:")
            print("  https://ffmpeg.org/download.html")
            return False

        try:
            url = self.FFMPEG_URLS[self.system]
            download_path = self.install_dir / "ffmpeg_download.zip"

            # Download
            print(f"Downloading FFmpeg from {url[:50]}...")
            self._download_with_progress(url, download_path)

            # Extract
            print("\nExtracting FFmpeg...")
            self._extract_ffmpeg(download_path)

            # Cleanup
            download_path.unlink()

            # Verify
            if self._verify_installation():
                print("\n✓ FFmpeg installed successfully!")
                self._add_to_path()
                return True
            else:
                print("\n✗ FFmpeg installation verification failed")
                return False

        except Exception as e:
            print(f"\n✗ Installation failed: {str(e)}")
            return False

    def _download_with_progress(self, url: str, output_path: Path):
        """Download file with progress bar."""
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '=' * filled + '-' * (bar_length - filled)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f'\r[{bar}] {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)', end='')

        urllib.request.urlretrieve(url, output_path, progress_hook)
        print()  # New line after progress bar

    def _extract_ffmpeg(self, archive_path: Path):
        """Extract FFmpeg from downloaded archive."""
        if self.system == "Windows":
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Extract all files
                temp_extract = self.install_dir / "temp"
                zip_ref.extractall(temp_extract)

                # Find and move ffmpeg executables
                for root, dirs, files in os.walk(temp_extract):
                    for file in files:
                        if file in ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']:
                            src = Path(root) / file
                            dst = self.install_dir / file
                            shutil.move(str(src), str(dst))
                            print(f"  Extracted: {file}")

                # Cleanup temp directory
                shutil.rmtree(temp_extract)

        elif self.system == "Linux":
            import tarfile
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                temp_extract = self.install_dir / "temp"
                tar_ref.extractall(temp_extract)

                # Find and move ffmpeg executables
                for root, dirs, files in os.walk(temp_extract):
                    for file in files:
                        if file in ['ffmpeg', 'ffprobe']:
                            src = Path(root) / file
                            dst = self.install_dir / file
                            shutil.move(str(src), str(dst))
                            # Make executable
                            os.chmod(dst, 0o755)
                            print(f"  Extracted: {file}")

                shutil.rmtree(temp_extract)

        elif self.system == "Darwin":  # macOS
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(self.install_dir)
                # Make executable
                ffmpeg_path = self.install_dir / "ffmpeg"
                os.chmod(ffmpeg_path, 0o755)
                print("  Extracted: ffmpeg")

    def _verify_installation(self) -> bool:
        """Verify FFmpeg was installed correctly."""
        ffmpeg_exe = self.install_dir / ("ffmpeg.exe" if self.system == "Windows" else "ffmpeg")
        return ffmpeg_exe.exists()

    def _add_to_path(self):
        """Add FFmpeg directory to PATH for current session."""
        ffmpeg_dir = str(self.install_dir)
        if ffmpeg_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
            print(f"  Added {ffmpeg_dir} to PATH for this session")

    def get_ffmpeg_path(self) -> str:
        """Get the path to FFmpeg binary."""
        return str(self.install_dir)


def main():
    """Main installation process."""
    # Check for --auto flag
    auto_install = '--auto' in sys.argv or '-y' in sys.argv

    print("=" * 50)
    print("Transribair - FFmpeg Installer")
    print("=" * 50)

    installer = FFmpegInstaller(auto_install=auto_install)

    if installer.is_installed():
        print("\nFFmpeg is already available. No installation needed.")
        return 0

    print("\nTransribair requires FFmpeg for audio processing.")

    if auto_install:
        print("Auto-install mode enabled. Installing FFmpeg...")
        response = 'y'
    else:
        response = input("Install FFmpeg automatically? [Y/n]: ").strip().lower()

    if response in ['', 'y', 'yes']:
        if installer.install():
            print("\nInstallation complete! You can now run Transribair.")
            return 0
        else:
            print("\nInstallation failed. Please install FFmpeg manually:")
            print("https://ffmpeg.org/download.html")
            return 1
    else:
        print("\nSkipping FFmpeg installation.")
        print("Please install FFmpeg manually before using Transribair.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
