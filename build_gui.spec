# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path
import customtkinter

# ✅ Ensure package is importable
root = Path.cwd()
sys.path.append(str(root / "src"))

import bato_downloader  # ensures package context

block_cipher = None

# Get customtkinter assets
customtkinter_path = Path(customtkinter.__file__).parent

a = Analysis(
    ['run_gui.py'],  # ✅ use entry point script
    pathex=[str(root)],
    binaries=[],
    datas=[(customtkinter_path, 'customtkinter')],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'bato_downloader.bato_scraper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='bato-downloader-gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version_file=None,
    icon=None,
)
