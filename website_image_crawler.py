#!/usr/bin/env python3
"""
Website Image Crawler

A tool that crawls websites, extracts images, and can follow links to a specified depth.
"""

import os
import re
import time
import random
import argparse
import urllib.parse
from urllib.parse import urlparse, urljoin
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebsiteImageCrawler:
    """Crawler that extracts images from websites and can follow links to a specified depth"""
    
    def __init__(self, save_dir="./crawled_images", max_images=100, formats=None, 
                 delay=1, user_agent=None, max_retries=3, verbose=False):
        """Initialize the crawler with configuration parameters
        
        Args:
            save_dir (str): Directory to save downloaded images
            max_images (int): Maximum number of images to download
            formats (list): List of image formats to download (e.g., ['jpg', 'png'])
            delay (float): Delay between requests to avoid rate limiting
            user_agent (str): Custom user agent string
            max_retries (int): Maximum number of retry attempts for failed requests
            verbose (bool): Enable verbose output
        """
        self.save_dir = save_dir
        self.max_images = max_images
        self.formats = formats
        self.delay = delay
        self.max_retries = max_retries
        self.verbose = verbose
        
        # Create a requests session for connection pooling
        self.session = requests.Session()
        
        # Set a realistic user agent if none provided
        if user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
            
        # Set headers for the session
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        })
        
        # Create output directory if it doesn't exist
        os.makedirs(self.save_dir, exist_ok=True)
        
        # Initialize tracking variables
        self.visited_urls = set()
        self.image_urls = set()
        self.pages_by_depth = {}
        self.downloaded_images = []
        
    def crawl(self, start_url, depth=1):
        """Crawl a website starting from the given URL up to the specified depth
        
        Args:
            start_url (str): Starting URL to crawl
            depth (int): Maximum depth of crawling
        
        Returns:
            tuple: (downloaded_images, visited_pages)
        """
        logger.info(f"Starting crawl from {start_url} with maximum depth {depth}")
        
        # Make sure the URL is properly formatted
        if not start_url.startswith(('http://', 'https://')):
            start_url = 'https://' + start_url
            
        # Track the pages at each depth
        self.pages_by_depth = {0: [start_url]}
        self.visited_urls.add(start_url)
        
        # Process each depth level
        for current_depth in range(depth + 1):
            logger.info(f"Processing depth {current_depth}")
            
            # Get pages for the current depth
            current_pages = self.pages_by_depth.get(current_depth, [])
            
            if not current_pages:
                logger.info(f"No pages to process at depth {current_depth}")
                break
                
            # Initialize the next depth's pages
            if current_depth < depth:
                self.pages_by_depth[current_depth + 1] = []
            
            # Process each page at the current depth
            for page_url in current_pages:
                logger.info(f"Processing page: {page_url}")
                
                # Extract images and links from the page
                html_content = self._fetch_url(page_url)
                if not html_content:
                    continue
                
                # Extract images from the page
                page_images = self._extract_images(html_content, page_url)
                self.image_urls.update(page_images)
                logger.info(f"Found {len(page_images)} images on {page_url}")
                
                # Extract links if we haven't reached maximum depth
                if current_depth < depth:
                    links = self._extract_links(html_content, page_url)
                    new_links = [link for link in links if link not in self.visited_urls]
                    
                    # Add to next depth and mark as visited
                    self.pages_by_depth[current_depth + 1].extend(new_links)
                    self.visited_urls.update(new_links)
                    
                    logger.info(f"Found {len(new_links)} new links on {page_url}")
                
                # Respect the site by waiting between requests
                time.sleep(self.delay)
        
        # Download all found images (up to max_images)
        image_list = list(self.image_urls)[:self.max_images]
        logger.info(f"Downloading up to {len(image_list)} images...")
        
        self.downloaded_images = self.download_images(image_list, self.formats)
        
        return {
            'downloaded_images': self.downloaded_images,
            'visited_pages': list(self.visited_urls),
            'total_images_found': len(self.image_urls)
        }
    
    def _fetch_url(self, url):
        """Fetch the content of a URL with retries
        
        Args:
            url (str): URL to fetch
            
        Returns:
            str or None: HTML content or None if failed
        """
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Error fetching {url} (attempt {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    # Exponential backoff with jitter
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(sleep_time)
        
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    def _extract_images(self, html_content, base_url):
        """Extract image URLs from HTML content
        
        Args:
            html_content (str): HTML content
            base_url (str): Base URL for resolving relative URLs
            
        Returns:
            set: Set of absolute image URLs
        """
        if not html_content:
            return set()
            
        soup = BeautifulSoup(html_content, 'html.parser')
        image_urls = set()
        
        # Extract from img tags
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                # Convert relative URLs to absolute
                abs_url = urljoin(base_url, src)
                image_urls.add(abs_url)
        
        # Extract from CSS background images (simplified)
        style_tags = soup.find_all('style')
        for style in style_tags:
            if style.string:
                # Find URLs in CSS
                css_urls = re.findall(r'url\([\'"]?([^\'"()]+)[\'"]?\)', style.string)
                for url in css_urls:
                    abs_url = urljoin(base_url, url)
                    image_urls.add(abs_url)
        
        # Extract from inline styles
        elements_with_style = soup.find_all(attrs={"style": True})
        for element in elements_with_style:
            if element.get('style'):
                # Find URLs in inline styles
                inline_urls = re.findall(r'url\([\'"]?([^\'"()]+)[\'"]?\)', element['style'])
                for url in inline_urls:
                    abs_url = urljoin(base_url, url)
                    image_urls.add(abs_url)
        
        # Filter by format if specified
        if self.formats:
            filtered_urls = set()
            for url in image_urls:
                ext = self._get_extension_from_url(url)
                if ext in self.formats:
                    filtered_urls.add(url)
            return filtered_urls
        
        return image_urls
    
    def _extract_links(self, html_content, base_url):
        """Extract links from HTML content, ensuring they are from the same domain
        
        Args:
            html_content (str): HTML content
            base_url (str): Base URL for resolving relative URLs
            
        Returns:
            list: List of absolute URLs
        """
        if not html_content:
            return []
            
        soup = BeautifulSoup(html_content, 'html.parser')
        base_domain = urlparse(base_url).netloc
        links = []
        
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            abs_url = urljoin(base_url, href)
            
            # Skip fragment identifiers and non-HTTP links
            if abs_url.startswith(('http://', 'https://')):
                # Only include links from the same domain
                link_domain = urlparse(abs_url).netloc
                if link_domain == base_domain:
                    links.append(abs_url)
        
        return links
    
    def download_images(self, urls, formats=None):
        """Download images in batches with concurrent downloads
        
        Args:
            urls (list): List of image URLs to download
            formats (list): List of formats to filter by
            
        Returns:
            list: Paths to downloaded images
        """
        if not urls:
            logger.warning("No image URLs to download")
            return []
            
        # Process in batches to avoid overwhelming the server
        batch_size = 10
        downloaded = []
        
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            logger.info(f"\nProcessing batch {i//batch_size + 1}/{(len(urls)-1)//batch_size + 1} (images {i+1}-{min(i+batch_size, len(urls))})")
            
            # Use ThreadPoolExecutor for concurrent downloads
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {executor.submit(self.download_image, url, formats): url for url in batch}
                for future in future_to_url:
                    try:
                        result = future.result()
                        if result:
                            downloaded.append(result)
                    except Exception as e:
                        logger.error(f"Error in download thread: {e}")
            
            # Show progress every 5 images
            if (i + batch_size) % 5 == 0 or i + batch_size >= len(urls):
                logger.info(f"Progress: {min(i + batch_size, len(urls))}/{len(urls)} in current batch")
                
            # Pause between batches
            if i + batch_size < len(urls):
                time.sleep(1)  # Avoid overwhelming the server
            
            logger.info(f"Batch {i//batch_size + 1} complete: Downloaded {len(downloaded) - i} images")
                
        return downloaded
    
    def download_image(self, url, formats=None):
        """Download a single image and save it to disk
        
        Args:
            url (str): URL of image to download
            formats (list): List of formats to filter by
            
        Returns:
            str or None: Path to downloaded image or None if download failed
        """
        retries = 2  # Number of retries for each download
        
        for attempt in range(retries + 1):
            try:
                # First perform a HEAD request to check content type
                try:
                    head_response = self.session.head(url, timeout=5)
                    content_type = head_response.headers.get('Content-Type', '').lower()
                except Exception:
                    # If HEAD fails, fallback to GET but only fetch headers
                    head_response = self.session.get(url, timeout=5, stream=True)
                    content_type = head_response.headers.get('Content-Type', '').lower()
                    head_response.close()  # Important: close the connection
                
                # Check if this is actually an image
                if not content_type.startswith('image/'):
                    logger.info(f"Skipping non-image content: {content_type} from {url}")
                    return None
                    
                # Check if format matches requested formats
                if formats:
                    format_matched = False
                    for fmt in formats:
                        if fmt.lower() in ['jpg', 'jpeg'] and 'jpeg' in content_type:
                            format_matched = True
                            break
                        elif fmt.lower() in content_type:
                            format_matched = True
                            break
                    
                    if not format_matched:
                        logger.info(f"Skipping image with format {content_type} - not in requested formats")
                        return None
                
                # Get the image content
                response = self.session.get(url, timeout=15, stream=True)
                response.raise_for_status()
                
                # Determine the correct file extension based on Content-Type
                content_type = response.headers.get('Content-Type', '').lower()
                extension = self._get_extension_from_content_type(content_type)
                if not extension:
                    # Fallback to URL-based extension
                    extension = self._get_extension_from_url(url)
                
                # Get the filename from response or URL
                filename = self._get_filename(url, response)
                
                # Make sure the extension is correct by replacing it
                if extension:
                    base_name = os.path.splitext(filename)[0]
                    filename = f"{base_name}.{extension}"
                
                # Sanitize filename to remove problematic characters
                filename = self._sanitize_filename(filename)
                
                # Save the image
                save_path = os.path.join(self.save_dir, filename)
                
                # Handle duplicate filenames
                counter = 1
                original_base_name, ext = os.path.splitext(filename)
                while os.path.exists(save_path):
                    new_filename = f"{original_base_name}_{counter}{ext}"
                    save_path = os.path.join(self.save_dir, new_filename)
                    counter += 1
                
                # Download the image in chunks to handle large files
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                size_kb = os.path.getsize(save_path) / 1024
                logger.info(f"Downloaded: {filename} ({content_type}) - {size_kb:.1f} KB")
                return save_path
                
            except Exception as e:
                logger.warning(f"Error downloading {url}: {e}. Retrying in {2**attempt}s (attempt {attempt+1}/{retries})")
                if attempt < retries:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to download {url} after {retries} attempts")
                    return None
    
    def _get_extension_from_content_type(self, content_type):
        """Get the file extension from Content-Type header
        
        Args:
            content_type (str): Content-Type header value
            
        Returns:
            str: File extension without dot
        """
        # Map MIME types to appropriate file extensions
        content_type = content_type.lower()
        mime_map = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/bmp': 'bmp',
            'image/webp': 'webp',
            'image/tiff': 'tiff',
            'image/svg+xml': 'svg'
        }
        
        # Check for exact match
        if content_type in mime_map:
            return mime_map[content_type]
        
        # Try partial match (some servers might send additional parameters)
        for mime, ext in mime_map.items():
            if content_type.startswith(mime):
                return ext
        
        # Check for generic patterns
        if 'jpeg' in content_type or 'jpg' in content_type:
            return 'jpg'
        elif 'png' in content_type:
            return 'png'
        elif 'gif' in content_type:
            return 'gif'
        elif 'webp' in content_type:
            return 'webp'
        
        # Default to jpg for unknown image types
        return 'jpg'
    
    def _get_extension_from_url(self, url):
        """Get file extension from URL
        
        Args:
            url (str): URL to extract extension from
            
        Returns:
            str: File extension without dot
        """
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1].lower().replace('.', '')
        
        # Check if extension is valid
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg', 'tiff']:
            return extension
            
        # Default to jpg for unknown extensions
        return 'jpg'
    
    def _get_filename(self, url, response):
        """Generate a filename for the image based on URL or content disposition
        
        Args:
            url (str): URL of the image
            response (Response): Response object from requests
            
        Returns:
            str: Generated filename
        """
        # Try content disposition header first
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            # Extract filename from Content-Disposition
            filename_match = re.search(r'filename=[\'"]?([^\'";]+)', content_disposition)
            if filename_match:
                return filename_match.group(1)
        
        # Try to extract filename from URL
        parsed_url = urlparse(url)
        url_path = parsed_url.path
        filename = os.path.basename(url_path)
        
        # Clean up the filename
        filename = urllib.parse.unquote(filename)  # Handle URL encoding
        
        # If filename looks valid, use it
        if filename and '.' in filename:
            return filename
            
        # Generate a filename based on URL hash
        url_hash = abs(hash(url)) % 10000
        extension = self._get_extension_from_url(url)
        return f"image_{url_hash}.{extension}"
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to remove problematic characters
        
        Args:
            filename (str): Filename to sanitize
            
        Returns:
            str: Sanitized filename
        """
        # Replace potentially problematic characters
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        # Limit filename length to avoid issues with long paths
        if len(filename) > 150:
            name, ext = os.path.splitext(filename)
            filename = name[:140] + ext
            
        # Remove leading/trailing spaces and dots which can cause issues
        filename = filename.strip('. ')
        
        # Ensure filename is not empty
        if not filename or filename == '.':
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            filename = f"image_{timestamp}_{random_suffix}.jpg"
            
        return filename
    
    def save_url_list(self, filename="crawled_urls.txt"):
        """Save the list of visited URLs to a file
        
        Args:
            filename (str): Filename to save URLs to
            
        Returns:
            str: Path to saved file
        """
        file_path = os.path.join(self.save_dir, filename)
        with open(file_path, 'w') as f:
            for url in sorted(self.visited_urls):
                f.write(f"{url}\n")
        
        logger.info(f"Saved {len(self.visited_urls)} URLs to {file_path}")
        return file_path
        
    def save_image_list(self, filename="image_urls.txt"):
        """Save the list of found image URLs to a file
        
        Args:
            filename (str): Filename to save URLs to
            
        Returns:
            str: Path to saved file
        """
        file_path = os.path.join(self.save_dir, filename)
        with open(file_path, 'w') as f:
            for url in sorted(self.image_urls):
                f.write(f"{url}\n")
        
        logger.info(f"Saved {len(self.image_urls)} image URLs to {file_path}")
        return file_path

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="Crawl websites and download images with depth control"
    )
    
    parser.add_argument("url", help="Starting URL to crawl")
    
    parser.add_argument(
        "--depth", "-d", 
        type=int, 
        default=1, 
        help="Maximum depth to crawl (default: 1)"
    )
    
    parser.add_argument(
        "--formats", "-f", 
        nargs="+", 
        help="Image formats to download (e.g., jpg png)"
    )
    
    parser.add_argument(
        "--max", "-m", 
        type=int, 
        default=100, 
        help="Maximum number of images to download (default: 100)"
    )
    
    parser.add_argument(
        "--output", "-o", 
        default="./crawled_images", 
        help="Output directory for downloaded images (default: ./crawled_images)"
    )
    
    parser.add_argument(
        "--delay", 
        type=float, 
        default=1.0, 
        help="Delay between requests in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--save-urls", "-s", 
        action="store_true", 
        help="Save the list of crawled URLs to a file"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create crawler
    crawler = WebsiteImageCrawler(
        save_dir=args.output,
        max_images=args.max,
        formats=args.formats,
        delay=args.delay,
        verbose=args.verbose
    )
    
    # Start crawling
    start_time = time.time()
    result = crawler.crawl(args.url, depth=args.depth)
    end_time = time.time()
    
    # Print results
    logger.info(f"\nCrawling complete!")
    logger.info(f"Visited {len(result['visited_pages'])} pages")
    logger.info(f"Found {result['total_images_found']} images")
    logger.info(f"Downloaded {len(result['downloaded_images'])} images to {args.output}")
    logger.info(f"Time taken: {end_time - start_time:.2f} seconds")
    
    # Save URL lists if requested
    if args.save_urls:
        crawler.save_url_list()
        crawler.save_image_list()

if __name__ == "__main__":
    main()
