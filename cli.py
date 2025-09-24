import typer
from typing_extensions import Annotated
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
from concurrent.futures import ThreadPoolExecutor
import threading
import time # Import time for sleep

from bato_scraper import get_manga_info, download_chapter, search_manga

app = typer.Typer(help="Bato.to Manga Scraper CLI. Download manga chapters from Bato.to.")
console = Console()

@app.command(name="info", help="Get information about a manga series.")
def get_info(
    series_url: Annotated[str, typer.Argument(help="The Bato.to series URL (e.g., https://bato.to/series/143275/no-guard-wife).")]
):
    """
    Fetches and displays information about a manga series from Bato.to.
    """
    rprint(Panel(Text("--- Bato.to Manga Scraper CLI ---", justify="center", style="bold green"), style="green"))
    rprint(f"\n[bold blue]Fetching manga info from:[/bold blue] [link={series_url}]{series_url}[/link]")

    with console.status("[bold yellow]Fetching manga information...[/bold yellow]", spinner="dots"):
        try:
            manga_title, chapters = get_manga_info(series_url)
        except Exception as e:
            rprint(f"[bold red]Error fetching manga info:[/bold red] {e}")
            rprint("[bold red]Please ensure the URL is correct and you have an internet connection.[/bold red]")
            raise typer.Exit(code=1)

    if not manga_title or not chapters:
        rprint("[bold red]Could not retrieve manga title or chapters. Please check the URL.[/bold red]")
        raise typer.Exit(code=1)

    rprint(Panel(f"[bold cyan]Manga Title:[/bold cyan] [bold white]{manga_title}[/bold white]", style="cyan"))
    rprint(f"[bold magenta]Found {len(chapters)} chapters.[/bold magenta]")

    if Prompt.ask(Text("Do you want to list all chapters?", style="bold yellow"), choices=["yes", "no"], default="no") == "yes":
        list_chapters_func(chapters)

@app.command(name="search", help="Search for manga series by title.")
def search(
    query: Annotated[str, typer.Argument(help="The manga title to search for.")]
):
    """
    Searches for manga series on Bato.to and displays the results.
    """
    rprint(Panel(Text("--- Bato.to Manga Scraper CLI ---", justify="center", style="bold green"), style="green"))
    rprint(f"\n[bold blue]Searching for manga:[/bold blue] [bold white]{query}[/bold white]")

    with console.status("[bold yellow]Searching for manga series...[/bold yellow]", spinner="dots"):
        try:
            results = search_manga(query)
        except Exception as e:
            rprint(f"[bold red]Error during search:[/bold red] {e}")
            rprint("[bold red]Please ensure you have an internet connection.[/bold red]")
            raise typer.Exit(code=1)

    if not results:
        rprint(f"[bold yellow]No results found for '{query}'. Please try a different query.[/bold yellow]")
        return

    rprint(Panel(Text(f"--- Search Results for '{query}' ---", justify="center", style="bold blue"), style="blue"))
    for i, manga in enumerate(results):
        rprint(f"[bold white]{i+1}.[/bold white] [green]{manga['title']}[/green] ([link={manga['url']}]{manga['url']}[/link])")
    
    rprint("\n[bold yellow]You can use the URL from the search results with the 'info' or 'download' commands.[/bold yellow]")


@app.command(name="list", help="List all chapters for a given manga series URL.")
def list_chapters(
    series_url: Annotated[str, typer.Argument(help="The Bato.to series URL.")]
):
    """
    Lists all chapters for a given manga series URL.
    """
    rprint(Panel(Text("--- Bato.to Manga Scraper CLI ---", justify="center", style="bold green"), style="green"))
    rprint(f"\n[bold blue]Fetching manga info from:[/bold blue] [link={series_url}]{series_url}[/link]")

    with console.status("[bold yellow]Fetching manga information...[/bold yellow]", spinner="dots"):
        try:
            _, chapters = get_manga_info(series_url)
        except Exception as e:
            rprint(f"[bold red]Error fetching manga info:[/bold red] {e}")
            rprint("[bold red]Please ensure the URL is correct and you have an internet connection.[/bold red]")
            raise typer.Exit(code=1)

    if not chapters:
        rprint("[bold red]Could not retrieve chapters. Please check the URL.[/bold red]")
        raise typer.Exit(code=1)

    list_chapters_func(chapters)

def list_chapters_func(chapters):
    rprint(Panel(Text("--- Chapters ---", justify="center", style="bold blue"), style="blue"))
    for i, chapter in enumerate(chapters):
        rprint(f"[bold white]{i+1}.[/bold white] [green]{chapter['title']}[/green] ([link={chapter['url']}]{chapter['url']}[/link])")

