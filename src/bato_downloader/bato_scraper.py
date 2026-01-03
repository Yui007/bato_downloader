import requests
from bs4 import BeautifulSoup  # type: ignore
import os
import re
import json
import time # Import time for sleep
from concurrent.futures import ThreadPoolExecutor
import threading
from urllib.parse import quote
import zipfile
import xml.etree.ElementTree as ET
from xml.dom import minidom

def search_manga(query, max_pages=5):
    import html
    
    all_results = []
    seen_urls = set() # Use a set to store unique URLs
    page = 1
    
    # Primary domains use requests, bato.si requires Playwright
    primary_domains = ["https://bato.to", "https://batotoo.com"]
    active_domain = None

    while page <= max_pages:
        response = None
        current_domain = None
        
        # Determine which domain to use (or try options)
        # If we already have an active_domain that works, try that first (or only that)
        # However, if it fails, we might want to fallback? 
        # For simplicity, if we found a working domain, we stick to it.
        
        search_domains = [active_domain] if active_domain else primary_domains
        
        for domain in search_domains:
            search_url = f"{domain}/search?word={quote(query)}&page={page}"
            print(f"Searching page {page}: {search_url}")
            try:
                response = requests.get(search_url, timeout=10)
                response.raise_for_status()
                current_domain = domain
                if not active_domain:
                    active_domain = domain # Lock onto the first working domain
                break
            except requests.exceptions.RequestException as e:
                print(f"Error fetching search page {page} from {domain}: {e}")
                continue
        
        if not response or not current_domain:
            # If primary domains failed, try bato.si with Playwright (only on first page)
            if page == 1 and not all_results:
                print("Primary domains failed. Trying bato.si with Playwright...")
                bato_si_results, _ = _search_bato_si_playwright(query, page=1)
                if bato_si_results:
                    return bato_si_results
            print(f"Could not fetch search results for page {page}. Stopping.")
            break

        soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

        page_results_found = False # Flag to check if any new results were found on this page
        for item in soup.find_all('div', class_='item-text'):
            title_element = item.find('a', class_='item-title')
            if title_element:
                title = title_element.text.strip()
                # Handle Unicode characters and HTML entities
                title = html.unescape(title)
                title = re.sub(r'[^\x00-\x7F]+', '', title)  # Remove non-ASCII
                url = current_domain + title_element['href']

                # Extract latest chapter info and language
                latest_chapter = None
                release_date = None
                language = None

                # Find the parent container that has both item-text and item-volch
                parent = item.parent
                if parent:
                    volch_div = parent.find('div', class_='item-volch')
                    if volch_div:
                        # Get chapter link
                        chapter_link = volch_div.find('a', class_='visited')
                        if chapter_link:
                            latest_chapter = chapter_link.text.strip()

                        # Get release date
                        date_element = volch_div.find('i')
                        if date_element:
                            release_date = date_element.text.strip()

                    # Extract language from flag element
                    flag_element = parent.find('em', class_='item-flag')
                    if flag_element and flag_element.get('data-lang'):
                        language = flag_element.get('data-lang')

                if url not in seen_urls: # Check if URL is already seen
                    all_results.append({
                        'title': title,
                        'url': url,
                        'latest_chapter': latest_chapter,
                        'release_date': release_date,
                        'language': language
                    })
                    seen_urls.add(url)
                    page_results_found = True
        
        if not page_results_found: # If no new results were found on this page
            print(f"No new results found on page {page}. Stopping search.")
            break
        
        page += 1
        time.sleep(1)
    return all_results


