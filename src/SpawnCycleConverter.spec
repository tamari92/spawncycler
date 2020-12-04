# -*- mode: python -*-

block_cipher = None


a = Analysis(['SpawnCycleConverter.py'],
             pathex=['C:\\SpawnCycler\\trunk\src\\one-file\\'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)


a.datas += [('img\\icon_go.png', 'C:\\SpawnCycler\\trunk\src\\img\\icon_go.png', "DATA"),
			('img\\icon_check.png', 'C:\\SpawnCycler\\trunk\src\\img\\icon_check.png', "DATA"),
			('img\\icon_warning.png', 'C:\\SpawnCycler\\trunk\src\\img\\icon_warning.png', "DATA"),
			('img\\logo.png', 'C:\\SpawnCycler\\trunk\src\\img\\logo.png', "DATA")]


pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)


exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SpawnCycleConverter',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='C:\\SpawnCycler\\trunk\src\\spawncycler.ico')
