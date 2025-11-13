# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Transcribair.
Builds a standalone executable with all dependencies.

To build:
    pyinstaller build.spec
"""

import sys
from pathlib import Path

# Project paths
project_root = Path(SPECPATH)

block_cipher = None

# Analysis: collect all Python files and dependencies
a = Analysis(
    ['app.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include any data files here if needed
    ],
    hiddenimports=[
        'customtkinter',
        'faster_whisper',
        'sounddevice',
        'soundfile',
        'pydub',
        'numpy',
        'PIL',
        'tkinter',
        'ctypes',
        '_ctypes',
        'openpyxl',
        'reportlab',
        'docx',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude large packages not used
        'matplotlib',
        'scipy',
        'pandas',
        'torch',
        'tensorflow',
        'jax',
        # Test frameworks
        'pytest',
        'unittest',
        'nose',
        # Development tools
        'IPython',
        'jupyter',
        'notebook',
        # Documentation
        'sphinx',
        'docutils',
        # Unused stdlib modules
        'pydoc',
        'pdb',
        'difflib',
        'asyncio',
        'multiprocessing',
        'xml.dom',
        'xml.etree',
        'xmlrpc',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove duplicate binaries
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Transcribair',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,  # Disable stripping to avoid DLL issues
    upx=False,  # Disable UPX - causes DLL loading issues on some systems
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add .ico file path here if you have an icon
    version_file=None,  # Can add version info resource file
)

# Note: FFmpeg binaries need to be installed separately
# pydub will use system FFmpeg if available
# For fully portable builds, you would need to bundle FFmpeg binaries
