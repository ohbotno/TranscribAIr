"""
TranscribAIr
Main entry point for the application.
"""
import sys
import os
from pathlib import Path
import shutil

# Python 3.13 compatibility fix - must be imported before pydub
import python313_fix

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui import MainWindow


def setup_ffmpeg():
    """Set up FFmpeg for the application."""
    # Set up FFmpeg path for PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        application_path = Path(sys._MEIPASS)

        # Add FFmpeg to PATH if bundled
        ffmpeg_path = application_path / "ffmpeg"
        if ffmpeg_path.exists():
            os.environ["PATH"] = str(ffmpeg_path) + os.pathsep + os.environ["PATH"]
            return True

    # Check if FFmpeg is available
    if shutil.which("ffmpeg"):
        return True

    # Check in our install directory
    install_dir = Path.home() / ".transcribair" / "ffmpeg"
    ffmpeg_exe = install_dir / ("ffmpeg.exe" if os.name == 'nt' else "ffmpeg")

    if ffmpeg_exe.exists():
        os.environ["PATH"] = str(install_dir) + os.pathsep + os.environ.get("PATH", "")
        return True

    # FFmpeg not found - try to install
    print("FFmpeg not found. Installing...")
    try:
        from install_ffmpeg import FFmpegInstaller
        installer = FFmpegInstaller(auto_install=True)
        if installer.install():
            return True
    except Exception as e:
        print(f"Failed to install FFmpeg: {e}")

    return False


def main():
    """Main application entry point."""
    # Set up FFmpeg
    if not setup_ffmpeg():
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "FFmpeg Required",
            "FFmpeg is required but could not be installed automatically.\n\n"
            "Please install FFmpeg manually:\n"
            "https://ffmpeg.org/download.html\n\n"
            "Or run: python install_ffmpeg.py"
        )
        sys.exit(1)

    # Create and run app
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