@app.command(name="download", help="Download chapters from a manga series.")
def download(
    series_url: Annotated[str, typer.Argument(help="The Bato.to series URL.")],
    all_chapters: Annotated[bool, typer.Option("--all", "-a", help="Download all chapters.")] = False,
    chapter_range: Annotated[Optional[str], typer.Option("--range", "-r", help="Download a specific range of chapters (e.g., '1-10').")] = None,
    output_dir: Annotated[str, typer.Option("--output", "-o", help="Directory to save downloaded chapters.")] = ".",
    max_workers: Annotated[int, typer.Option("--max-workers", "-w", help="Maximum number of concurrent chapter downloads.")] = 3,
    image_workers: Annotated[int, typer.Option("--image-workers", "-iw", help="Maximum number of concurrent image downloads per chapter.")] = 15,
    convert_to_pdf: Annotated[bool, typer.Option("--pdf", help="Convert downloaded chapters to PDF.")] = False,
    convert_to_cbz: Annotated[bool, typer.Option("--cbz", help="Convert downloaded chapters to CBZ (comic book archive).")] = False,
    keep_images: Annotated[bool, typer.Option("--keep-images", help="Keep original image files after conversion. Only applicable with --pdf or --cbz.")] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Enable verbose output.")] = False
):
    """
    Downloads chapters from a manga series.
    """
    rprint(Panel(Text("--- Bato.to Manga Scraper CLI ---", justify="center", style="bold green"), style="green"))
    rprint(f"\n[bold blue]Fetching manga info from:[/bold blue] [link={series_url}]{series_url}[/link]")

    with console.status("[bold yellow]Fetching manga information...[/bold yellow]", spinner="dots"):
        try:
            manga_title, chapters = get_manga_info(series_url)
        except Exception as e:
            rprint(f"[bold red]Error fetching manga info:[/bold red] {e}")
            rprint("[bold red]Please ensure the URL is correct and you have an internet connection.[/bold red]")
            raise typer.Exit(code=1)

    if not manga_title or not chapters:
        rprint("[bold red]Could not retrieve manga title or chapters. Please check the URL.[/bold red]")
        raise typer.Exit(code=1)

    rprint(Panel(f"[bold cyan]Manga Title:[/bold cyan] [bold white]{manga_title}[/bold white]", style="cyan"))
    rprint(f"[bold magenta]Found {len(chapters)} chapters.[/bold magenta]")

    chapters_to_download = []

    if all_chapters:
        chapters_to_download = chapters
        rprint("\n[bold blue]--- Downloading all chapters ---[/bold blue]")
    elif chapter_range:
        try:
            start_chap_str, end_chap_str = chapter_range.split('-')
            start_chap = int(start_chap_str)
            end_chap = int(end_chap_str)

            if not (1 <= start_chap <= len(chapters) and 1 <= end_chap <= len(chapters) and start_chap <= end_chap):
                rprint("[bold red]Invalid chapter range. Please enter valid numbers within the available range.[/bold red]")
                raise typer.Exit(code=1)

            chapters_to_download = chapters[start_chap - 1:end_chap]
            rprint(f"\n[bold blue]--- Downloading chapters {start_chap} to {end_chap} ---[/bold blue]")
        except ValueError:
            rprint("[bold red]Invalid range format. Use 'start-end' (e.g., '1-10').[/bold red]")
            raise typer.Exit(code=1)
    else:
        rprint("[bold yellow]No download option selected. Use --all or --range.[/bold yellow]")
        raise typer.Exit(code=0)

    if not chapters_to_download:
        rprint("[bold yellow]No chapters selected for download.[/bold yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console
    ) as progress:
        task = progress.add_task("[bold green]Downloading chapters...", total=len(chapters_to_download))
        
        # Use a lock for thread-safe printing with rich
        print_lock = threading.Lock()
        stop_event = threading.Event() # Event to signal stopping downloads

        def download_single_chapter_cli(chapter, index, stop_event):
            if stop_event.is_set():
                if verbose:
                    with print_lock:
                        rprint(f"[bold yellow]Skipping {chapter['title']} (download stopped).[/bold yellow]")
                return

            if verbose:
                with print_lock:
                    progress.update(task, description=f"[bold green]Downloading {chapter['title']}...[/bold green] ([{index+1}/{len(chapters_to_download)}])")
            try:
                download_chapter(chapter['url'], manga_title, chapter['title'], output_dir, stop_event, convert_to_pdf, convert_to_cbz, keep_images, image_workers)
                if not stop_event.is_set() and verbose: # Only update progress if not stopped
                    with print_lock:
                        progress.advance(task)
            except Exception as e:
                if not stop_event.is_set(): # Only log error if not stopped by user
                    with print_lock:
                        rprint(f"[bold red]Error downloading {chapter['title']}:[/bold red] {e}")

        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor: # Adjust max_workers as needed for chapters
                futures = []
                for i, chapter in enumerate(chapters_to_download):
                    if stop_event.is_set():
                        rprint("[bold yellow]Download stopped by user.[/bold yellow]")
                        break
                    futures.append(executor.submit(download_single_chapter_cli, chapter, i, stop_event))
                
                # Wait for all futures to complete or for the stop event to be set
                for future in futures:
                    try:
                        future.result() # This will re-raise any exceptions from the threads
                    except Exception as e:
                        # Handle exceptions from cancelled futures or other errors
                        pass
                    if stop_event.is_set():
                        # If stop is pressed, cancel remaining futures and break
                        for f in futures:
                            f.cancel()
                        break
        except KeyboardInterrupt:
                rprint("\n[bold yellow]KeyboardInterrupt detected. Stopping downloads...[/bold yellow]")
                stop_event.set() # Set the stop event
                progress.stop() # Stop the progress bar immediately
                # Allow a moment for threads to react to the stop event
                time.sleep(1) # Give threads a chance to finish current image or exit
        finally:
                if not stop_event.is_set():
                    rprint("\n[bold green]All selected chapters downloaded (or attempted).[/bold green]")
                else:
                    rprint("\n[bold yellow]Downloads stopped by user.[/bold yellow]")


@app.command(name="gui", help="Launch the GUI application.")
def launch_gui():
    """
    Launches the GUI application.
    """
    rprint(Panel(Text("--- Bato.to Manga Scraper GUI ---", justify="center", style="bold purple"), style="purple"))
    rprint("[bold yellow]Launching GUI...[/bold yellow]")
    try:
        from gui import main_gui
        main_gui()
    except ImportError:
        rprint("[bold red]GUI module not found. Please ensure 'gui.py' exists.[/bold red]")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[bold red]Error launching GUI:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
