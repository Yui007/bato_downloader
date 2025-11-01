@echo off
echo ========================================
echo Building Bato.to Downloader Executables
echo ========================================
echo.

echo Building CLI executable...
pyinstaller --clean build_cli.spec
if %errorlevel% neq 0 (
    echo Error building CLI executable!
    pause
    exit /b %errorlevel%
)
echo CLI executable built successfully!
echo.

echo Building GUI executable...
pyinstaller --clean build_gui.spec
if %errorlevel% neq 0 (
    echo Error building GUI executable!
    pause
    exit /b %errorlevel%
)
echo GUI executable built successfully!
echo.

echo ========================================
echo Both executables built successfully!
echo ========================================
echo.
echo You can find the executables in the 'dist' directory:
echo - bato-downloader-cli.exe
echo - bato-downloader-gui.exe
echo.
pause