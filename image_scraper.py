#!/usr/bin/env python3
"""
Simple Image Scraper - Download images by search query with format filtering
"""
import os
import re
import json
import sys
import argparse
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, quote_plus

class ImageScraper:
    def __init__(self, save_dir="/mnt/d/media/raw/firearms/", max_images=50000):
        """Initialize the image scraper"""
        self.save_dir = save_dir
        self.max_images = max_images
        
        # Create directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # Set up session with more realistic browser-like headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/jxl,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bing.com/',
            'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Connection': 'keep-alive'
        })
    
    def search_images(self, query, formats=None, engine="duckduckgo"):
        """Search for images using the specified engine with fallback mechanism"""
        print(f"Searching for '{query}' images...")
        
        image_urls = []
        
        # Try the requested engine first
        if engine == "bing":
            image_urls = self._search_bing(query, formats)
        elif engine == "duckduckgo":
            image_urls = self._search_duckduckgo(query, formats)
        elif engine == "google":
            image_urls = self._search_google(query, formats)
        else:
            print(f"Unknown engine: {engine}. Using DuckDuckGo instead.")
            engine = "duckduckgo"
            image_urls = self._search_duckduckgo(query, formats)
        
        # If the primary engine failed, try fallbacks
        if not image_urls:
            print(f"No results from {engine}. Trying fallback engines...")
            
            # If we haven't tried DuckDuckGo yet, try it now (most reliable)
            if engine != "duckduckgo":
                print("Trying DuckDuckGo as fallback...")
                image_urls = self._search_duckduckgo(query, formats)
                
            # If we still don't have results and haven't tried Bing yet, try it
            if not image_urls and engine != "bing":
                print("Trying Bing as fallback...")
                image_urls = self._search_bing(query, formats)
        
        return image_urls
            
    def _search_bing(self, query, formats=None):
        """Search for images using Bing with a simpler approach"""
        # First, visit Bing homepage to get cookies
        try:
            self.session.get("https://www.bing.com", timeout=10)
        except Exception as e:
            print(f"Warning: Could not initialize Bing session: {e}")
        
        # Set up headers to look more like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.bing.com/',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # Try Google search instead
        print(f"Bing search may be blocked by the server. Trying Google instead.")
        return self._search_google(query, formats)
    
    def _search_google(self, query, formats=None):
        """Search for images using Google as an alternative"""
        # Google image search URL
        base_url = "https://www.google.com/search"
        
        # Format filter parameter for Google
        format_param = ""
        if formats:
            format_types = []
            for fmt in formats:
                if fmt.lower() in ['jpg', 'jpeg']:
                    format_types.append('jpg')
                else:
                    format_types.append(fmt.lower())
            format_param = " filetype:" + " OR filetype:".join(format_types)
        
        # Prepare search query with format filter
        search_query = query + format_param
        
        # Set up parameters
        params = {
            'q': search_query,
            'tbm': 'isch',  # Image search
            'ijn': '0',     # Page number
            'start': '0',   # Starting image
            'asearch': 'ichunk',
            'async': '_id:rg_s,_pms:s,_fmt:pc'
        }
        
        # Update headers for Google
        self.session.headers.update({
            'Referer': 'https://www.google.com/',
            'Authority': 'www.google.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        })
        
        print(f"Searching Google for: {search_query}")
        image_urls = []
        
        try:
            # Send request
            response = self.session.get(base_url, params=params, timeout=20)
            response.raise_for_status()
            
            # Save the HTML response to a file for debugging
            with open('google_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"Saved response HTML to google_response.html for debugging")
            
            # Extract image URLs
            # Google stores image URLs in the 'src' attribute of img tags and in JSON data
            # Method 1: Extract from JSON data
            data_matches = re.findall(r'\["(https?://[^"]+\.(?:jpg|jpeg|png))",[^\]]+\]', response.text)
            
            # Method 2: Extract from img tags
            img_matches = re.findall(r'<img[^>]+src=["\']?(https?://[^"\'>]+\.(?:jpg|jpeg|png))["\'>]', response.text)
            
            # Combine results
            all_matches = data_matches + img_matches
            
            # Process URLs
            for url in all_matches:
                if url.startswith('http') and url not in image_urls:
                    image_urls.append(url)
            
            print(f"Found {len(image_urls)} images from Google")
            
            # If we didn't find any, try a different pattern
            if len(image_urls) == 0:
                print("Trying alternative pattern...")
                alt_matches = re.findall(r'\["(https?://[^"]+)",[^\]]+\]', response.text)
                for url in alt_matches:
                    if '.jpg' in url.lower() or '.jpeg' in url.lower() or '.png' in url.lower():
                        if url not in image_urls:
                            image_urls.append(url)
                            
                print(f"Found {len(image_urls)} images with alternative pattern")
            
        except Exception as e:
            print(f"Error searching Google: {e}")
        
        return image_urls[:self.max_images]
    
    def _search_duckduckgo(self, query, formats=None):
        """Search for images using DuckDuckGo with pagination"""
        # DuckDuckGo uses a different approach with an API endpoint
        vqd_url = "https://duckduckgo.com/"
        search_url = "https://duckduckgo.com/i.js"
        
        try:
            # First request to get the vqd token (required for API)
            response = self.session.get(vqd_url, params={'q': query}, timeout=10)
            vqd_match = re.search(r'vqd="([^"]+)"', response.text)
            
            if not vqd_match:
                print("Could not extract DuckDuckGo search token")
                return []
                
            vqd = vqd_match.group(1)
            
            # Format filter
            formats_str = ""
            if formats:
                format_list = []
                for fmt in formats:
                    if fmt.lower() in ['jpg', 'jpeg']:
                        format_list.append('jpg')
                    else:
                        format_list.append(fmt.lower())
                formats_str = ",".join(set(format_list))
            
            # Now get the images with pagination
            image_urls = []
            max_pages = min(10, self.max_images // 50 + 1)  # DuckDuckGo returns ~50 images per page
            
            for page in range(max_pages):
                if len(image_urls) >= self.max_images:
                    break
                    
                # Create params with pagination
                params = {
                    'q': query,
                    'o': 'json',
                    'vqd': vqd,
                    'f': formats_str if formats_str else '',
                    'p': '1',  # Safe search off
                    's': page * 50,  # Skip parameter for pagination
                    't': 'images',
                    'iax': 'images'
                }
                
                # Add randomized delay between requests to avoid rate limiting
                if page > 0:
                    delay = random.uniform(1.0, 3.0)
                    print(f"Waiting {delay:.1f} seconds before loading page {page+1}...")
                    time.sleep(delay)
                
                try:
                    print(f"Searching DuckDuckGo page {page+1} with offset {page*50}")
                    response = self.session.get(search_url, params=params, timeout=15)
                    response.raise_for_status()
                    
                    # Parse JSON response
                    data = response.json()
                    new_urls_count = 0
                    
                    for result in data.get('results', []):
                        image_url = result.get('image')
                        if image_url and image_url.startswith('http'):
                            if image_url not in image_urls:  # Skip duplicates
                                image_urls.append(image_url)
                                new_urls_count += 1
                    
                    print(f"Found {new_urls_count} new images from DuckDuckGo page {page+1}")
                    
                    # If we don't get any new images, or we get fewer than expected, we've likely reached the end
                    if new_urls_count == 0 or len(data.get('results', [])) < 20:
                        print("Reached end of results")
                        break
                        
                except Exception as e:
                    print(f"Error fetching DuckDuckGo page {page+1}: {e}")
                    # Continue to next page despite errors
                    continue
            
            print(f"Total images found from DuckDuckGo: {len(image_urls)}")
            return image_urls[:self.max_images]
            
        except Exception as e:
            print(f"Error in DuckDuckGo search setup: {e}")
            return []
    
    def download_images(self, urls, formats=None):
        """Download images from the provided URLs"""
        if not urls:
            print("No image URLs to download.")
            return []
        
        print(f"Downloading up to {len(urls)} images...")
        
        downloaded = []
        
        # Process URLs in batches to avoid overwhelming connections
        batch_size = 20  # Number of concurrent downloads
        total_batches = (len(urls) + batch_size - 1) // batch_size
        
        for batch_num, i in enumerate(range(0, len(urls), batch_size)):
            batch_urls = urls[i:i+batch_size]
            batch_start = i + 1
            batch_end = min(i + batch_size, len(urls))
            
            print(f"\nProcessing batch {batch_num+1}/{total_batches} (images {batch_start}-{batch_end})")
            
            batch_downloaded = []
            with ThreadPoolExecutor(max_workers=min(10, len(batch_urls))) as executor:
                # Submit the batch of downloads
                future_to_url = {executor.submit(self.download_image, url, formats): url for url in batch_urls}
                
                # Track completed downloads for progress reporting
                completed = 0
                
                # Process the results as they complete
                for future in future_to_url:
                    try:
                        result = future.result(timeout=60)  # Add timeout to prevent hanging
                        if result:
                            batch_downloaded.append(result)
                        
                        # Update progress
                        completed += 1
                        if completed % 5 == 0 or completed == len(batch_urls):
                            print(f"Progress: {completed}/{len(batch_urls)} in current batch")
                            
                    except Exception as e:
                        print(f"Error in download thread: {e}")
                        # Continue with other downloads
                        completed += 1
                        continue
            
            # Add the batch results to our total downloaded list
            downloaded.extend(batch_downloaded)
            print(f"Batch {batch_num+1} complete: Downloaded {len(batch_downloaded)}/{len(batch_urls)} images")
            
            # Sleep between batches to avoid overwhelming the server/network
            # But don't sleep after the last batch
            if batch_num < total_batches - 1:
                pause_time = random.uniform(2.0, 4.0)
                print(f"Pausing for {pause_time:.1f} seconds before next batch...")
                time.sleep(pause_time)
                
        print(f"\nDownload complete! Successfully downloaded {len(downloaded)} of {len(urls)} images")
        return downloaded
    
    def download_image(self, url, formats=None):
        """Download a single image and save it to disk"""
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
                    print(f"Skipping non-image content: {content_type} from {url}")
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
                        print(f"Skipping image with format {content_type} - not in requested formats")
                        return None
                
                # Get the filename from URL or content disposition
                response = self.session.get(url, timeout=15, stream=True)
                response.raise_for_status()
                
                # Determine the correct file extension based on Content-Type
                # This ensures the file has the right extension regardless of the URL
                content_type = response.headers.get('Content-Type', '').lower()
                extension = self._get_extension_from_content_type(content_type)
                if not extension:
                    # Fallback to URL-based extension
                    extension = self._guess_extension(url)
                
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
                
                # Check if we already have this file (avoid duplicates)
                if os.path.exists(save_path):
                    # Add a suffix to make it unique
                    name, ext = os.path.splitext(filename)
                    filename = f"{name}_{random.randint(1, 999)}{ext}"
                    save_path = os.path.join(self.save_dir, filename)
                
                with open(save_path, 'wb') as f:
                    # Use a timeout for the writing process to prevent hanging
                    bytes_downloaded = 0
                    start_time = time.time()
                    for chunk in response.iter_content(chunk_size=8192):
                        # Check if download is taking too long
                        if time.time() - start_time > 30:  # 30 second timeout
                            raise TimeoutError("Download taking too long")
                        
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)
                            bytes_downloaded += len(chunk)
                
                # Verify we got some actual data
                if bytes_downloaded == 0:
                    os.remove(save_path)  # Remove empty file
                    print(f"Downloaded empty file from {url}, skipping")
                    return None
                
                print(f"Downloaded: {filename} ({content_type}) - {bytes_downloaded/1024:.1f} KB")
                return save_path
                
            except (requests.exceptions.RequestException, requests.exceptions.Timeout, TimeoutError) as e:
                if attempt < retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    print(f"Error downloading {url}: {e}. Retrying in {wait_time}s (attempt {attempt+1}/{retries})")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to download {url} after {retries} retries: {e}")
                    return None
            except Exception as e:
                print(f"Unexpected error downloading {url}: {e}")
                return None
                
        return None  # Fallback in case all retries fail
    
    def _get_filename(self, url, response):
        """Generate a filename for the downloaded image"""
        # Try to get filename from Content-Disposition header
        content_disposition = response.headers.get('Content-Disposition', '')
        filename_match = re.search(r'filename="?([^"]+)"?', content_disposition)
        
        if filename_match:
            return filename_match.group(1)
        
        # Otherwise extract from URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        
        # If filename is empty or lacks extension, create one
        if not filename or '.' not in filename:
            # Determine extension from Content-Type
            content_type = response.headers.get('Content-Type', '').lower()
            extension = 'jpg'  # default
            
            if 'image/png' in content_type:
                extension = 'png'
            elif 'image/jpeg' in content_type:
                extension = 'jpg'
            elif 'image/gif' in content_type:
                extension = 'gif'
            elif 'image/webp' in content_type:
                extension = 'webp'
            
            # Create filename with timestamp to ensure uniqueness
            timestamp = int(time.time())
            random_suffix = random.randint(1000, 9999)
            filename = f"image_{timestamp}_{random_suffix}.{extension}"
        
        return filename
    
    def _get_extension_from_content_type(self, content_type):
        """Get the file extension from Content-Type header"""
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
    
    def _get_filename_from_url(self, url):
        """Extract filename from URL"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        filename = os.path.basename(path)
        
        # If URL has no filename or invalid characters, return None
        if not filename or filename == '/' or '?' in filename or '#' in filename:
            return None
            
        return filename
    
    def _guess_extension(self, url):
        """Guess file extension from URL"""
        parsed_url = urlparse(url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1].lower().replace('.', '')
        
        # Check if extension is valid
        if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
            return extension
            
        # Default to jpg for unknown extensions
        return 'jpg'
    
    def _sanitize_filename(self, filename):
        """Sanitize filename to remove problematic characters"""
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Download images by search query with format filtering")
    parser.add_argument("query", help="Search query for images")
    parser.add_argument("--formats", "-f", nargs="+", help="Image formats to filter (e.g., jpg png)")
    parser.add_argument("--max", "-m", type=int, default=25, help="Maximum number of images to download")
    parser.add_argument("--output", "-o", default="./downloaded_images", help="Output directory for downloaded images")
    parser.add_argument("--engine", "-e", default="bing", choices=["bing", "duckduckgo"], 
                        help="Search engine to use (bing, duckduckgo)")
    
    args = parser.parse_args()
    
    # Initialize the scraper
    scraper = ImageScraper(save_dir=args.output, max_images=args.max)
    
    # Search for images
    image_urls = scraper.search_images(args.query, args.formats, args.engine)
    
    if not image_urls:
        print("No images found matching your criteria.")
        return
    
    # Download the images
    downloaded = scraper.download_images(image_urls, args.formats)
    
    print(f"\nDownload complete! Saved {len(downloaded)} images to {args.output}")

if __name__ == "__main__":
    main()
