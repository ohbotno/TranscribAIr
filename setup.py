"""
Setup script for Transcribair.
Creates virtual environment and installs all dependencies.
"""
import subprocess
import sys
import os
from pathlib import Path
import platform


def run_command(cmd, description, check=True):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if check and result.returncode != 0:
        print(f"✗ Failed: {description}")
        return False
    print(f"✓ {description} complete")
    return True


def main():
    """Main setup process."""
    print("=" * 60)
    print("Transcribair Setup")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Create a virtual environment")
    print("  2. Install Python dependencies (including LLM providers)")
    print("  3. Install FFmpeg (if needed)")
    print("  4. Set up the application")
    print("\nNote: For feedback organization features, you'll need an LLM provider:")
    print("  - Ollama (local, recommended): Install from https://ollama.ai")
    print("  - OpenAI: Requires API key from platform.openai.com")
    print("  - Anthropic: Requires API key from console.anthropic.com")
    print()

    response = input("Continue? [Y/n]: ").strip().lower()
    if response and response not in ['y', 'yes']:
        print("Setup cancelled.")
        return 1

    project_root = Path(__file__).parent
    venv_dir = project_root / "venv"
    system = platform.system()

    # Determine Python command
    python_cmd = sys.executable

    # Step 1: Create virtual environment
    print("\n" + "=" * 60)
    print("Step 1: Creating Virtual Environment")
    print("=" * 60)

    if venv_dir.exists():
        print(f"Virtual environment already exists at: {venv_dir}")
        response = input("Recreate it? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            import shutil
            print("Removing existing virtual environment...")
            shutil.rmtree(venv_dir)
        else:
            print("Using existing virtual environment.")

    if not venv_dir.exists():
        if not run_command(
            [python_cmd, "-m", "venv", str(venv_dir)],
            "Creating virtual environment"
        ):
            return 1

    # Determine venv Python and pip paths
    if system == "Windows":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
        activate_script = venv_dir / "Scripts" / "activate.bat"
        activate_cmd = str(activate_script)
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"
        activate_script = venv_dir / "bin" / "activate"
        activate_cmd = f"source {activate_script}"

    # Step 2: Upgrade pip
    print("\n" + "=" * 60)
    print("Step 2: Upgrading pip")
    print("=" * 60)

    if not run_command(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrading pip"
    ):
        return 1

    # Step 3: Install dependencies
    print("\n" + "=" * 60)
    print("Step 3: Installing Dependencies")
    print("=" * 60)

    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        print("✗ requirements.txt not found!")
        return 1

    if not run_command(
        [str(venv_pip), "install", "-r", str(requirements_file)],
        "Installing Python dependencies"
    ):
        return 1

    # Step 4: Install FFmpeg
    print("\n" + "=" * 60)
    print("Step 4: Installing FFmpeg")
    print("=" * 60)

    # Check if FFmpeg is already available
    import shutil
    ffmpeg_installed = False

    if shutil.which("ffmpeg"):
        print("✓ FFmpeg already installed in system PATH")
        ffmpeg_installed = True
    else:
        print("FFmpeg not found. Installing automatically...")
        install_ffmpeg_script = project_root / "install_ffmpeg.py"
        if install_ffmpeg_script.exists():
            # Use --auto flag for non-interactive installation
            result = subprocess.run(
                [str(venv_python), str(install_ffmpeg_script), "--auto"],
                capture_output=False
            )
            if result.returncode == 0:
                print("✓ FFmpeg installed successfully")

                # Verify installation by checking the install location
                ffmpeg_dir = Path.home() / ".transcribair" / "ffmpeg"
                ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"
                if ffmpeg_exe.exists():
                    ffmpeg_installed = True
                    print(f"✓ FFmpeg verified at: {ffmpeg_dir}")
                else:
                    print("✗ FFmpeg installation verification failed")
            else:
                print("✗ FFmpeg installation failed")
        else:
            print("✗ install_ffmpeg.py not found")

    if not ffmpeg_installed:
        print("\n" + "=" * 60)
        print("ERROR: FFmpeg Installation Required")
        print("=" * 60)
        print("\nFFmpeg is required for Transcribair to function.")
        print("Installation failed. Please install FFmpeg manually:")
        print("  1. Download from: https://ffmpeg.org/download.html")
        print("  2. Add to system PATH")
        print("  3. Or run: python install_ffmpeg.py")
        print("\nSetup cannot continue without FFmpeg.")
        return 1

    # Step 5: Test installation
    print("\n" + "=" * 60)
    print("Step 5: Testing Installation")
    print("=" * 60)

    test_imports = [
        "customtkinter",
        "faster_whisper",
        "sounddevice",
        "soundfile",
        "pydub",
        "ollama",
        "openai",
        "anthropic",
        "reportlab",
        "docx"
    ]

    print("Testing imports...")
    all_ok = True
    for module in test_imports:
        result = subprocess.run(
            [str(venv_python), "-c", f"import {module}"],
            capture_output=True
        )
        if result.returncode == 0:
            print(f"  ✓ {module}")
        else:
            print(f"  ✗ {module} - FAILED")
            all_ok = False

    # Success message
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)

    if all_ok:
        print("\n✓ All dependencies installed successfully!")
    else:
        print("\n⚠ Some dependencies failed to import.")
        print("  You may need to troubleshoot the installation.")

    print(f"\nVirtual environment created at: {venv_dir}")
    print("\nTo activate the virtual environment:")
    if system == "Windows":
        print(f"  {activate_cmd}")
    else:
        print(f"  {activate_cmd}")

    print("\nTo run the application:")
    if system == "Windows":
        print(f"  {venv_python} app.py")
        print("  or")
        print(f"  {activate_cmd} && python app.py")
    else:
        print(f"  {venv_python} app.py")
        print("  or")
        print(f"  {activate_cmd} && python app.py")

    print("\nTo build the executable:")
    print(f"  {activate_cmd} && pip install pyinstaller && python build.py")

    print("\n" + "=" * 60)
    print("Optional: Install Ollama for Local Feedback Organization")
    print("=" * 60)
    print("\nFor the feedback organization feature, you can:")
    print("  1. Install Ollama (recommended - free, runs locally):")
    print("     - Download from: https://ollama.ai")
    print("     - After installing, run: ollama pull llama2")
    print("     - Configure in app via Settings button")
    print("\n  2. Or use cloud providers (OpenAI/Anthropic):")
    print("     - Configure API keys in Settings after first launch")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Setup failed with error: {e}")
        sys.exit(1)
