"""
Conversion utilities for PDF and CBZ formats with ComicInfo.xml support.
"""

import io
import os
import zipfile
from pathlib import Path
from typing import Optional, List
from xml.etree import ElementTree as ET

from PIL import Image, ImageFile

# Allow PIL to load slightly truncated/malformed images
# This fixes false-positive errors with certain CDN-served images
ImageFile.LOAD_TRUNCATED_IMAGES = True

from ..logger import get_logger
from ..scraper.info import MangaInfo
from ..scraper.chapters import Chapter


def get_image_files(folder: Path) -> List[Path]:
    """Get sorted list of image files in a folder."""
    extensions = {'.webp', '.jpg', '.jpeg', '.png', '.gif'}
    images = [
        f for f in folder.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    ]
    return sorted(images, key=lambda x: x.name)


def images_to_pdf(
    image_folder: str | Path,
    output_path: str | Path
) -> bool:
    """
    Convert images in a folder to a PDF file.
    
    Args:
        image_folder: Folder containing images
        output_path: Path for output PDF file
    
    Returns:
        True if successful, False otherwise
    """
    logger = get_logger()
    image_folder = Path(image_folder)
    output_path = Path(output_path)
    
    logger.debug(f"Converting to PDF: {image_folder} -> {output_path}")
    
    try:
        images = get_image_files(image_folder)
        
        if not images:
            logger.warning(f"No images found in {image_folder}")
            return False
        
        # Convert all images to RGB (required for PDF)
        pil_images = []
        for img_path in images:
            try:
                img = Image.open(img_path)
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                pil_images.append(img)
            except Exception as e:
                logger.warning(f"Failed to load image {img_path}: {e}")
        
        if not pil_images:
            logger.error("No valid images to convert")
            return False
        
        # Save as PDF
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        first_image = pil_images[0]
        if len(pil_images) > 1:
            first_image.save(
                output_path,
                "PDF",
                save_all=True,
                append_images=pil_images[1:]
            )
        else:
            first_image.save(output_path, "PDF")
        
        # Cleanup
        for img in pil_images:
            img.close()
        
        logger.debug(f"PDF created successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create PDF: {e}")
        return False


def generate_comic_info_xml(
    manga_info: Optional[MangaInfo],
    chapter: Optional[Chapter]
) -> str:
    """
    Generate ComicInfo.xml content for CBZ metadata.
    
    Args:
        manga_info: Manga information
        chapter: Chapter information
    
    Returns:
        XML string content
    """
    root = ET.Element("ComicInfo")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
    
    if manga_info:
        # Title
        title_elem = ET.SubElement(root, "Title")
        title_elem.text = manga_info.title
        
        # Series
        series_elem = ET.SubElement(root, "Series")
        series_elem.text = manga_info.title
        
        # Authors/Writers
        if manga_info.authors:
            writer_elem = ET.SubElement(root, "Writer")
            writer_elem.text = ", ".join(manga_info.authors)
        
        # Genres
        if manga_info.genres:
            genre_elem = ET.SubElement(root, "Genre")
            genre_elem.text = ", ".join(manga_info.genres)
        
        # Summary
        if manga_info.description:
            summary_elem = ET.SubElement(root, "Summary")
            summary_elem.text = manga_info.description
        
        # Web link
        web_elem = ET.SubElement(root, "Web")
        web_elem.text = manga_info.url
    
    if chapter:
        # Number
        number_elem = ET.SubElement(root, "Number")
        number_elem.text = chapter.number
        
        # Chapter title
        if chapter.title:
            chapter_title_elem = ET.SubElement(root, "StoryArc")
            chapter_title_elem.text = chapter.title
    
    # Format
    format_elem = ET.SubElement(root, "Manga")
    format_elem.text = "Yes"
    
    # Convert to string with proper XML declaration
    xml_string = ET.tostring(root, encoding='unicode')
    return f'<?xml version="1.0" encoding="utf-8"?>\n{xml_string}'


def images_to_cbz(
    image_folder: str | Path,
    output_path: str | Path,
    manga_info: Optional[MangaInfo] = None,
    chapter: Optional[Chapter] = None
) -> bool:
    """
    Convert images in a folder to a CBZ archive with ComicInfo.xml.
    
    Args:
        image_folder: Folder containing images
        output_path: Path for output CBZ file
        manga_info: Optional manga info for ComicInfo.xml
        chapter: Optional chapter info for ComicInfo.xml
    
    Returns:
        True if successful, False otherwise
    """
    logger = get_logger()
    image_folder = Path(image_folder)
    output_path = Path(output_path)
    
    logger.debug(f"Converting to CBZ: {image_folder} -> {output_path}")
    
    try:
        images = get_image_files(image_folder)
        
        if not images:
            logger.warning(f"No images found in {image_folder}")
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as cbz:
            # Add images
            for img_path in images:
                cbz.write(img_path, img_path.name)
            
            # Add ComicInfo.xml
            comic_info = generate_comic_info_xml(manga_info, chapter)
            cbz.writestr("ComicInfo.xml", comic_info)
        
        logger.debug(f"CBZ created successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create CBZ: {e}")
        return False


def cleanup_images(folder: Path) -> bool:
    """
    Remove image files from a folder after conversion.
    
    Args:
        folder: Folder to clean up
    
    Returns:
        True if successful
    """
    logger = get_logger()
    
    try:
        images = get_image_files(folder)
        for img in images:
            img.unlink()
        
        # Remove folder if empty
        if folder.exists() and not any(folder.iterdir()):
            folder.rmdir()
        
        logger.debug(f"Cleaned up images from: {folder}")
        return True
        
    except Exception as e:
        logger.warning(f"Failed to cleanup images: {e}")
        return False
