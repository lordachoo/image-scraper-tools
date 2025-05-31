# Technical Context: Website Image Crawler

## Technologies Used

### Core Dependencies
- **Python 3.6+**: Core programming language
- **requests**: HTTP client for fetching pages and images
- **BeautifulSoup4**: HTML parsing for image extraction
- **urllib.parse**: URL manipulation and normalization
- **concurrent.futures**: Thread pool for concurrent downloads
- **cloudscraper**: Specialized library to bypass Cloudflare protection
- **logging**: Structured logging for operation tracking

### Development Tools
- **Git**: Version control
- **pip**: Package management
- **argparse**: Command-line interface parsing

## Technical Constraints
1. **Respect for Websites**:
   - Configurable delays between requests
   - User-agent rotation to reduce impact
   - No aggressive crawling patterns

2. **Security Limitations**:
   - No handling of authentication
   - No storage of cookies between sessions
   - Limited to publicly accessible content

3. **Anti-Bot Considerations**:
   - Cloudflare and similar protections may evolve
   - Not all anti-bot measures can be bypassed
   - Some sites may block even sophisticated scrapers

## Dependencies
```
requests>=2.25.0
beautifulsoup4>=4.9.0
urllib3>=1.26.0
cloudscraper>=1.2.0
```

## Tool Usage Patterns

### Command-Line Interface
The tool is designed for command-line usage with a balance of required and optional parameters:
```
python website_image_crawler.py [url] [options]
```

### Configuration Options
- **Required**: Starting URL
- **Optional**: Depth, formats, max images, output directory, delay, verbosity

### Execution Environments
- Compatible with Linux, macOS, and Windows
- Can be used in scripts and automation
- Works in Jupyter Notebooks for interactive usage

### Output Handling
- Images saved to specified directory with appropriate extensions
- Terminal output with progress information
- Optional verbose logging for debugging
- Format mismatch warnings for content negotiation cases
