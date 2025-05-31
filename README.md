# Image Scraping Tools

A collection of powerful and reliable command-line tools for scraping and downloading images from various sources.

## Tools

This package includes two powerful image scraping tools:

1. **image_scraper.py** - Search engine-based image scraper
2. **website_image_crawler.py** - Website crawler that extracts images with depth control

## Common Features

- **Format Filtering**: Filter images by specific formats (jpg, png, etc.)
- **Robust Error Handling**: Retries with exponential backoff for transient network errors
- **Concurrent Downloads**: Downloads images in parallel with appropriate rate limiting
- **Content-Type Verification**: Ensures downloaded files match requested formats
- **Proper File Extensions**: Automatically detects and fixes file extensions based on Content-Type
- **Customizable Output**: Specify output directory and maximum number of images
- **Detailed Logging**: Progress reporting and error diagnostics

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - requests
  - urllib3
  - beautifulsoup4 (for website crawler)
  - cloudscraper (for bypassing Cloudflare protection)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd image-scraper
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Tool 1: Search Engine Image Scraper

### Description
The `image_scraper.py` tool searches for images matching a query across multiple search engines (DuckDuckGo, Bing, and Google with automatic fallback) and downloads them.

### Features
- **Multiple Search Engines**: Uses DuckDuckGo (default), Bing, and Google with automatic fallback
- **Pagination Support**: Retrieves images from multiple result pages

### Usage

```bash
python image_scraper.py "search query" [OPTIONS]
```

### Command-line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|----------|
| `query` | - | Search query for images (required) | - |
| `--formats`, `-f` | `-f` | Image formats to filter (e.g., jpg png) | All formats |
| `--max`, `-m` | `-m` | Maximum number of images to download | 25 |
| `--output`, `-o` | `-o` | Output directory for downloaded images | ./downloaded_images |
| `--engine`, `-e` | `-e` | Search engine to use (bing, duckduckgo) | duckduckgo |

### Examples

**Basic search:**
```bash
python image_scraper.py "landscape mountains"
```

**Download specific formats:**
```bash
python image_scraper.py "landscape mountains" --formats jpg png
```

**Download more images:**
```bash
python image_scraper.py "landscape mountains" --max 100
```

**Specify output directory:**
```bash
python image_scraper.py "landscape mountains" --output ./mountain_pics
```

**Use a specific search engine:**
```bash
python image_scraper.py "landscape mountains" --engine bing
```

**Combine multiple options:**
```bash
python image_scraper.py "landscape mountains" --formats jpg png --max 50 --output ./mountain_pics --engine duckduckgo
```

## Tool 2: Website Image Crawler

### Description
The `website_image_crawler.py` tool crawls a specific website, extracting all images and optionally following links to a specified depth.

### Features
- **Depth Control**: Specify how many pages deep to crawl (1 = just the starting page)
- **Domain Limiting**: Only follows links within the same domain
- **URL Listing**: Can save all crawled URLs and image URLs to text files
- **CSS Background Extraction**: Also extracts images from CSS backgrounds
- **JavaScript Image Extraction**: Extracts image URLs embedded in JavaScript and JSON content
- **Content Negotiation Handling**: Properly handles modern CDNs that serve optimized image formats (WebP) for traditional URLs (.jpg, .png)
- **Format Preservation**: Maintains original URL extensions when requested, even when servers use content negotiation
- **Cloudflare Bypass**: Automatically detects and bypasses Cloudflare and similar anti-bot protection

### Usage

```bash
python website_image_crawler.py "https://example.com" [OPTIONS]
```

### Command-line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|----------|
| `url` | - | Starting URL to crawl (required) | - |
| `--depth`, `-d` | `-d` | Maximum depth to crawl | 1 |
| `--formats`, `-f` | `-f` | Image formats to filter (e.g., jpg png) | All formats |
| `--max`, `-m` | `-m` | Maximum number of images to download | 100 |
| `--output`, `-o` | `-o` | Output directory for downloaded images | ./crawled_images |
| `--delay` | - | Delay between requests in seconds | 1.0 |
| `--save-urls`, `-s` | `-s` | Save the list of crawled URLs to a file | False |
| `--verbose`, `-v` | `-v` | Enable verbose output | False |

