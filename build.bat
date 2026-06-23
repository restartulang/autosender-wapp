@echo off
echo ==============================================
echo Building Autosender WAPP (Directory Mode)
echo ==============================================

echo [1/3] Membersihkan folder build lama (jika ada)...
rmdir /s /q build
rmdir /s /q dist

echo [2/3] Menjalankan PyInstaller...
python -m PyInstaller --noconfirm ^
  --windowed ^
  --name "Autosender_WAPP" ^
  --icon="assets\logo_final.ico" ^
  --add-data "database/schema.sql;database" ^
  --add-data "assets;assets" ^
  --add-data "browsers;browsers" ^
  --collect-all customtkinter ^
  --collect-all playwright ^
  main.py

echo [3/3] Proses kompilasi selesai!
echo Silakan periksa folder "dist\Autosender_WAPP"
