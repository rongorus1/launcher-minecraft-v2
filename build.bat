@echo off
setlocal
cd /d "%~dp0"

echo =============================================
echo   RongonLang Launcher - Build
echo =============================================

echo [1/5] Instalando dependencias...
python -m pip install -r src\requirements.txt pyinstaller
if errorlevel 1 goto :error

echo [2/5] Generando ejecutable directamente en dist\distribucion...
if exist "dist\distribucion\RongonLang Launcher" (
    rmdir /s /q "dist\distribucion\RongonLang Launcher"
)

python -m PyInstaller --noconfirm --onedir --noconsole --name "RongonLang Launcher" --distpath "dist\distribucion" --workpath "build" --icon Launcher.ico --paths src --add-data "src\assets;assets" --hidden-import PIL._tkinter_finder --hidden-import PIL.ImageTk --hidden-import cffi --hidden-import _cffi_backend --hidden-import unrar.cffi.rarfile src\main.py
if errorlevel 1 goto :error

echo [3/5] Empaquetando juego preinstalado dentro de la carpeta del launcher...
if exist "dist\distribucion\juego_preinstalado.zip" del /q "dist\distribucion\juego_preinstalado.zip"
python empaquetar_juego.py
if errorlevel 1 goto :error

echo [4/5] Añadiendo modpack e instrucciones al paquete...
if exist "Rongoland.rar" (
    copy /y "Rongoland.rar" "dist\distribucion\Rongoland.rar" >nul
)
if exist "INSTRUCCIONES.txt" (
    copy /y "INSTRUCCIONES.txt" "dist\distribucion\INSTRUCCIONES.txt" >nul
)

echo [5/5] Generando paquete de actualizacion (solo codigo) para GitHub Releases...
python empaquetar_actualizacion.py
if errorlevel 1 goto :error

rem Limpia los artefactos intermedios (evita exe duplicados)
if exist "build" (
    rmdir /s /q "build"
)

echo.
echo =============================================
echo   Listo: dist\distribucion\
echo   (carpeta "RongonLang Launcher" que incluye juego_preinstalado.zip adentro,
echo    mas Rongoland.rar e INSTRUCCIONES.txt)
echo   Este es el UNICO lugar con el ejecutable.
echo =============================================
pause
exit /b 0

:error
echo.
echo ERROR: algo fallo durante el proceso.
pause
exit /b 1