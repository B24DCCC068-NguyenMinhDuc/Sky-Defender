# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec — Sky Defender (onefile, windowed).

Build:
    python -m PyInstaller SkyDefender.spec --clean --noconfirm

Output:
    dist/SkyDefender.exe
"""

block_cipher = None

# Chỉ bundle các thư mục/file thực sự được main.py load.
datas = [
    ('assets/images', 'assets/images'),
    ('shooter_assets/img/explosion', 'shooter_assets/img/explosion'),
    ('shooter_assets/img/start_btn.png', 'shooter_assets/img'),
    ('shooter_assets/img/restart_btn.png', 'shooter_assets/img'),
    ('shooter_assets/img/exit_btn.png', 'shooter_assets/img'),
    (
        'shooter_assets/kenney_space-shooter-extension/PNG/Sprites',
        'shooter_assets/kenney_space-shooter-extension/PNG/Sprites',
    ),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
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
    name='SkyDefender',
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
)
