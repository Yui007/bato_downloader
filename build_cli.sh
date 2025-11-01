#!/bin/bash

# CLI Build Script for Linux/Mac
echo "Building Bato.to Downloader CLI executable..."
pyinstaller --clean build_cli.spec
echo "CLI executable built successfully!"