def _search_bato_si_playwright(query, page=1):
    """Search bato.si using Playwright (required due to JS rendering). Returns results for a single page."""
    import html
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright is not installed. Cannot search bato.si.")
        print("Install with: pip install playwright && playwright install")
        return [], False  # results, has_next_page
    
    results = []
    has_next_page = False
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            
            bpage = context.new_page()
            
            search_url = f"https://bato.si/v4x-search?type=comic&word={quote(query)}&page={page}"
            print(f"[bato.si] Searching page {page}: {search_url}")
            bpage.goto(search_url, timeout=60000)
            
            # Wait for search results
            try:
                bpage.wait_for_selector(
                    "div.flex.border-b.border-b-base-200.pb-5",
                    timeout=30000
                )
            except Exception:
                print(f"[bato.si] No results found on page {page}.")
                browser.close()
                return [], False
            
            # Extract results
            cards = bpage.query_selector_all("div.flex.border-b.border-b-base-200.pb-5")
            print(f"[bato.si] Found {len(cards)} results on page {page}")
            
            for card in cards:
                title_el = card.query_selector("h3 a[href^='/title/']")
                title = title_el.inner_text().strip() if title_el else "N/A"
                title = html.unescape(title)
                title = re.sub(r'[^\x00-\x7F]+', '', title)
                
                manga_href = title_el.get_attribute("href") if title_el else None
                manga_url = f"https://bato.si{manga_href}" if manga_href else None
                
                chap_el = card.query_selector("a[href*='-ch_']")
                latest_chapter = chap_el.inner_text().strip() if chap_el else None
                
                # Extract authors from author links
                authors = []
                author_links = card.query_selector_all("a[href^='/author']")
                for author_link in author_links:
                    author_name = author_link.inner_text().strip()
                    if author_name:
                        authors.append(author_name)
                
                # Extract description from first line-clamp-2 div
                description = None
                desc_divs = card.query_selector_all("div.text-xs.opacity-80.line-clamp-2")
                if desc_divs and len(desc_divs) > 0:
                    desc_text = desc_divs[0].inner_text().strip()
                    if desc_text:
                        description = desc_text[:100] + "..." if len(desc_text) > 100 else desc_text
                
                if manga_url:
                    results.append({
                        'title': title,
                        'url': manga_url,
                        'latest_chapter': latest_chapter,
                        'release_date': None,
                        'authors': authors,
                        'description': description
                    })
            
            # Check if next page exists
            next_page_link = bpage.query_selector(f"a[href*='page={page + 1}']")
            has_next_page = next_page_link is not None
            
            browser.close()
            
    except Exception as e:
        print(f"[bato.si] Error during Playwright search: {e}")
        return [], False
    
    return results, has_next_page

