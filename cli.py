"""
Interactive CLI for Bato Downloader using Typer + Rich.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich import print as rprint
from typing import Optional, List
from pathlib import Path
import sys

from src.scraper import search_manga, fetch_manga_info, fetch_chapters, SearchResult, MangaInfo, Chapter
from src.downloader.chapter_downloader import ChapterDownloader, DownloadProgress
from src.downloader.converter import images_to_pdf, images_to_cbz, cleanup_images
from src.config import get_config, save_config

app = typer.Typer()
console = Console()


def clear_screen():
    """Clear terminal screen."""
    console.clear()


def print_header():
    """Print application header."""
    header = Text()
    header.append("📚 ", style="bold")
    header.append("BATO DOWNLOADER", style="bold cyan")
    header.append(" 📚", style="bold")
    
    console.print(Panel(header, style="cyan", padding=(0, 2)))
    console.print()


def print_menu():
    """Print main menu."""
    console.print("[bold cyan]Main Menu[/bold cyan]")
    console.print()
    console.print("  [1] 📥 Download Manga by URL")
    console.print("  [2] 🔍 Search For Manga")
    console.print("  [3] ⚙️  Settings")
    console.print("  [4] 🚪 Exit")
    console.print()


def display_manga_info(info: MangaInfo):
    """Display manga information in a nice format."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Title", info.title)
    table.add_row("Authors", ", ".join(info.authors) if info.authors else "Unknown")
    table.add_row("Status", info.status or "Unknown")
    table.add_row("Genres", ", ".join(info.genres[:5]) if info.genres else "N/A")
    if info.description:
        desc = info.description[:200] + "..." if len(info.description) > 200 else info.description
        table.add_row("Description", desc)
    table.add_row("Views", info.views or "N/A")
    
    console.print(Panel(table, title="[bold]Manga Info[/bold]", border_style="green"))


