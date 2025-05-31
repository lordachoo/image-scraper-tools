# System Patterns: Website Image Crawler

## System Architecture
The Website Image Crawler follows a modular, object-oriented design with clearly separated concerns:

1. **Main WebsiteImageCrawler Class**: Core orchestration logic
2. **URL Crawling**: BFS traversal with depth control
3. **Image Extraction**: Multiple strategies for different sources
4. **Download Management**: Concurrent downloads with error handling
5. **Anti-Bot Bypass**: Specialized handling for protected sites

## Key Technical Decisions

### 1. Image Extraction Strategy
- HTML parsing with BeautifulSoup for standard elements
- Regex-based extraction for CSS and JavaScript
- Multiple extraction methods combined for maximum coverage

### 2. Anti-Bot Solution
- Browser-like headers to mimic legitimate browsers
- User-agent rotation to appear more human-like
- Cloudflare bypass using the cloudscraper library
- Domain-specific handling for known protected sites

### 3. Concurrency Model
- ThreadPoolExecutor for parallel downloads
- Session reuse for connection pooling
- Rate limiting with configurable delays

### 4. Error Handling
- Exponential backoff for transient errors
- Multiple fallback strategies for various failure modes
- Detailed logging for troubleshooting

## Component Relationships
```
WebsiteImageCrawler
├── _crawl_url(): URL traversal logic
├── _extract_images(): Extract from HTML
│   ├── _extract_html_images(): Standard img tags
│   ├── _extract_css_images(): CSS backgrounds
│   └── _extract_javascript_images(): JS/JSON content
├── _fetch_url(): HTTP handling with anti-bot measures
│   ├── Regular requests with browser-like headers
│   └── Cloudflare bypass with cloudscraper
├── download_images(): Concurrent download management
└── download_image(): Individual image download with validation
```

## Critical Implementation Paths

### Image Extraction Flow
1. Fetch page content with anti-bot measures
2. Parse HTML with BeautifulSoup
3. Extract images from various sources (HTML, CSS, JS)
4. Normalize and filter URLs
5. Queue for download if matching format criteria

### Cloudflare Bypass Flow
1. Detect Cloudflare protection or known protected domains
2. Use cloudscraper with appropriate settings
3. Fall back to regular requests if cloudscraper fails
4. Handle cookies and maintain sessions appropriately

### Download Management Flow
1. Filter images by requested formats
2. Group into batches for concurrent processing
3. Download with appropriate error handling
4. Validate Content-Type and handle format mismatches
5. Save with correct file extension
