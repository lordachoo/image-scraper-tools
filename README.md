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

## Usage

```bash
python image_scraper.py "search query" [OPTIONS]
```

### Command-line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
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

## How It Works

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
