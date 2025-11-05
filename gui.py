import customtkinter as ctk
import threading
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox, filedialog
from bato_scraper import get_manga_info, download_chapter, search_manga
import os
import re

# Language code to full name mapping
LANGUAGE_NAMES = {
    'en': 'English',
    'id': 'Indonesian',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'tr': 'Turkish',
    'pl': 'Polish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'no': 'Norwegian',
    'da': 'Danish',
    'fi': 'Finnish',
}

class BatoScraperGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bato.to Manga Scraper")
        self.geometry("800x700")
        self.resizable(True, True)

        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # --- Input Frame ---
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=3)
        self.input_frame.grid_columnconfigure(2, weight=1)

        self.url_label = ctk.CTkLabel(self.input_frame, text="Series URL:")
        self.url_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.url_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter Bato.to series URL")
        self.url_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.info_button = ctk.CTkButton(self.input_frame, text="Get Info", command=self.get_info_thread)
        self.info_button.grid(row=0, column=2, padx=10, pady=5, sticky="e")

        self.search_label = ctk.CTkLabel(self.input_frame, text="Search Query:")
        self.search_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.search_entry = ctk.CTkEntry(self.input_frame, placeholder_text="Enter manga title to search")
        self.search_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.search_button = ctk.CTkButton(self.input_frame, text="Search", command=self.search_manga_thread)
        self.search_button.grid(row=1, column=2, padx=10, pady=5, sticky="e")

        # --- Action Buttons Frame ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.action_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.list_chapters_button = ctk.CTkButton(self.action_frame, text="List Chapters", command=self.list_chapters_thread)
        self.list_chapters_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.download_all_button = ctk.CTkButton(self.action_frame, text="Download All", command=self.download_all_thread)
        self.download_all_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.download_range_button = ctk.CTkButton(self.action_frame, text="Download Range", command=self.download_range_thread)
        self.download_range_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.output_dir_button = ctk.CTkButton(self.action_frame, text="Select Output Dir", command=self.select_output_directory)
        self.output_dir_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        self.stop_downloads_button = ctk.CTkButton(self.action_frame, text="Stop All Downloads", command=self.stop_all_downloads, fg_color="red")
        self.stop_downloads_button.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.convert_pdf_checkbox = ctk.CTkCheckBox(self.action_frame, text="Convert to PDF")
        self.convert_pdf_checkbox.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.convert_pdf_checkbox.bind("<Button-1>", self.toggle_keep_images_checkbox)

        self.convert_cbz_checkbox = ctk.CTkCheckBox(self.action_frame, text="Convert to CBZ")
        self.convert_cbz_checkbox.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
        self.convert_cbz_checkbox.bind("<Button-1>", self.toggle_keep_images_checkbox)

        self.keep_images_checkbox = ctk.CTkCheckBox(self.action_frame, text="Keep Images (with PDF/CBZ)")
        self.keep_images_checkbox.grid(row=1, column=3, padx=10, pady=10, sticky="ew")
        self.keep_images_checkbox.configure(state="disabled") # Initially disabled

        self.settings_button = ctk.CTkButton(self.action_frame, text="Settings", command=self.open_settings)
        self.settings_button.grid(row=1, column=4, padx=10, pady=10, sticky="ew")

        self.output_dir_label = ctk.CTkLabel(self.action_frame, text=f"Output: {os.getcwd()}")
        self.output_dir_label.grid(row=2, column=0, columnspan=5, padx=10, pady=5, sticky="w")
        self.output_directory = os.getcwd() # Default output directory

        # --- Progress Bar ---
        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal")
        self.progress_bar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)

        # --- Output Text Area ---
        self.output_text = ctk.CTkTextbox(self, wrap="word")
        self.output_text.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.output_text.insert("end", "Welcome to Bato.to Manga Scraper GUI!\n")
        self.output_text.configure(state="disabled") # Make it read-only

        # --- Selection Input Frame (hidden by default) ---
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.selection_frame.grid_columnconfigure(1, weight=1)
        self.selection_frame.grid_remove() # Hide initially

        self.selection_label = ctk.CTkLabel(self.selection_frame, text="Enter selection number:")
        self.selection_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.selection_entry = ctk.CTkEntry(self.selection_frame, placeholder_text="Enter number or 0 to cancel")
        self.selection_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        self.selection_button = ctk.CTkButton(self.selection_frame, text="Select", command=self.process_selection)
        self.selection_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

        self.manga_title = None
        self.chapters = []
        self.download_executor = None # To hold the ThreadPoolExecutor
        self.stop_downloads_flag = threading.Event() # Event to signal stopping downloads
        self.max_image_workers = 15 # Default value for concurrent image downloads
        self.search_results = None # Store search results for selection

    def toggle_keep_images_checkbox(self, event):
        # This function is called when the convert_pdf_checkbox or convert_cbz_checkbox is clicked
        if self.convert_pdf_checkbox.get() == 1 or self.convert_cbz_checkbox.get() == 1: # If any conversion is enabled
            self.keep_images_checkbox.configure(state="normal")
        else:
            self.keep_images_checkbox.configure(state="disabled")
            self.keep_images_checkbox.deselect() # Uncheck if no conversion is enabled

    def log_message(self, message):
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message + "\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")

    def select_output_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory = directory
            self.output_dir_label.configure(text=f"Output: {self.output_directory}")
            self.log_message(f"Output directory set to: {self.output_directory}")

    def get_info_thread(self):
        series_url = self.url_entry.get().strip()
        if not series_url:
            messagebox.showerror("Input Error", "Please enter a series URL.")
            return
        self.log_message(f"Fetching info for: {series_url}")
        self.progress_bar.set(0)
        threading.Thread(target=self._get_info, args=(series_url,)).start()

    def _get_info(self, series_url):
        try:
            self.manga_title, self.chapters = get_manga_info(series_url)
            if self.manga_title and self.chapters:
                self.log_message(f"Manga Title: {self.manga_title}")
                self.log_message(f"Found {len(self.chapters)} chapters.")
            else:
                self.log_message("Could not retrieve manga title or chapters. Check URL.")
        except Exception as e:
            self.log_message(f"Error fetching info: {e}")
        finally:
            self.progress_bar.set(1)

    def list_chapters_thread(self):
        if not self.chapters:
            messagebox.showinfo("Info", "Please get manga info first using 'Get Info' or 'Search' and selecting a series.")
            return
        self.log_message("\n--- Chapters ---")
        for i, chapter in enumerate(self.chapters):
            self.log_message(f"{i+1}. {chapter['title']} ({chapter['url']})")

    def search_manga_thread(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showerror("Input Error", "Please enter a search query.")
            return
        self.log_message(f"Searching for: {query}")
        self.progress_bar.set(0)
        threading.Thread(target=self._search_manga, args=(query,)).start()

    def _search_manga(self, query):
        try:
            results = search_manga(query)
            if results:
                self.log_message(f"\n--- Search Results for '{query}' ---\n")
                
                for i, manga in enumerate(results):
                    self.log_message(f"[{i+1}] {manga['title']}")
                    
                    # Add language on separate line
                    if manga.get('language'):
                        lang_name = LANGUAGE_NAMES.get(manga['language'], manga['language'].capitalize())
                        self.log_message(f"    🌐 Language: {lang_name}")
                    else:
                        self.log_message(f"    🌐 Language: English (probably)")
                    
                    self.log_message(f"    🔗 {manga['url']}")
                    
                    # Display latest chapter and release date if available
                    if manga.get('latest_chapter') or manga.get('release_date'):
                        chapter_info = []
                        if manga.get('latest_chapter'):
                            chapter_info.append(f"Latest: {manga['latest_chapter']}")
                        if manga.get('release_date'):
                            chapter_info.append(f"Released: {manga['release_date']}")
                        self.log_message(f"    📖 {' • '.join(chapter_info)}")
                    
                    self.log_message("")
                
                # Store results and show selection input
                self.search_results = results
                self.log_message("Enter the number of the series you want to select, or 0 to cancel:")
                self.selection_frame.grid() # Show the selection input frame
                self.selection_entry.delete(0, ctk.END)
                self.selection_entry.focus_set()
            else:
                self.log_message(f"No results found for '{query}'.")
        except Exception as e:
            self.log_message(f"Error during search: {e}")
        finally:
            self.progress_bar.set(1)

    def process_selection(self):
        if not self.search_results:
            return
        
        try:
            selection_text = self.selection_entry.get().strip()
            selection = int(selection_text)
            
            if 1 <= selection <= len(self.search_results):
                selected_manga = self.search_results[selection - 1]
                self.url_entry.delete(0, ctk.END)
                self.url_entry.insert(0, selected_manga['url'])
                self.log_message(f"Selected: {selected_manga['title']}. URL set in Series URL field.")
                self.log_message("Fetching info for selected manga...")
                self.selection_frame.grid_remove() # Hide the selection frame
                self.search_results = None
                self.get_info_thread() # Automatically get info for the selected manga
            elif selection == 0:
                self.log_message("Search selection cancelled.")
                self.selection_frame.grid_remove()
                self.search_results = None
            else:
                self.log_message("Invalid selection. Please enter a valid number.")
        except ValueError:
            self.log_message("Invalid input. Please enter a number.")

    def download_all_thread(self):
        if not self.chapters:
            messagebox.showinfo("Info", "Please get manga info first using 'Get Info' or 'Search' and selecting a series.")
            return
        self.log_message("\n--- Downloading all chapters ---")
        self.progress_bar.set(0)
        threading.Thread(target=self._download_chapters, args=(self.chapters,)).start()

    def download_range_thread(self):
        if not self.chapters:
            messagebox.showinfo("Info", "Please get manga info first using 'Get Info' or 'Search' and selecting a series.")
            return
        
        range_input = ctk.CTkInputDialog(text="Enter chapter range (e.g., 1-10):", title="Download Range")
        chapter_range_str = range_input.get_input()

        if not chapter_range_str:
            self.log_message("Download range cancelled.")
            return

        try:
            start_chap_str, end_chap_str = chapter_range_str.split('-')
            start_chap = int(start_chap_str)
            end_chap = int(end_chap_str)

            if not (1 <= start_chap <= len(self.chapters) and 1 <= end_chap <= len(self.chapters) and start_chap <= end_chap):
                messagebox.showerror("Input Error", "Invalid chapter range. Please enter valid numbers within the available range.")
                return

            chapters_to_download = self.chapters[start_chap - 1:end_chap]
            self.log_message(f"\n--- Downloading chapters {start_chap} to {end_chap} ---")
            self.progress_bar.set(0)
            threading.Thread(target=self._download_chapters, args=(chapters_to_download,)).start()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid range format. Use 'start-end' (e.g., '1-10').")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def _download_chapters(self, chapters_to_download):
        total_chapters = len(chapters_to_download)
        
        # Use a lock for thread-safe GUI updates
        gui_update_lock = threading.Lock()

        def download_single_chapter(chapter, index):
            if self.stop_downloads_flag.is_set():
                with gui_update_lock:
                    self.log_message(f"Skipping {chapter['title']} (download stopped).")
                return

            with gui_update_lock:
                self.log_message(f"Downloading {chapter['title']}...")
            try:
                convert_to_pdf = self.convert_pdf_checkbox.get() == 1
                convert_to_cbz = self.convert_cbz_checkbox.get() == 1
                keep_images = self.keep_images_checkbox.get() == 1
                download_chapter(chapter['url'], self.manga_title, chapter['title'], self.output_directory, self.stop_downloads_flag, convert_to_pdf, convert_to_cbz, keep_images, self.max_image_workers)
                if not self.stop_downloads_flag.is_set(): # Only update progress if not stopped
                    with gui_update_lock:
                        self.update_progress(index + 1, total_chapters)
            except Exception as e:
                if not self.stop_downloads_flag.is_set(): # Only log error if not stopped by user
                    with gui_update_lock:
                        self.log_message(f"Error downloading {chapter['title']}: {e}")

        # Use ThreadPoolExecutor for concurrent chapter downloads
        # Re-initialize executor to ensure a clean state for stopping
        if self.download_executor:
            self.download_executor.shutdown(wait=False, cancel_futures=True)
        self.download_executor = ThreadPoolExecutor(max_workers=self.max_concurrent_downloads)
        self.stop_downloads_flag.clear() # Clear the stop flag for a new download session

        futures = []
        for i, chapter in enumerate(chapters_to_download):
            if self.stop_downloads_flag.is_set():
                self.log_message("Download stopped by user before starting all chapters.")
                break
            futures.append(self.download_executor.submit(download_single_chapter, chapter, i))
        
        # Wait for all futures to complete, or until stop flag is set
        for future in futures:
            try:
                # Use a timeout or check stop_downloads_flag more frequently if futures are very long-running
                future.result()
            except Exception as e:
                # Handle exceptions from cancelled futures or other errors
                pass
            if self.stop_downloads_flag.is_set():
                # If stop is pressed, cancel remaining futures and break
                for f in futures:
                    f.cancel()
                break

        self.download_executor.shutdown(wait=True) # Ensure all threads are properly shut down
        if not self.stop_downloads_flag.is_set():
            self.log_message("\nAll selected chapters downloaded (or attempted).")
            self.progress_bar.set(1) # Ensure progress bar is full at the end
        else:
            self.log_message("\nDownloads stopped by user.")
            self.progress_bar.set(0) # Reset progress bar if stopped

    def update_progress(self, current, total):
        progress_value = current / total
        self.progress_bar.set(progress_value)
        self.update_idletasks() # Update the GUI immediately

    def stop_all_downloads(self):
        if self.download_executor:
            self.stop_downloads_flag.set() # Signal threads to stop
            self.log_message("Stopping all active downloads...")
        else:
            self.log_message("No active downloads to stop.")

    def open_settings(self):
        settings_window = ctk.CTkToplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("500x300")
        settings_window.transient(self) # Make it appear on top of the main window
        settings_window.grab_set() # Make it modal

        # Max Concurrent Chapter Downloads Setting
        ctk.CTkLabel(settings_window, text="Max Concurrent Chapter Downloads:").pack(pady=10)
        self.max_downloads_slider = ctk.CTkSlider(settings_window, from_=1, to=10, number_of_steps=9)
        self.max_downloads_slider.set(self.max_concurrent_downloads) # Set current value
        self.max_downloads_slider.pack(pady=5)
        self.max_downloads_label = ctk.CTkLabel(settings_window, text=f"Value: {int(self.max_downloads_slider.get())}")
        self.max_downloads_label.pack(pady=5)
        self.max_downloads_slider.bind("<B1-Motion>", self._update_max_downloads_label)
        self.max_downloads_slider.bind("<ButtonRelease-1>", self._update_max_downloads_setting)

        # Max Concurrent Image Downloads Setting
        ctk.CTkLabel(settings_window, text="Max Concurrent Image Downloads:").pack(pady=10)
        self.max_image_downloads_slider = ctk.CTkSlider(settings_window, from_=5, to=30, number_of_steps=25)
        self.max_image_downloads_slider.set(self.max_image_workers) # Set current value
        self.max_image_downloads_slider.pack(pady=5)
        self.max_image_downloads_label = ctk.CTkLabel(settings_window, text=f"Value: {int(self.max_image_downloads_slider.get())}")
        self.max_image_downloads_label.pack(pady=5)
        self.max_image_downloads_slider.bind("<B1-Motion>", self._update_max_image_downloads_label)
        self.max_image_downloads_slider.bind("<ButtonRelease-1>", self._update_max_image_downloads_setting)

        # Close button
        ctk.CTkButton(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)

    def _update_max_downloads_label(self, event):
        self.max_downloads_label.configure(text=f"Value: {int(self.max_downloads_slider.get())}")

    def _update_max_downloads_setting(self, event):
        new_value = int(self.max_downloads_slider.get())
        if new_value != self.max_concurrent_downloads:
            self.max_concurrent_downloads = new_value
            self.log_message(f"Max concurrent downloads set to: {self.max_concurrent_downloads}")

    def _update_max_image_downloads_label(self, event):
        self.max_image_downloads_label.configure(text=f"Value: {int(self.max_image_downloads_slider.get())}")

    def _update_max_image_downloads_setting(self, event):
        new_value = int(self.max_image_downloads_slider.get())
        if new_value != self.max_image_workers:
            self.max_image_workers = new_value
            self.log_message(f"Max concurrent image downloads set to: {self.max_image_workers}")

def main_gui():
    ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
    app = BatoScraperGUI()
    app.max_concurrent_downloads = 3 # Default value for concurrent chapter downloads
    app.max_image_workers = 15 # Default value for concurrent image downloads
    app.mainloop()

if __name__ == "__main__":
    main_gui()
