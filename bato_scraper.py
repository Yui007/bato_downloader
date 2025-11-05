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

def search_manga(query, max_pages=5):
    import html
    
    all_results = []
    seen_urls = set() # Use a set to store unique URLs
    page = 1
    while page <= max_pages:
        search_url = f"https://bato.to/search?word={quote(query)}&page={page}"
        print(f"Searching page {page}: {search_url}")
        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching search page {page}: {e}")
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
                url = "https://bato.to" + title_element['href']
                
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

def get_manga_info(series_url):
    import html
    
    response = requests.get(series_url)
    soup = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

    manga_title_element = soup.find('h3', class_='item-title')
    manga_title = manga_title_element.text.strip() if manga_title_element else "Unknown Title"
    
    # Properly decode HTML entities and handle Unicode for console display
    manga_title = html.unescape(manga_title)
    
    # Remove or replace problematic Unicode characters for console display
    # Keep only ASCII characters and common Unicode that displays well
    manga_title = re.sub(r'[^\x00-\x7F]+', '', manga_title)
    manga_title = manga_title.strip()
    
    chapters = []
    
    # Find all chapter links
    chapter_elements = soup.find_all('a', class_='chapt')
    for chapter_element in chapter_elements:
        chapter_title = chapter_element.text.strip()
        chapter_title = html.unescape(chapter_title)
        # Remove non-ASCII characters from chapter titles too
        chapter_title = re.sub(r'[^\x00-\x7F]+', '', chapter_title)
        chapter_url = "https://bato.to" + chapter_element['href']
        chapters.append({'title': chapter_title, 'url': chapter_url})
    
    # Reverse the order of chapters so that Chapter 1 is listed first
    chapters.reverse()
    
    return manga_title, chapters

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

def convert_chapter_to_cbz(chapter_dir, delete_images=False):
    """Convert chapter images to CBZ (ZIP) comic book archive."""
    image_files = [os.path.join(chapter_dir, f) for f in os.listdir(chapter_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
    image_files.sort(key=lambda f: int(match.group(1)) if (match := re.search(r'page_(\d+)', os.path.basename(f))) else 0)

    if not image_files:
        print(f"No images found in {chapter_dir} to convert to CBZ.")
        return None

    cbz_path = chapter_dir + ".cbz"

    try:
        with zipfile.ZipFile(cbz_path, 'w', zipfile.ZIP_DEFLATED) as cbz_file:
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
    name = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores and remove multiple underscores
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    # Remove trailing dots, which are invalid in Windows folder names
    return name.rstrip('.')

def download_chapter(chapter_url, manga_title, chapter_title, output_dir=".", stop_event=None, convert_to_pdf=False, convert_to_cbz=False, keep_images=True, max_workers=15):
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
                img_data = requests.get(img_url).content
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
        cbz_file = convert_chapter_to_cbz(chapter_dir, delete_images=not keep_images)
        if cbz_file:
            print(f"CBZ created: {cbz_file}")
        else:
            print(f"Failed to create CBZ for {chapter_title}.")