def display_chapters(chapters: List[Chapter], page: int = 1, per_page: int = 200):
    """Display chapters with pagination."""
    total_pages = (len(chapters) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    page_chapters = chapters[start:end]
    
    table = Table(title=f"Chapters (Page {page}/{total_pages})", show_header=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Chapter", style="cyan")
    table.add_column("Title", style="white")
    
    for i, chapter in enumerate(page_chapters, start=start+1):
        table.add_row(str(i), chapter.number, chapter.title or "")
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(chapters)} chapters[/dim]")
    
    return total_pages


def select_chapters(chapters: List[Chapter]) -> List[Chapter]:
    """Interactive chapter selection."""
    console.print("\n[cyan]Chapter Selection[/cyan]")
    console.print("Enter chapter numbers or ranges (e.g., 1,3,5-10 or 'all')")
    console.print("[dim]Press Enter for all chapters[/dim]\n")
    
    selection = Prompt.ask("Select chapters", default="all")
    
    if selection.lower() == "all" or selection == "":
        return chapters
    
    selected_indices = set()
    parts = selection.replace(" ", "").split(",")
    
    for part in parts:
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                for i in range(start, end + 1):
                    if 1 <= i <= len(chapters):
                        selected_indices.add(i - 1)
            except ValueError:
                continue
        else:
            try:
                idx = int(part)
                if 1 <= idx <= len(chapters):
                    selected_indices.add(idx - 1)
            except ValueError:
                continue
    
    return [chapters[i] for i in sorted(selected_indices)]


def download_chapters(chapters: List[Chapter], manga_info: MangaInfo):
    """Download selected chapters with progress display using concurrent downloads."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    config = get_config()
    output_dir = Path(config.output_directory) if config.output_directory else Path(".")
    
    console.print(f"\n[cyan]Downloading {len(chapters)} chapter(s) to:[/cyan] {output_dir}")
    console.print(f"[dim]Format: {config.download_format} | Concurrent: {config.concurrent_chapters}[/dim]\n")
    
    completed = 0
    failed = 0
    
    def download_single(chapter: Chapter):
        """Download a single chapter."""
        downloader = ChapterDownloader(lambda p: None)  # No per-image progress in concurrent mode
        success, chapter_folder = downloader.download_chapter(
            chapter,
            output_dir,
            manga_info.title
        )
        
        if success and config.download_format != 'images':
            if config.download_format == 'pdf':
                output_file = chapter_folder.parent / f"{chapter_folder.name}.pdf"
                images_to_pdf(chapter_folder, output_file)
            else:  # cbz
                output_file = chapter_folder.parent / f"{chapter_folder.name}.cbz"
                images_to_cbz(chapter_folder, output_file, manga_info, chapter)
            
            if not config.keep_images_after_conversion:
                cleanup_images(chapter_folder)
        
        return chapter, success
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        overall_task = progress.add_task("[cyan]Downloading chapters...", total=len(chapters))
        
        with ThreadPoolExecutor(max_workers=config.concurrent_chapters) as executor:
            futures = {executor.submit(download_single, ch): ch for ch in chapters}
            
            for future in as_completed(futures):
                chapter = futures[future]
                try:
                    _, success = future.result()
                    if success:
                        completed += 1
                        progress.console.print(f"  [green]✓[/green] Chapter {chapter.number}")
                    else:
                        failed += 1
                        progress.console.print(f"  [red]✗[/red] Chapter {chapter.number} failed")
                except Exception as e:
                    failed += 1
                    progress.console.print(f"  [red]✗[/red] Chapter {chapter.number}: {e}")
                
                progress.update(overall_task, advance=1)
    
    console.print(f"\n[bold green]✓ Download complete![/bold green] ({completed} succeeded, {failed} failed)")


def download_by_url():
    """Download manga by URL option."""
    clear_screen()
    print_header()
    
    console.print("[bold cyan]📥 Download Manga by URL[/bold cyan]\n")
    
    url = Prompt.ask("Enter manga URL")
    
    if not url or "bato" not in url.lower():
        console.print("[red]Invalid URL. Please enter a valid bato.to URL.[/red]")
        Prompt.ask("\nPress Enter to continue")
        return
    
    console.print("\n[dim]Fetching manga info...[/dim]")
    
    try:
        with console.status("[cyan]Loading manga info..."):
            info = fetch_manga_info(url)
            chapters = fetch_chapters(url)
        
        display_manga_info(info)
        console.print()
        
        # Reverse chapters so Ch.1 is first (matching display order)
        chapters_ordered = list(reversed(chapters))
        display_chapters(chapters_ordered)
        
        selected = select_chapters(chapters_ordered)
        
        if selected and Confirm.ask(f"\nDownload {len(selected)} chapter(s)?"):
            download_chapters(selected, info)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    Prompt.ask("\nPress Enter to continue")


def search_for_manga():
    """Search for manga option."""
    clear_screen()
    print_header()
    
    console.print("[bold cyan]🔍 Search For Manga[/bold cyan]\n")
    
    query = Prompt.ask("Enter search term")
    
    if not query:
        return
    
    page = 1
    
    while True:
        try:
            with console.status(f"[cyan]Searching for '{query}' (page {page})..."):
                results = search_manga(query, page=page)
            
            if not results:
                console.print("[yellow]No results found.[/yellow]")
                Prompt.ask("\nPress Enter to continue")
                return
            
            # Display results
            table = Table(title=f"Search Results (Page {page})", show_header=True)
            table.add_column("#", style="dim", width=4)
            table.add_column("Name", style="cyan")
            table.add_column("Authors", style="white", max_width=30)
            table.add_column("Latest", style="green", max_width=20)
            
            for i, result in enumerate(results, 1):
                authors = ", ".join(result.authors[:2]) if result.authors else ""
                latest = result.latest_chapter or ""
                if len(latest) > 20:
                    latest = latest[:17] + "..."
                table.add_row(str(i), result.name, authors, latest)
            
            console.print(table)
            console.print(f"\n[dim]Found {len(results)} results[/dim]")
            
            # Menu
            console.print("\n[dim]Enter number to select, 'n' for next page, 'p' for previous, 'q' to quit[/dim]")
            choice = Prompt.ask("Choice", default="q")
            
            if choice.lower() == 'q':
                return
            elif choice.lower() == 'n':
                page += 1
                clear_screen()
                print_header()
                console.print("[bold cyan]🔍 Search For Manga[/bold cyan]\n")
                continue
            elif choice.lower() == 'p' and page > 1:
                page -= 1
                clear_screen()
                print_header()
                console.print("[bold cyan]🔍 Search For Manga[/bold cyan]\n")
                continue
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(results):
                        selected = results[idx]
                        
                        # Load selected manga
                        with console.status("[cyan]Loading manga..."):
                            info = fetch_manga_info(selected.full_url)
                            chapters = fetch_chapters(selected.full_url)
                        
                        clear_screen()
                        print_header()
                        display_manga_info(info)
                        console.print()
                        
                        # Reverse chapters so Ch.1 is first
                        chapters_ordered = list(reversed(chapters))
                        display_chapters(chapters_ordered)
                        
                        selected_chapters = select_chapters(chapters_ordered)
                        
                        if selected_chapters and Confirm.ask(f"\nDownload {len(selected_chapters)} chapter(s)?"):
                            download_chapters(selected_chapters, info)
                        
                        Prompt.ask("\nPress Enter to continue")
                        return
                except ValueError:
                    pass
                    
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            Prompt.ask("\nPress Enter to continue")
            return


def settings_menu():
    """Settings menu option."""
    while True:
        clear_screen()
        print_header()
        
        config = get_config()
        
        console.print("[bold cyan]⚙️  Settings[/bold cyan]\n")
        
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="dim", width=4)
        table.add_column("Setting", style="cyan", width=28)
        table.add_column("Value", style="white")
        
        table.add_row("[1]", "Download Format", config.download_format)
        table.add_row("[2]", "Output Directory", config.output_directory or "(Current folder)")
        table.add_row("[3]", "Concurrent Chapters", str(config.concurrent_chapters))
        table.add_row("[4]", "Concurrent Images", str(config.concurrent_images))
        table.add_row("[5]", "Max Chapter Retries", str(config.max_chapter_retries))
        table.add_row("[6]", "Max Image Retries", str(config.max_image_retries))
        table.add_row("[7]", "Keep Images After Convert", "Yes" if config.keep_images_after_conversion else "No")
        table.add_row("[8]", "Enable Detailed Logs", "Yes" if config.enable_detailed_logs else "No")
        table.add_row("", "", "")
        table.add_row("[0]", "Back to Main Menu", "")
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask("Select option", default="0")
        
        if choice == "0":
            return
        elif choice == "1":
            formats = ["images", "pdf", "cbz"]
            console.print("\nAvailable formats: images, pdf, cbz")
            new_format = Prompt.ask("Enter format", default=config.download_format)
            if new_format in formats:
                config.download_format = new_format
                config.save()
                console.print("[green]✓ Saved[/green]")
        elif choice == "2":
            new_dir = Prompt.ask("Enter output directory", default=config.output_directory or "")
            config.output_directory = new_dir
            config.save()
            console.print("[green]✓ Saved[/green]")
        elif choice == "3":
            new_val = IntPrompt.ask("Concurrent chapters (1-10)", default=config.concurrent_chapters)
            config.concurrent_chapters = max(1, min(10, new_val))
            config.save()
            console.print("[green]✓ Saved[/green]")
        elif choice == "4":
            new_val = IntPrompt.ask("Concurrent images (1-20)", default=config.concurrent_images)
            config.concurrent_images = max(1, min(20, new_val))
            config.save()
            console.print("[green]✓ Saved[/green]")
        elif choice == "5":
            new_val = IntPrompt.ask("Max chapter retries (1-10)", default=config.max_chapter_retries)
            config.max_chapter_retries = max(1, min(10, new_val))
            config.save()
            console.print("[green]✓ Saved[/green]")
        elif choice == "6":
            new_val = IntPrompt.ask("Max image retries (1-10)", default=config.max_image_retries)
            config.max_image_retries = max(1, min(10, new_val))
            config.save()
            console.print("[green]✓ Saved[/green]")
        elif choice == "7":
            config.keep_images_after_conversion = Confirm.ask("Keep images after conversion?")
            config.save()
            console.print("[green]✓ Saved[/green]")
        elif choice == "8":
            config.enable_detailed_logs = Confirm.ask("Enable detailed logs?")
            config.save()
            console.print("[green]✓ Saved[/green]")


def main_menu():
    """Main interactive menu loop."""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4"], default="4")
        
        if choice == "1":
            download_by_url()
        elif choice == "2":
            search_for_manga()
        elif choice == "3":
            settings_menu()
        elif choice == "4":
            console.print("\n[cyan]Goodbye! 👋[/cyan]\n")
            break


@app.command()
def interactive():
    """Run the interactive CLI menu."""
    main_menu()


@app.command()
def download(url: str):
    """Download manga directly by URL."""
    console.print(f"[cyan]Fetching manga from:[/cyan] {url}\n")
    
    try:
        info = fetch_manga_info(url)
        chapters = fetch_chapters(url)
        
        display_manga_info(info)
        console.print(f"\n[cyan]Found {len(chapters)} chapters[/cyan]")
        
        if Confirm.ask("Download all chapters?"):
            download_chapters(chapters, info)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()  
def search(query: str, page: int = 1):
    """Search for manga by name."""
    console.print(f"[cyan]Searching for:[/cyan] {query}\n")
    
    try:
        results = search_manga(query, page=page)
        
        if not results:
            console.print("[yellow]No results found.[/yellow]")
            raise typer.Exit(0)
        
        table = Table(title=f"Search Results (Page {page})")
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="dim")
        
        for i, result in enumerate(results, 1):
            table.add_row(str(i), result.name, result.full_url)
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    # Default to interactive mode if no args
    if len(sys.argv) == 1:
        main_menu()
    else:
        app()
