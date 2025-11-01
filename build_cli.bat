@echo off
echo Building Bato.to Downloader CLI executable...
pyinstaller --clean build_cli.spec
echo CLI executable built successfully!
pause