def get_manga_info(series_url):
    import html
    from urllib.parse import urlparse
    
    # Determine base URL from the series URL
    parsed_url = urlparse(series_url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    response = requests.get(series_url)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

    # Logic for bato.si (different HTML structure)
    if 'bato.si' in base_url:
        try:
            # Title
            # Look for h3 with specific classes usually found in bato.si (Tailwind)
            manga_title_element = soup.select_one('h3.text-lg.md\\:text-2xl.font-bold a')
            manga_title = manga_title_element.text.strip() if manga_title_element else "Unknown Title"
            manga_title = html.unescape(manga_title)
            manga_title = re.sub(r'[^\x00-\x7F]+', '', manga_title).strip()

            # --- Extract Metadata ---
            metadata = {
                'authors': [],
                'artists': [],
                'genres': [],
                'status': None,
                'summary': None
            }
            
            # Authors/Artists (bato.si often groups them or links them similarly)
            # Find div containing author links
            # Selector approximation based on user snippet: div with mt-2 containing /author links
            # User snippet: <div class="mt-2 text-sm md:text-base opacity-80" ...>
            author_container = soup.select_one('div.mt-2.text-sm.md\\:text-base.opacity-80')
            if author_container:
                for link in author_container.find_all('a', href=True):
                    if '/author' in link['href']:
                        text = link.text.strip()
                        # Simple heuristic to separate if marked? User ex: "G Yu(Art)"
                        if '(Art)' in text or '(Artist)' in text:
                            metadata['artists'].append(text)
                        else:
                            metadata['authors'].append(text)

            # Genres
            # Look for "Genres:" bold text
            genres_b = soup.find('b', string=lambda t: t and 'Genres:' in t)
            if genres_b and genres_b.parent:
                # User snippet: <span q:key="manhwa"><span class="whitespace-nowrap font-bold">Manhwa</span>...</span>
                # The genres seem to be in spans inside the parent div
                # We want the text inside the spans that are not commas or "Genres:"
                # A safe bet is to iterate children and extract text from spans that define genres
                # The hierarchy is a bit complex in the snippet.
                # Simplification: find all spans with class 'whitespace-nowrap' inside the parent container?
                genre_container = genres_b.parent
                # Find direct or nested spans that have text and aren't commas
                potential_genres = genre_container.select('span.whitespace-nowrap')
                metadata['genres'] = [g.text.strip() for g in potential_genres]

            # Status
            # Look for "Bato Upload Status:"
            status_div = soup.find(lambda tag: tag.name == 'div' and ('Bato Status:' in tag.text or 'Bato Upload Status:' in tag.text))
            if status_div:
                status_span = status_div.select_one('span.font-bold')
                if status_span:
                    metadata['status'] = status_span.text.strip()

            # Summary
            # <div class="limit-html prose lg:prose-lg"><div class="limit-html-p">
            summary_div = soup.select_one('.limit-html')
            if summary_div:
                metadata['summary'] = summary_div.text.strip()

            # Chapters
            chapters = []
            # User snippet: <div data-name="chapter-list" ...>
            chapter_list_div = soup.select_one('div[data-name="chapter-list"]')
            if chapter_list_div:
                 # Find links. The user snippet shows links like:
                 # <a href="/title/..." class="link-hover link-primary visited:text-accent">Chapter 13</a>
                 # We can select 'a' tags that have 'ch_' in href or just all links in this list that point to a title
                 
                 links = chapter_list_div.select('a.link-hover.link-primary')
                 for link in links:
                     href = link.get('href')
                     # Ensure href is a string and matches pattern
                     if isinstance(href, str) and '/title/' in href and not '/u/' in href:
                         c_title = link.text.strip()
                         c_title = html.unescape(c_title)
                         c_title = re.sub(r'[^\x00-\x7F]+', '', c_title).strip()
                         c_url = base_url + href if href.startswith('/') else href
                         chapters.append({'title': c_title, 'url': c_url})
            
            # Reverse for consistency (oldest first? or just follow site order usually desc)
            # Existing logic reverses them, assuming site lists new first. Bato.si snippet shows Ch 13, 12... so yes.
            chapters.reverse()
            
            return manga_title, chapters, metadata

        except Exception as e:
            print(f"Error parsing bato.si info: {e}")
            # Fallthrough might crash if variables aren't set, so return empty or raise
            return "Error Parsing", [], {}

    manga_title_element = soup.find('h3', class_='item-title')
    manga_title = manga_title_element.text.strip() if manga_title_element else "Unknown Title"
    
    # Properly decode HTML entities and handle Unicode for console display
    manga_title = html.unescape(manga_title)
    
    # Remove or replace problematic Unicode characters for console display
    # Keep only ASCII characters and common Unicode that displays well
    manga_title = re.sub(r'[^\x00-\x7F]+', '', manga_title)
    manga_title = manga_title.strip()

    # --- Extract Metadata ---
    metadata = {
        'authors': [],
        'artists': [],
        'genres': [],
        'status': None,
        'summary': None
    }

    try:
        # Authors
        authors_div = soup.find('div', class_='attr-item', string=lambda text: text and 'Authors:' in text)
        if authors_div: # Sometimes the text is inside b tag
             authors_span = authors_div.find('span')
             if authors_span:
                 metadata['authors'] = [a.text.strip() for a in authors_span.find_all('a')]
        else: # Try finding b tag
             authors_b = soup.find('b', class_='text-muted', string='Authors:')
             if authors_b and authors_b.parent:
                 authors_span = authors_b.parent.find('span')
                 if authors_span:
                     metadata['authors'] = [a.text.strip() for a in authors_span.find_all('a')]

        # Artists
        artists_div = soup.find('div', class_='attr-item', string=lambda text: text and 'Artists:' in text)
        if artists_div:
            artists_span = artists_div.find('span')
            if artists_span:
                metadata['artists'] = [a.text.strip() for a in artists_span.find_all('a')]
        else:
             artists_b = soup.find('b', class_='text-muted', string='Artists:')
             if artists_b and artists_b.parent:
                 artists_span = artists_b.parent.find('span')
                 if artists_span:
                     metadata['artists'] = [a.text.strip() for a in artists_span.find_all('a')]

        # Genres
        genres_div = soup.find('div', class_='attr-item', string=lambda text: text and 'Genres:' in text)
        if genres_div:
             genres_span = genres_div.find('span')
             if genres_span:
                 metadata['genres'] = [span.text.strip() for span in genres_span.find_all('span')]
        else:
             genres_b = soup.find('b', class_='text-muted', string='Genres:')
             if genres_b and genres_b.parent:
                 genres_span = genres_b.parent.find('span')
                 if genres_span:
                     # Genres can be in span, u, b tags
                     metadata['genres'] = [el.text.strip() for el in genres_span.find_all(['span', 'u', 'b'])]

        # Status (Upload status)
        status_div = soup.find('div', class_='attr-item', string=lambda text: text and 'Upload status:' in text)
        if status_div:
            status_span = status_div.find('span')
            if status_span:
                metadata['status'] = status_span.text.strip()
        else:
             status_b = soup.find('b', class_='text-muted', string='Upload status:')
             if status_b and status_b.parent:
                 status_span = status_b.parent.find('span')
                 if status_span:
                     metadata['status'] = status_span.text.strip()

        # Summary
        summary_div = soup.find('div', class_='limit-html')
        if summary_div:
            metadata['summary'] = summary_div.text.strip()
            
    except Exception as e:
        print(f"Warning: Error extracting metadata: {e}")

    chapters = []
    
    # Find all chapter links
    chapter_elements = soup.find_all('a', class_='chapt')
    for chapter_element in chapter_elements:
        chapter_title = chapter_element.text.strip()
        chapter_title = html.unescape(chapter_title)
        # Remove non-ASCII characters from chapter titles too
        chapter_title = re.sub(r'[^\x00-\x7F]+', '', chapter_title)
        chapter_url = base_url + chapter_element['href']
        chapters.append({'title': chapter_title, 'url': chapter_url})
    
    # Reverse the order of chapters so that Chapter 1 is listed first
    chapters.reverse()
    
    return manga_title, chapters, metadata

def convert_chapter_to_pdf(chapter_dir, delete_images=False):
    from PIL import Image

    image_files = [os.path.join(chapter_dir, f) for f in os.listdir(chapter_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    image_files.sort(key=lambda f: int(match.group(1)) if (match := re.search(r'page_(\d+)', os.path.basename(f))) else 0)

    if not image_files:
        print(f"No images found in {chapter_dir} to convert to PDF.")
        return None

    pdf_path = chapter_dir + ".pdf"
    
    try:
        images = []
        for img_file in image_files:
            try:
                img = Image.open(img_file).convert("RGB")
                images.append(img)
            except Exception as e:
                print(f"Error opening image {img_file}: {e}")
                continue
        
        if images:
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            print(f"Successfully created PDF: {pdf_path}")

            if delete_images:
                for img_file in image_files:
                    try:
                        os.remove(img_file)
                    except Exception as e:
                        print(f"Error deleting image {img_file}: {e}")
                try:
                    os.rmdir(chapter_dir) # Remove the directory if it's empty
                    print(f"Deleted image directory: {chapter_dir}")
                except OSError as e:
                    print(f"Could not delete directory {chapter_dir}: {e}")
            return pdf_path
        else:
            print(f"No valid images to convert to PDF in {chapter_dir}.")
            return None
    except Exception as e:
        print(f"Error creating PDF for {chapter_dir}: {e}")
        return None

def _create_comic_info_xml(manga_title, chapter_title, metadata=None):
    """Create ComicInfo.xml content as a string."""
    
    # Basic XML structure
    root = ET.Element("ComicInfo")
    
    # Add Series
    series = ET.SubElement(root, "Series")
    series.text = manga_title
    
    # Add Title
    title = ET.SubElement(root, "Title")
    title.text = chapter_title
    
    # Extract chapter number from title
    match = re.search(r'Ch\.(\d+(\.\d+)?)', chapter_title, re.IGNORECASE)
    if match:
        number = ET.SubElement(root, "Number")
        number.text = match.group(1)
    
    if metadata:
        if metadata.get('summary'):
            summary = ET.SubElement(root, "Summary")
            summary.text = metadata['summary']
        
        if metadata.get('authors'):
            writer = ET.SubElement(root, "Writer")
            writer.text = ', '.join(metadata['authors'])
            
        if metadata.get('artists'):
            penciller = ET.SubElement(root, "Penciller")
            penciller.text = ', '.join(metadata['artists'])
            
        if metadata.get('genres'):
            genre = ET.SubElement(root, "Genre")
            genre.text = ', '.join(metadata['genres'])
            
    # Add a note
    notes = ET.SubElement(root, "Notes")
    notes.text = "Generated by Bato-Downloader"
    
    # Pretty print the XML
    xml_str = ET.tostring(root, 'utf-8')
    pretty_xml_str = minidom.parseString(xml_str).toprettyxml(indent="  ")
    
    return pretty_xml_str

def convert_chapter_to_cbz(chapter_dir, manga_title, chapter_title, delete_images=False, metadata=None):
    """Convert chapter images to CBZ (ZIP) comic book archive."""
    image_files = [os.path.join(chapter_dir, f) for f in os.listdir(chapter_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    image_files.sort(key=lambda f: int(match.group(1)) if (match := re.search(r'page_(\d+)', os.path.basename(f))) else 0)

    if not image_files:
        print(f"No images found in {chapter_dir} to convert to CBZ.")
        return None

    cbz_path = chapter_dir + ".cbz"

    try:
        # Create ComicInfo.xml
        comic_info_xml = _create_comic_info_xml(manga_title, chapter_title, metadata)

        with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz_file:
            # Add ComicInfo.xml to the archive
            cbz_file.writestr("ComicInfo.xml", comic_info_xml)
            print("Added ComicInfo.xml to CBZ archive")

            for img_file in image_files:
                # Add files to ZIP with just the filename (not full path)
                arcname = os.path.basename(img_file)
                cbz_file.write(img_file, arcname)
                print(f"Added {arcname} to CBZ archive")

        print(f"Successfully created CBZ: {cbz_path}")

        if delete_images:
            for img_file in image_files:
                try:
                    os.remove(img_file)
                except Exception as e:
                    print(f"Error deleting image {img_file}: {e}")
            try:
                os.rmdir(chapter_dir) # Remove the directory if it's empty
                print(f"Deleted image directory: {chapter_dir}")
            except OSError as e:
                print(f"Could not delete directory {chapter_dir}: {e}")
        return cbz_path
    except Exception as e:
        print(f"Error creating CBZ for {chapter_dir}: {e}")
        return None

def sanitize_filename(name: str) -> str:
    """Sanitize filename to remove invalid Windows characters and normalize spaces."""
    if not name:
        return "untitled"

    # Remove characters that are invalid in Windows file paths
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Handle Unicode by removing emoji and special characters that might cause issues
    # Preserve dots for decimal chapter numbers (e.g., 30.1, 30.2)
    name = re.sub(r'[^\w\s.\-]', '', name)
    # Replace spaces with underscores and remove multiple underscores
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    # Remove trailing dots, which are invalid in Windows folder names
    return name.rstrip('.')

def download_chapter(chapter_url, manga_title, chapter_title, output_dir=".", stop_event=None, convert_to_pdf=False, convert_to_cbz=False, keep_images=True, max_workers=15, metadata=None):
    if stop_event and stop_event.is_set():
        return # Stop early if signal is already set

    response = requests.get(chapter_url)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

    # Sanitize both manga_title and chapter_title for use in file paths
    sanitized_manga_title = sanitize_filename(manga_title)
    sanitized_chapter_title = sanitize_filename(chapter_title)

    chapter_dir = os.path.join(output_dir, sanitized_manga_title, sanitized_chapter_title)
    os.makedirs(chapter_dir, exist_ok=True)

    image_urls = []
    script_tags = soup.find_all('script')
    for script in script_tags:
        if 'imgHttps' in script.text:
            match = re.search(r'imgHttps = (\[.*?\]);', script.text)
            if match:
                try:
                    image_urls = json.loads(match.group(1))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from script tag: {e}")
                break

    if not image_urls:
        # Fallback for bato.si style (Qwik app structure)
        # Look for div with data-name="image-item" containing an img
        img_elements = soup.select('div[data-name="image-item"] img')
        if img_elements:
             # Using print in a thread-safe way might be tricky here as it's not inside the lock, 
             # but download_chapter is called from a thread. 
             # However, this print is useful for debugging. 
             # The existing code prints normally so I will follow that pattern.
             image_urls = [img.get('src') for img in img_elements if img.get('src')]
    
    if not image_urls and 'bato.si' in chapter_url:
        print(f"Trying to fetch images with Playwright for bato.si: {chapter_url}")
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(chapter_url, timeout=60000) # Increased timeout
                
                # Wait for at least one image to appear
                try:
                    page.wait_for_selector('div[data-name="image-item"] img', timeout=30000)
                except Exception as e:
                     print(f"Playwright wait for selector failed: {e}")

                # Extract all image srcs
                imgs = page.query_selector_all('div[data-name="image-item"] img')
                for img in imgs:
                    src = img.get_attribute('src')
                    if src:
                        image_urls.append(src)
                
                browser.close()
                print(f"Successfully extracted {len(image_urls)} images using Playwright.")

        except ImportError:
             print("Playwright is not installed. Please install it with 'pip install playwright' and 'playwright install' to support bato.si downloads.")
        except Exception as e:
            print(f"Error using Playwright to fetch images: {e}")

    if not image_urls:
        print(f"No image URLs found for {chapter_title} at {chapter_url}.")
        dump_file_path = os.path.join(chapter_dir, f"{sanitized_chapter_title}_dump.html")
        with open(dump_file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))
        print(f"Full HTML content dumped to {dump_file_path} for inspection.")
        return

    # Use a lock for thread-safe printing
    print_lock = threading.Lock()

    def download_image(img_url, index):
        if stop_event and stop_event.is_set():
            return # Stop early if signal is set

        if img_url and img_url.startswith('http'):
            try:
                # Helper to detect potential "k" to "n" host switch candidates
                def looks_like_broken_batoto_url(u):
                    return isinstance(u, str) and '//k' in u and '.mb' in u
                
                def replace_k_with_n(u):
                    return u.replace('//k', '//n') if isinstance(u, str) else u

                img_response = requests.get(img_url)
                
                # Check for 5xx/4xx errors and try fallback host if applicable
                if not img_response.ok and looks_like_broken_batoto_url(img_url):
                    fallback_url = replace_k_with_n(img_url)
                    with print_lock:
                         print(f"Warning: {img_url} returned {img_response.status_code}. Retrying with fallback: {fallback_url}")
                    img_response = requests.get(fallback_url)
                
                # Raise error if both failed or if original failed and no fallback was applicable
                img_response.raise_for_status()
                
                img_data = img_response.content
                img_extension = img_url.split('.')[-1].split('?')[0]
                img_path = os.path.join(chapter_dir, f"page_{index+1}.{img_extension}")
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                with print_lock:
                    print(f"Downloaded {img_url} to {chapter_dir}")
            except Exception as e:
                with print_lock:
                    print(f"Error downloading {img_url}: {e}")

    # Use ThreadPoolExecutor for concurrent downloads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_image, img_url, i) for i, img_url in enumerate(image_urls)]
        for future in futures:
            future.result() # Ensure all images are downloaded before proceeding

    # Handle conversions
    if convert_to_pdf:
        print(f"Converting {chapter_title} to PDF...")
        pdf_file = convert_chapter_to_pdf(chapter_dir, delete_images=not keep_images)
        if pdf_file:
            print(f"PDF created: {pdf_file}")
        else:
            print(f"Failed to create PDF for {chapter_title}.")

    if convert_to_cbz:
        print(f"Converting {chapter_title} to CBZ...")
        cbz_file = convert_chapter_to_cbz(chapter_dir, manga_title, chapter_title, delete_images=not keep_images, metadata=metadata)
        if cbz_file:
            print(f"CBZ created: {cbz_file}")
        else:
            print(f"Failed to create CBZ for {chapter_title}.")
