<div align="center">

# 📚 Bato.to Manga Downloader

[![PyPI](https://img.shields.io/pypi/v/bato-downloader?style=for-the-badge&logo=pypi&logoColor=white&label=PyPI)](https://pypi.org/project/bato-downloader/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-GUI-green?style=for-the-badge&logo=qt&logoColor=white)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Beautiful manga downloader for bato.to, batotoo.com, and bato.si**

*Search, browse, and download your favorite manga with ease*

![GUI Screenshot](GUI.PNG)

</div>

---

## ✨ Features
<div align="center">
<table>
<tr>
<td width="50%">

### 🔍 Smart Search
- Search by manga title
- Card-based results with covers
- Authors, genres & ratings display
- Pagination support

</td>
<td width="50%">

### 📥 Powerful Downloads
- Concurrent chapter downloads
- Parallel image fetching
- Progress tracking
- Resume support

</td>
</tr>
<tr>
<td width="50%">

### 📁 Multiple Formats
- **Images** - Raw image files
- **PDF** - Single file per chapter
- **CBZ** - Comic book archive

</td>
<td width="50%">

### 🎨 Two Interfaces
- **GUI** - Beautiful PyQt6 interface
- **CLI** - Interactive Rich terminal

</td>
</tr>
</table>
</div>

---

## 🚀 Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install from PyPI
pip install bato-downloader

# Launch GUI
bato-downloader-gui

# Launch CLI
bato-downloader
```

> ✅ That's it! All dependencies are installed automatically.

### Option 2: Download Executables

| Platform | GUI | CLI |
|----------|-----|-----|
| Windows | [📥 BatoDownloaderGUI.exe](https://github.com/Yui007/bato_downloader/releases) | [📥 BatoDownloaderCLI.exe](https://github.com/Yui007/bato_downloader/releases) |

> Just download and run - no Python needed!

---

## 🖥️ Graphical User Interface

<div align="center">

| Search | Manga Details | Settings |
|--------|---------------|----------|
| Search by title | View chapters | Configure downloads |
| Cover previews | Select multiple | Set output format |
| One-click select | Download progress | Adjust concurrency |

</div>

### How to Use

1. **🔍 Search** - Enter manga name and press Search
2. **👆 Select** - Click a result card to view details
3. **☑️ Choose** - Select chapters you want to download
4. **📥 Download** - Click "Download Selected" and wait

---

## 💻 Command-Line Interface

```
╭────────────────────────────────────────╮
│       📚 BATO DOWNLOADER 📚            │
╰────────────────────────────────────────╯

Main Menu

  [1] 📥 Download Manga by URL
  [2] 🔍 Search For Manga
  [3] ⚙️  Settings
  [4] 🚪 Exit

Select option [1/2/3/4]:
```

### Direct Commands

```bash
# Interactive mode
bato-downloader

# Search for manga
bato-downloader search "Solo Leveling"

# Download from URL
bato-downloader download "https://bato.si/title/81514-solo-leveling"
```

---

## ⚙️ Configuration

Settings are saved in `config.json`:

| Setting | Options | Default |
|---------|---------|---------|
| 📁 `download_format` | `images` / `pdf` / `cbz` | `images` |
| 📂 `output_directory` | Any path | Current folder |
| ⚡ `concurrent_chapters` | 1-10 | `3` |
| 🖼️ `concurrent_images` | 1-20 | `5` |
| 💾 `keep_images_after_conversion` | `true` / `false` | `true` |

---

## 📁 Project Structure

```
bato_downloader/
├── 🚀 main.py              # GUI entry point
├── 🖥️ cli.py               # CLI entry point
├── 📁 gui/
│   ├── main_window.py      # Main window
│   ├── workers.py          # Background threads
│   ├── styles.py           # Theme & colors
│   └── widgets/            # UI components
├── 📁 src/
│   ├── config.py           # Settings
│   ├── scraper/            # Web scraping
│   └── downloader/         # Download logic
├── 🔧 build_gui.bat        # Build GUI
├── 🔧 build_cli.bat        # Build CLI
└── 🔧 build_all.bat        # Build both
```

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| ![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=flat-square&logo=qt) | Modern GUI framework |
| ![Typer](https://img.shields.io/badge/Typer-CLI-000?style=flat-square) | CLI framework |
| ![Rich](https://img.shields.io/badge/Rich-Terminal-purple?style=flat-square) | Beautiful terminal output |
| ![Requests](https://img.shields.io/badge/Requests-HTTP-blue?style=flat-square) | HTTP requests |
| ![Pillow](https://img.shields.io/badge/Pillow-Images-yellow?style=flat-square) | Image processing |

---

## ❓ Troubleshooting

<details>
<summary><b>🖼️ Cover images not loading</b></summary>

- Check your internet connection
- Covers load asynchronously, wait a moment
- Try refreshing the search

</details>

<details>
<summary><b>⏱️ Download timeouts</b></summary>

- Reduce `concurrent_chapters` in settings (try 1-2)
- Reduce `concurrent_images` in settings
- Check if the site is accessible

</details>

<details>
<summary><b>❌ Invalid URL error</b></summary>

- URL must contain `bato` and `/title/`
- Example: `https://bato.si/title/81514-solo-leveling`

</details>

<details>
<summary><b>📄 PDF conversion fails</b></summary>

```bash
pip install Pillow --upgrade
```

</details>

---

## 🛠️ Development

### Install from Source

```bash
# Clone the repository
git clone https://github.com/Yui007/bato_downloader.git
cd bato_downloader

# Install in development mode
pip install -e .

# Run directly
bato-downloader      # CLI
bato-downloader-gui  # GUI

# Or run scripts directly
python cli.py
python main.py
```

### Building Executables

```bash
# Build GUI only
.\build_gui.bat

# Build CLI only
.\build_cli.bat

# Build both at once
.\build_all.bat
```

**Output:**
```
dist/
├── BatoDownloaderGUI.exe   # 🖼️ Windowed application
└── BatoDownloaderCLI.exe   # 💻 Console application
```

---

<div align="center">

## 📜 License

This project is licensed under the **MIT License**

Made with ❤️ by [Yui007](https://github.com/Yui007)

⭐ Star this repo if you find it useful!

</div>