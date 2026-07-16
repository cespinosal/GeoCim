# -*- mode: python ; coding: utf-8 -*-
"""
GeoCim.spec  —  PyInstaller onedir (recomendado para QtWebEngine)
Uso:
    pyinstaller GeoCim.spec
El ejecutable queda en:  dist\GeoCim\GeoCim.exe
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('GeoCim.html', '.'),
        ('GeoCim.ico',  '.'),
        ('GeoCim.png',  '.'),
    ],
    hiddenimports=[
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebChannel',
        'PySide6.QtNetwork',
        'PySide6.QtPositioning',
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
    [],
    exclude_binaries=True,
    name='GeoCim',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    icon='GeoCim.ico',
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GeoCim',
)
