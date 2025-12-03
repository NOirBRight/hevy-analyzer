# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

# Collect all streamlit data files and submodules
streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all('streamlit')
altair_datas, altair_binaries, altair_hiddenimports = collect_all('altair')
pandas_datas = collect_data_files('pandas')
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all('plotly')

# Add app-specific data files
datas = [
    ('app.py', '.'),
    ('exercises.csv', '.'),
    ('muscle_heatmap_svg.html', '.'),
    ('muscle_heatmap_3d.html', '.'),
    ('muscle_heatmap_svg_backup.html', '.'),
]

# Add all collected data
datas += streamlit_datas
datas += altair_datas
datas += pandas_datas
datas += plotly_datas

# Hidden imports
hiddenimports = [
    'streamlit',
    'streamlit.web.cli',
    'streamlit.runtime.scriptrunner',
    'pandas',
    'numpy',
    'altair',
    'plotly',
    'plotly.express',
    'plotly.graph_objects',
    'requests',
    'PIL',
    'json',
    'datetime',
    'webbrowser',
    'threading',
]
hiddenimports += streamlit_hiddenimports
hiddenimports += altair_hiddenimports
hiddenimports += plotly_hiddenimports
hiddenimports += collect_submodules('streamlit')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('plotly')

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=streamlit_binaries + altair_binaries + plotly_binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='HevyAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='HevyAnalyzer',
)
