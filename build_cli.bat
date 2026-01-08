@echo off
REM ================================================
REM   Bato Downloader CLI - Build Script
REM   Creates: BatoDownloaderCLI.exe (Console)
REM ================================================

echo.
echo ╔════════════════════════════════════════╗
echo ║      BATO DOWNLOADER CLI BUILDER       ║
echo ║          (Console Mode)                ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Clean previous CLI build only
echo [*] Cleaning previous CLI build...
if exist "dist\BatoDownloaderCLI.exe" del /q "dist\BatoDownloaderCLI.exe"
if exist "build\BatoDownloaderCLI" rmdir /s /q "build\BatoDownloaderCLI"
echo.

REM Build the CLI application
echo [*] Building Bato Downloader CLI...
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

echo.
if %errorlevel% equ 0 (
    echo ╔════════════════════════════════════════╗
    echo ║         BUILD SUCCESSFUL!              ║
    echo ╚════════════════════════════════════════╝
    echo.
    echo   Output: dist\BatoDownloaderCLI.exe
    echo.
) else (
    echo ╔════════════════════════════════════════╗
    echo ║           BUILD FAILED!                ║
    echo ╚════════════════════════════════════════╝
    echo   Check error messages above.
)

pause
