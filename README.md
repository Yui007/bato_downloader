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
*   **Flexible Output:** Specify a custom directory for downloaded manga.
*   **User-Friendly Interfaces:** Choose between a powerful CLI built with `Typer` and `Rich`, or an intuitive GUI built with `CustomTkinter`.
*   **Robust Scraping:** Handles image extraction and sanitization for file paths.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Yui007/bato_downloader.git
    cd bato_downloader
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Command-Line Interface (CLI)

The CLI is built with `Typer` and provides several commands.

To run the CLI, navigate to the project directory and use `python cli.py [command] [options]`.

*   **Get Manga Info:**
    ```bash
    python cli.py info "https://bato.to/series/143275/no-guard-wife"
    ```
    This command fetches and displays the manga title and the number of chapters. It will also prompt you if you want to list all chapters.

*   **Search Manga:**
    ```bash
    python cli.py search "Solo Leveling"
    ```
    This command searches for manga series matching the query and lists their titles and URLs.

*   **List Chapters:**
    ```bash
    python cli.py list "https://bato.to/series/143275/no-guard-wife"
    ```
    This command fetches and lists all chapters for the given series URL, including their titles and URLs.

*   **Download Chapters:**
    *   **Download all chapters:**
        ```bash
        python cli.py download "https://bato.to/series/143275/no-guard-wife" --all -o "MangaDownloads"
        ```
    *   **Download a specific range of chapters (e.g., chapters 1 to 10):**
        ```bash
        python cli.py download "https://bato.to/series/143275/no-guard-wife" --range "1-10" -o "MangaDownloads"
        ```
    *   **Convert to PDF:** Use the `--pdf` flag to convert downloaded chapters into a single PDF file. By default, original images are deleted after conversion.
        ```bash
        python cli.py download "https://bato.to/series/143275/no-guard-wife" --all --pdf -o "MangaDownloads"
        ```
    *   **Keep Images with PDF:** Use the `--keep-images` flag along with `--pdf` to retain the original image files after PDF conversion.
        ```bash
        python cli.py download "https://bato.to/series/143275/no-guard-wife" --all --pdf --keep-images -o "MangaDownloads"
        ```
    *   **Specify output directory:** Use the `--output` or `-o` option to set the download directory. If not specified, chapters will be downloaded to the current working directory.

*   **Launch GUI:**
    ```bash
    python cli.py gui
    ```
    This command launches the graphical user interface.

### Graphical User Interface (GUI)

The GUI provides a visual way to interact with the scraper.

To launch the GUI, run:
```bash
python gui.py
# Or via the CLI:
python cli.py gui
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
*   **Keep Images Checkbox:** Enable this (along with "Convert to PDF") to keep original image files after PDF conversion.
*   **Select Output Dir Button:** Allows you to choose a directory where downloaded manga will be saved.
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
    *   `download_chapter(chapter_url, manga_title, chapter_title, output_dir, stop_event, convert_to_pdf, keep_images)`: Downloads all images for a given chapter, sanitizes chapter titles for file paths, creates necessary directories, and saves images. Now also handles optional PDF conversion and image deletion.
    *   `convert_chapter_to_pdf(chapter_dir, delete_images)`: Converts a directory of images into a single PDF file.
    *   Uses `requests` for HTTP requests and `BeautifulSoup` for parsing HTML.
    *   Includes basic error handling for network requests and JSON parsing.

## Dependencies

The project relies on the following Python libraries:

*   `typer`: For building the command-line interface.
*   `rich`: For beautiful terminal output in the CLI.
*   `customtkinter`: For creating the modern-looking graphical user interface.
*   `requests`: For making HTTP requests to Bato.to.
*   `beautifulsoup4`: For parsing HTML content and extracting data.
*   `Pillow`: For image processing and PDF creation.

## Error Handling

Both the CLI and GUI include basic error handling for network issues and invalid inputs. If an error occurs during fetching information or downloading, an appropriate message will be displayed in the console (CLI) or the output log/message box (GUI).

Common issues and tips:
*   **Invalid URL:** Ensure the Bato.to series URL is correct and accessible.
*   **Internet Connection:** Verify your internet connection if fetching or downloading fails.
*   **Rate Limiting:** Excessive requests might lead to temporary blocks. The `bato_scraper.py` includes a `time.sleep(1)` between search pages to mitigate this.
*   **Website Changes:** Bato.to's website structure might change, which could break the scraping logic. If the tool stops working, the scraping logic in `bato_scraper.py` might need updates.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.