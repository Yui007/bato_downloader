# Bato.to Manga Downloader

A Python-based tool for searching, listing, and downloading manga chapters from Bato.to, featuring both a Command-Line Interface (CLI) and a Graphical User Interface (GUI).

![GUI Screenshot](GUI.PNG)

## Table of Contents

*   [Features](#features)
*   [Installation](#installation)
*   [Usage](#usage)
    *   [Command-Line Interface (CLI)](#command-line-interface-cli)
    *   [Graphical User Interface (GUI)](#graphical-user-interface-gui)
*   [Project Structure](#project-structure)
*   [Dependencies](#dependencies)
*   [Error Handling](#error-handling)
*   [License](#license)

## Features

*   **Manga Information:** Get details about a specific manga series using its Bato.to URL.
*   **Manga Search:** Search for manga series by title.
*   **Chapter Listing:** List all available chapters for a given manga series.
*   **Chapter Download:** Download single chapters, a range of chapters, or all chapters from a series.
*   **PDF Conversion:** Convert downloaded chapters into a single PDF file.
*   **CBZ Conversion:** Convert downloaded chapters into CBZ (comic book archive) files for digital comic readers.
*   **Flexible Output:** Specify a custom directory for downloaded manga.
*   **Concurrent Downloads:** Configurable threading for both chapter downloads and image downloads within chapters.
*   **Windows Compatibility:** Automatic sanitization of folder names to prevent invalid characters on Windows systems.
*   **User-Friendly Interfaces:** Choose between a powerful CLI built with `Typer` and `Rich`, or an intuitive GUI built with `CustomTkinter`.
*   **Robust Scraping:** Handles image extraction and sanitization for file paths.

## Installation

There are two primary methods to install Bato.to Downloader.

### Method 1: Install from PyPI (Recommended)

This is the easiest and fastest way to get started.

1.  **Install the package using `pip`:**
    ```bash
    pip install bato-downloader
    ```
2.  **Run the application:**
    *   To launch the GUI:
        ```bash
        bato-downloader-gui
        ```
    *   To use the CLI:
        ```bash
        bato-downloader --help
        ```

### Method 2: Install from Source (For Developers)

Use this method if you want to modify the code or contribute to the project.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Yui007/bato_downloader.git
    cd bato_downloader
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the project in editable mode:**
    ```bash
    pip install -e .
    ```
    This command reads the dependencies from `pyproject.toml` and installs them, while also making the project runnable from your local source code.

## Download Executables (No Installation Required)

For users who prefer not to install Python dependencies, you can download pre-built executables:

**For Windows:**
- `bato-downloader-cli.exe` - Command-line interface executable
- `bato-downloader-gui.exe` - Graphical user interface executable

**For Linux/Mac:**
- `bato-downloader-cli` - Command-line interface executable
- `bato-downloader-gui` - Graphical user interface executable

Simply download the executable for your platform and run it directly without any installation!

## Building Executables from Source

If you want to build your own executables:

1. **Install dependencies including PyInstaller:**
    ```bash
    pip install -r requirements.txt
    ```

2. **Build CLI executable:**
    - Windows: Run `build_cli.bat`
    - Linux/Mac: Run `build_cli.sh`

3. **Build GUI executable:**
    - Windows: Run `build_gui.bat`
    - Linux/Mac: Run `build_gui.sh`

The executables will be created in the `dist` directory.

## Usage

### Command-Line Interface (CLI)

The CLI is built with `Typer` and provides several commands.

To run the CLI from the source code, navigate to the project's root directory and use `python -m src.bato_downloader.cli [command] [options]`.

*   **Get Manga Info:**
    ```bash
    python -m src.bato_downloader.cli info "https://bato.to/series/143275/no-guard-wife"
    ```
    This command fetches and displays the manga title and the number of chapters. It will also prompt you if you want to list all chapters.

*   **Search Manga:**
    ```bash
    python -m src.bato_downloader.cli search "Solo Leveling"
    ```
    This command searches for manga series matching the query and lists their titles and URLs.

*   **List Chapters:**
    ```bash
    python -m src.bato_downloader.cli list "https://bato.to/series/143275/no-guard-wife"
    ```
    This command fetches and lists all chapters for the given series URL, including their titles and URLs.

*   **Download Chapters:**
    *   **Download all chapters:**
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --all -o "MangaDownloads"
        ```
    *   **Download a specific range of chapters (e.g., chapters 1 to 10):**
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --range "1-10" -o "MangaDownloads"
        ```
    *   **Convert to PDF:** Use the `--pdf` flag to convert downloaded chapters into a single PDF file. By default, original images are deleted after conversion.
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --all --pdf -o "MangaDownloads"
        ```
    *   **Convert to CBZ:** Use the `--cbz` flag to convert downloaded chapters into CBZ (comic book archive) files.
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --all --cbz -o "MangaDownloads"
        ```
    *   **Convert to both PDF and CBZ:** Use both flags to create both formats.
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --all --pdf --cbz -o "MangaDownloads"
        ```
    *   **Keep Images:** Use the `--keep-images` flag along with `--pdf` or `--cbz` to retain the original image files after conversion.
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --all --pdf --keep-images -o "MangaDownloads"
        ```
    *   **Concurrent Downloads:** Control download performance with threading options.
        *   `--max-workers` or `-w`: Maximum concurrent chapter downloads (default: 3)
        *   `--image-workers` or `-iw`: Maximum concurrent image downloads per chapter (default: 15)
        ```bash
        python -m src.bato_downloader.cli download "https://bato.to/series/143275/no-guard-wife" --all --pdf --max-workers 5 --image-workers 20
        ```
    *   **Specify output directory:** Use the `--output` or `-o` option to set the download directory. If not specified, chapters will be downloaded to the current working directory.

*   **Launch GUI:**
    ```bash
    python -m src.bato_downloader.cli gui
    ```
    This command launches the graphical user interface.

### Graphical User Interface (GUI)

The GUI provides a visual way to interact with the scraper.

To launch the GUI from source, run:
```bash
python -m src.bato_downloader.gui
# Or via the CLI:
python -m src.bato_downloader.cli gui
```

**GUI Features:**

*   **Series URL Input:** Enter the Bato.to series URL.
*   **Get Info Button:** Fetches and displays manga title and chapter count.
*   **Search Query Input:** Enter a manga title to search.
*   **Search Button:** Displays search results, allowing you to select a series to populate the URL field.
*   **List Chapters Button:** Displays all fetched chapters in the output log.
*   **Download All Button:** Downloads all chapters of the currently loaded manga.
*   **Download Range Button:** Prompts for a chapter range (e.g., `1-10`) and downloads those chapters.
*   **Convert to PDF Checkbox:** Enable this to convert downloaded chapters into PDF files.
*   **Convert to CBZ Checkbox:** Enable this to convert downloaded chapters into CBZ (comic book archive) files.
*   **Keep Images Checkbox:** Enable this (along with "Convert to PDF" or "Convert to CBZ") to keep original image files after conversion.
*   **Select Output Dir Button:** Allows you to choose a directory where downloaded manga will be saved.
*   **Settings Button:** Configure download performance with separate controls for chapter and image concurrency.
*   **Progress Bar:** Shows the download progress.
*   **Output Log:** Displays messages, search results, and download status.

## Project Structure

*   `cli.py`:
    *   Implements the command-line interface using `Typer`.
    *   Provides commands for `info`, `search`, `list`, `download`, and `gui` (to launch the GUI).
    *   Uses `rich` for enhanced terminal output (panels, colors, progress bars).
    *   Orchestrates calls to functions in `bato_scraper.py`.

*   `gui.py`:
    *   Implements the graphical user interface using `CustomTkinter`.
    *   Provides input fields for URL and search queries, and buttons for various actions.
    *   Manages UI state, progress bar updates, and logging messages to a text area.
    *   Uses `threading` to perform scraping and download operations in the background, preventing the UI from freezing.
    *   Interacts with `bato_scraper.py` for core functionality.

*   `bato_scraper.py`:
    *   Contains the core logic for scraping Bato.to.
    *   `search_manga(query, max_pages)`: Searches for manga based on a query across multiple pages.
    *   `get_manga_info(series_url)`: Extracts the manga title and a list of chapters (title and URL) from a series page.
    *   `download_chapter(chapter_url, manga_title, chapter_title, output_dir, stop_event, convert_to_pdf, convert_to_cbz, keep_images, max_workers)`: Downloads all images for a given chapter with configurable threading, sanitizes titles for file paths, creates necessary directories, and saves images. Handles optional PDF and CBZ conversion.
    *   `convert_chapter_to_pdf(chapter_dir, delete_images)`: Converts a directory of images into a single PDF file.
    *   `convert_chapter_to_cbz(chapter_dir, delete_images)`: Converts a directory of images into a CBZ (comic book archive) file.
    *   `sanitize_filename(name)`: Sanitizes filenames to remove invalid Windows characters and normalize spaces.
    *   Uses `requests` for HTTP requests, `BeautifulSoup` for parsing HTML, and `ThreadPoolExecutor` for concurrent downloads.
    *   Includes comprehensive error handling for network requests, JSON parsing, and file operations.

## Dependencies

The project relies on the following Python libraries:

*   `typer`: For building the command-line interface.
*   `rich`: For beautiful terminal output in the CLI.
*   `customtkinter`: For creating the modern-looking graphical user interface.
*   `requests`: For making HTTP requests to Bato.to.
*   `beautifulsoup4`: For parsing HTML content and extracting data.
*   `Pillow`: For image processing and PDF creation.
*   `urllib.parse` (built-in): For URL encoding in search queries.

**Note:** CBZ conversion uses Python's built-in `zipfile` module, so no additional dependencies are required.

## Error Handling

Both the CLI and GUI include comprehensive error handling for network issues, invalid inputs, and file system operations. If an error occurs during fetching information or downloading, an appropriate message will be displayed in the console (CLI) or the output log/message box (GUI).

Common issues and tips:
*   **Invalid URL:** Ensure the Bato.to series URL is correct and accessible.
*   **Internet Connection:** Verify your internet connection if fetching or downloading fails.
*   **Rate Limiting:** Excessive requests might lead to temporary blocks. The scraper includes delays between requests to mitigate this.
*   **Windows Compatibility:** Folder names are automatically sanitized to remove invalid characters like `:`, `<`, `>`, etc.
*   **Threading Issues:** If downloads fail intermittently, try reducing the concurrent download settings in the GUI or CLI options.
*   **Disk Space:** Ensure sufficient disk space for downloads, especially when keeping images after conversion.
*   **Website Changes:** Bato.to's website structure might change, which could break the scraping logic. If the tool stops working, the scraping logic in `bato_scraper.py` might need updates.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.