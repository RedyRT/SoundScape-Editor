# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['SoundScapeEditor.py'],
    pathex=[], binaries=[], datas=[], hiddenimports=[],
    hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False,
)
pyz = PYZ(a.pure)

splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(26, 254),        # строка статуса там же, где у Qt-сплэша (y=252..270)
    text_size=9,               # Consolas 9pt — как в Qt-сплэше
    text_color='#c7d0d9',
    text_default='Распаковка программы...',
    always_on_top=True,
)

exe = EXE(
    pyz, a.scripts,
    splash, splash.binaries,
    a.binaries, a.zipfiles, a.datas, [],
    name='SoundScapeEditor',
    debug=False, bootloader_ignore_signals=False, strip=False,
    upx=True, upx_exclude=[], runtime_tmpdir=None,
    console=False, icon='soundscape.ico',
)