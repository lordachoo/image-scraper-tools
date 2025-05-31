# Product Context: Website Image Crawler

## Why This Project Exists
The Website Image Crawler was created to address the growing challenge of extracting images from modern websites that increasingly rely on JavaScript for content loading, employ sophisticated CDN strategies like content negotiation, and implement anti-scraping measures. Traditional scraping tools often fail with these sites, creating a need for a more advanced solution.

## Problems It Solves
1. **JavaScript-heavy websites**: Many modern websites load images dynamically through JavaScript, making them invisible to simple scrapers
2. **Content negotiation**: Modern CDNs serve WebP images even for URLs ending in .jpg or .png
3. **Anti-scraping measures**: Sites implement various protections, including Cloudflare, to prevent automated access
4. **Depth control**: Need to limit crawling depth while maximizing image collection
5. **Format specificity**: Users often need only specific image formats
6. **Performance concerns**: Downloading large numbers of images efficiently

## How It Should Work
1. User provides a starting URL and optional parameters (depth, formats, etc.)
2. The crawler visits the URL and extracts all images, even those in JavaScript
3. If depth > 0, it follows links within the same domain up to the specified depth
4. It filters images based on user-specified formats
5. It downloads images efficiently in parallel with appropriate rate limiting
6. For Cloudflare-protected sites, it uses specialized techniques to bypass protection
7. It handles content negotiation intelligently, preserving requested formats

## User Experience Goals
- Simple command-line interface with intuitive options
- Reasonable defaults for casual usage
- Detailed logging for debugging and progress tracking
- Efficient performance with appropriate rate limiting
- Reliable operation even with complex websites
- Clear documentation with examples for different use cases
