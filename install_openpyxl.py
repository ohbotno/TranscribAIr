"""
Automatic openpyxl installer for Excel import functionality.
"""
import subprocess
import sys
from pathlib import Path


class OpenpyxlInstaller:
    """Handles automatic installation of openpyxl."""

    def __init__(self):
        self.package_name = "openpyxl"
        self.min_version = "3.0.0"

    def is_installed(self) -> bool:
        """Check if openpyxl is already installed."""
        try:
            import openpyxl
            return True
        except ImportError:
            return False

    def install(self) -> bool:
        """
        Install openpyxl using pip.

        Returns:
            True if installation succeeded, False otherwise
        """
        if self.is_installed():
            print(f"{self.package_name} is already installed")
            return True

        print(f"Installing {self.package_name}...")

        try:
            # Use the same Python interpreter that's running this script
            python_exe = sys.executable

            # Install using pip
            result = subprocess.run(
                [python_exe, "-m", "pip", "install", f"{self.package_name}>={self.min_version}"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if result.returncode == 0:
                print(f"Successfully installed {self.package_name}")
                return True
            else:
                print(f"Failed to install {self.package_name}")
                print(f"Error: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print(f"Installation timed out after 120 seconds")
            return False
        except Exception as e:
            print(f"Error during installation: {e}")
            return False


def main():
    """Standalone installer entry point."""
    installer = OpenpyxlInstaller()

    if installer.is_installed():
        print(f"✓ {installer.package_name} is already installed")
        return 0

    print(f"Installing {installer.package_name}...")
    if installer.install():
        print(f"✓ Successfully installed {installer.package_name}")
        return 0
    else:
        print(f"✗ Failed to install {installer.package_name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
