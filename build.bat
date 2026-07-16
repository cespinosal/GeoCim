@echo off
echo ============================================================
echo  GeoCim — Build PyInstaller
echo ============================================================
cd /d "%~dp0"

where pip >nul 2>&1 || (echo ERROR: pip no encontrado & pause & exit /b 1)

echo [1/3] Instalando dependencias...
pip install PySide6 pyinstaller --quiet

echo [2/3] Empaquetando con PyInstaller...
pyinstaller GeoCim.spec --noconfirm

echo [3/3] Listo.
echo El ejecutable esta en:  dist\GeoCim\GeoCim.exe
echo.
pause
