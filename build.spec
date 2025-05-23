# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['MedicalAnalyzer.py'],
    pathex=[],
    binaries=[],
    datas=[
        #('databases/doctors_db.xlsx', 'databases'),
        ('resources/icon.png', 'resources'),
        ('resources/icon2.png', 'resources'),
        ('resources/client_secret.json', 'resources'),
        #('Pictures/*.png','Pictures'),
        ('resources/token.json', 'resources'),
    ],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'sklearn',
        'sklearn.ensemble',
        'sklearn.linear_model',
        'sklearn.neighbors',
        'sklearn.tree',
        'matplotlib.backends.backend_qtagg',
        'numpy'
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
    name='MedicalAnalyzer',
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
    icon='resources/icon.png',  # Укажите путь к .ico файлу если есть
)
