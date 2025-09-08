# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['build_entry.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ('models', 'models'),
        ('data', 'data'),
        ('config', 'config'),
    ],
    hiddenimports=[
        'luminous_nix',
        'luminous_nix.core',
        'luminous_nix.ai',
        'luminous_nix.ai.hrm_integrated_v6_final',
        'luminous_nix.ai.dev_environment_specialist',
        'luminous_nix.ai.update_maintenance_specialist',
        'luminous_nix.ai.transformer_enhanced_model',
        'luminous_nix.ai.active_learning_system',
        'luminous_nix.cache',
        'luminous_nix.services',
        'luminous_nix.ui',
        'click',
        'rich',
        'prompt_toolkit',
        'yaml',
        'toml',
        'textual',
        'httpx',
        'questionary',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torchvision', 'transformers'],  # Exclude heavy ML libs for basic version
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
    name='luminous-nix',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
