@echo off
REM ================================================
REM   Bato Downloader GUI - Build Script
REM   Creates: BatoDownloaderGUI.exe (Windowed)
REM ================================================

echo.
echo ╔════════════════════════════════════════╗
echo ║     BATO DOWNLOADER GUI BUILDER        ║
echo ║         (Windowed Mode)                ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Clean previous GUI build only
echo [*] Cleaning previous GUI build...
if exist "dist\BatoDownloaderGUI.exe" del /q "dist\BatoDownloaderGUI.exe"
if exist "build\BatoDownloaderGUI" rmdir /s /q "build\BatoDownloaderGUI"
echo.

REM Build the GUI application
echo [*] Building Bato Downloader GUI...
echo.

pyinstaller --noconfirm --onefile --windowed ^
    --name "BatoDownloaderGUI" ^
    --hidden-import "PyQt6" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "requests" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    main.py

echo.
if %errorlevel% equ 0 (
    echo ╔════════════════════════════════════════╗
    echo ║         BUILD SUCCESSFUL!              ║
    echo ╚════════════════════════════════════════╝
    echo.
    echo   Output: dist\BatoDownloaderGUI.exe
    echo.
) else (
    echo ╔════════════════════════════════════════╗
    echo ║           BUILD FAILED!                ║
    echo ╚════════════════════════════════════════╝
    echo   Check error messages above.
)

pause