### Examples

**Basic website crawl (just the homepage):**
```bash
python website_image_crawler.py "https://example.com"
```

**Crawl 3 levels deep:**
```bash
python website_image_crawler.py "https://example.com" --depth 3
```

**Download only JPG and PNG images:**
```bash
python website_image_crawler.py "https://example.com" --formats jpg png
```

**Save up to 200 images and use a specific output directory:**
```bash
python website_image_crawler.py "https://example.com" --max 200 --output ./example_images
```

**Save list of all crawled URLs:**
```bash
python website_image_crawler.py "https://example.com" --save-urls
```

**Add a longer delay between requests for rate limiting:**
```bash
python website_image_crawler.py "https://example.com" --delay 2.5
```

**Crawl a site with all options:**
```bash
python website_image_crawler.py "https://example.com" --depth 2 --formats jpg png --max 150 --output ./example_images --save-urls --delay 1.5 --verbose
```

**Extract images from JavaScript-heavy websites:**
```bash
python website_image_crawler.py "https://www.smith-wesson.com/" --formats jpg png --output ./smith_images --verbose
```

**Scrape images from Cloudflare-protected sites:**
```bash
python website_image_crawler.py "https://imfdb.org/wiki/Main_Page" --formats jpg png --output ./imfdb_images --verbose
```

The JavaScript extraction feature is particularly effective for modern e-commerce sites and content management systems that load images dynamically through JavaScript. The Cloudflare bypass feature automatically detects protected sites and uses specialized techniques to access content that would normally be blocked.

## How It Works

### Image Scraper Tool

1. **Search Phase**: 
   - The tool sends a search query to the specified search engine
   - It extracts image URLs from the search results
   - If the primary engine fails, it automatically tries fallback engines

2. **Download Phase**:
   - The tool performs format validation using HEAD requests
   - It downloads images in batches with concurrent processing
   - Each download includes retry logic for transient errors
   - File extensions are corrected based on actual Content-Type

3. **Post-Processing**:
   - Filename sanitization to ensure valid filenames
   - Duplicate detection to avoid overwriting files
   - Verification of downloaded content

### Website Crawler Tool

1. **Crawling Phase**:
   - Starts from the specified URL and extracts all links
   - Follows links up to the specified depth, staying within the same domain
   - Manages a queue of URLs to visit while avoiding duplicates
   - Respects delay settings to avoid overwhelming the target server

2. **Image Extraction**:
   - Extracts images from standard HTML elements (img tags, srcset attributes)
   - Finds images in CSS backgrounds and inline styles
   - **JavaScript Extraction**: Uses regex patterns to extract image URLs from JavaScript and JSON content in script tags
   - Particularly effective for modern websites using content management systems or JavaScript frameworks
   - Supports specialized CDN domains like `contentstack.io` used by many commercial websites

3. **Download Phase**:
   - Validates image URLs and formats before downloading
   - **Content Negotiation Handling**: Detects when servers deliver WebP images for URLs ending in .jpg or .png
   - **Format Preservation**: Saves files with requested extensions even when content is delivered in a different format
   - Provides clear warnings when format mismatches occur
   - Downloads occur in parallel with thread pool management for efficiency
   - Implements adaptive delay based on server response

4. **Anti-Bot Bypass**:
   - **Cloudflare Detection**: Automatically identifies Cloudflare-protected websites
   - **Specialized Handling**: Uses cloudscraper library to bypass protection
   - **Domain Recognition**: Pre-emptively uses bypass techniques for known protected domains
   - **Fallback Mechanism**: Attempts regular requests first, falls back to bypass techniques when necessary

## Error Handling

The scraper implements several error handling mechanisms:
- Retry logic with exponential backoff for network errors
- HEAD request fallback to GET when HEAD is blocked
- Timeouts to prevent hanging downloads
- Engine fallback when a search engine fails to return results
- Content-Type verification to skip invalid content

## Limitations

- Search engines may periodically change their HTML structure, requiring updates
- Some websites block scraping attempts or rate-limit requests
- The tool respects robots.txt implicitly through the `requests` library behavior
- No official API usage means reliability is not guaranteed

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
