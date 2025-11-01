@echo off
echo Building Bato.to Downloader GUI executable...
pyinstaller --clean build_gui.spec
echo GUI executable built successfully!
pause