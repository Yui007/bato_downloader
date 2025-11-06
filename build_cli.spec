# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# ✅ Ensure package is importable
root = Path.cwd()
sys.path.append(str(root / "src"))

import bato_downloader  # ensures package context

block_cipher = None

a = Analysis(
    ['run_cli.py'],  # ✅ use entry point script
    pathex=[str(root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'bato_downloader.bato_scraper',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='bato-downloader-cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version_file=None,
    icon=None
)
