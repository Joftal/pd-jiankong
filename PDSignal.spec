# -*- mode: python ; coding: utf-8 -*-
import os

# 获取当前目录的绝对路径
current_dir = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('sql', 'sql'), ('usersetting.json', '.'), ('pandatv.ico', '.')],
    hiddenimports=['flet', 'plyer', 'plyer.platforms', 'plyer.platforms.win', 'plyer.platforms.win.notification', 'win10toast', 'requests', 'certifi', 'urllib3', 'charset_normalizer', 'idna'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDSignal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(current_dir, 'pandatv.ico'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDSignal',
)
