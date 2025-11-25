# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['scada_desktop_app\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('scada_desktop_app/ui', 'ui'), ('scada_desktop_app/utils', 'utils'), ('scada_desktop_app/models', 'models')],
    hiddenimports=['PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'scipy', 'PIL'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
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
