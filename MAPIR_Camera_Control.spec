# -*- mode: python -*-

block_cipher = None


a = Analysis(['MAPIR_Camera_Control.py'],
             pathex=['C:\\Users\\peau\\Desktop\\Kernel_Interface'],
             binaries=[],
             datas=[('exiftool.exe', '.'), ('dcraw.exe', '.'), ('FiducialFinder.exe', '.'), ('Mapir_Converter.exe', '.'), ('Mapir_Converter_dark.exe', '.'),
             ('instring.txt', '.'),('calib.txt', '.'), 
             ('MAPIR_Processing_dockwidget_base.ui', '.'),
             ('MAPIR_Processing_dockwidget_CAN.ui', '.'),
             ('MAPIR_Processing_dockwidget_modal.ui', '.'),
             ('MAPIR_Processing_dockwidget_time.ui', '.'),
             (('_gdal.pyd'),'.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='MAPIR_Camera_Control',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='C:\\Users\\peau\\Desktop\\corn_logo_color_square_256x256.ico')
