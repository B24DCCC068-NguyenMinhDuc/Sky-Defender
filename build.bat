@echo off
setlocal
pushd "%~dp0"

echo === Sky Defender Build ===
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong tim thay trong PATH.
    popd
    pause
    exit /b 1
)

python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [INFO] PyInstaller chua co - cai dat...
    python -m pip install --upgrade pip
    python -m pip install pyinstaller pygame
    if errorlevel 1 (
        echo [ERROR] Khong cai duoc PyInstaller / pygame.
        popd
        pause
        exit /b 1
    )
)

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [INFO] Building SkyDefender.exe ...
python -m PyInstaller SkyDefender.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo [ERROR] Build that bai.
    popd
    pause
    exit /b 1
)

echo.
echo === DONE ===
echo Output: %CD%\dist\SkyDefender.exe
echo.
popd
pause
