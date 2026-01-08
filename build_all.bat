@echo off
REM ================================================
REM   Bato Downloader - Build All Script
REM   Creates both GUI and CLI executables
REM ================================================

echo.
echo ╔════════════════════════════════════════════════╗
echo ║       BATO DOWNLOADER - BUILD ALL             ║
echo ║   Building GUI (Windowed) + CLI (Console)     ║
echo ╚════════════════════════════════════════════════╝
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Clean all previous builds
echo [*] Cleaning previous builds...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
echo.

REM ================================================
REM                 BUILD GUI
REM ================================================
echo ┌────────────────────────────────────────┐
echo │  [1/2] Building GUI (Windowed)...      │
echo └────────────────────────────────────────┘
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

if %errorlevel% neq 0 (
    echo [X] GUI build failed!
    goto :end
)
echo [OK] GUI build complete!
echo.

REM ================================================
REM                 BUILD CLI
REM ================================================
echo ┌────────────────────────────────────────┐
echo │  [2/2] Building CLI (Console)...       │
echo └────────────────────────────────────────┘
echo.

pyinstaller --noconfirm --onefile --console ^
    --name "BatoDownloaderCLI" ^
    --hidden-import "typer" ^
    --hidden-import "rich" ^
    --hidden-import "rich.console" ^
    --hidden-import "rich.panel" ^
    --hidden-import "rich.table" ^
    --hidden-import "rich.prompt" ^
    --hidden-import "rich.progress" ^
    --hidden-import "requests" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    cli.py

if %errorlevel% neq 0 (
    echo [X] CLI build failed!
    goto :end
)
echo [OK] CLI build complete!
echo.

REM ================================================
REM                SUMMARY
REM ================================================
echo.
echo ╔════════════════════════════════════════════════╗
echo ║           ALL BUILDS SUCCESSFUL!              ║
echo ╠════════════════════════════════════════════════╣
echo ║                                                ║
echo ║  dist\BatoDownloaderGUI.exe  (Windowed)       ║
echo ║  dist\BatoDownloaderCLI.exe  (Console)        ║
echo ║                                                ║
echo ╚════════════════════════════════════════════════╝
echo.

:end
pause
