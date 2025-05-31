# Active Context: Website Image Crawler

## Current Work Focus
The current focus is on enhancing the crawler's ability to bypass anti-scraping measures, particularly Cloudflare protection, to improve reliability and success rate when crawling protected sites like IMFDB.

## Recent Changes
1. **Cloudflare Bypass Implementation**: 
   - Added cloudscraper library integration to handle Cloudflare-protected sites
   - Implemented domain-specific detection for known protected domains
   - Created fallback mechanism to try cloudscraper when 403 errors are encountered
   - Successfully tested on IMFDB.org which was previously inaccessible

2. **Content Negotiation Handling**:
   - Enhanced handling of WebP images served with .jpg/.png URLs
   - Added warnings for format mismatches
   - Preserved original URL extensions when requested

3. **JavaScript Image Extraction**:
   - Improved extraction of images from JavaScript/JSON content
   - Added support for contentstack.io and similar CDN domains
   - Enhanced regex patterns for better coverage

## Next Steps
1. **Proxy Support**: Add ability to use proxies to distribute requests and avoid IP-based blocking
2. **Rate Limiting Enhancement**: Implement more sophisticated rate limiting based on domain
3. **Cookie Management**: Improve cookie handling for sites requiring session persistence
4. **Site-Specific Handlers**: Develop specialized handlers for common sites/platforms
5. **Testing on More Protected Sites**: Validate Cloudflare bypass on additional protected domains

## Active Decisions and Considerations
1. **Cloudflare Bypass Approach**: Chose cloudscraper over browser automation (Selenium/Playwright) for its lightweight nature and simplicity
2. **Protected Domain List**: Maintaining a list of known Cloudflare-protected domains for proactive handling
3. **Balance of Efficiency vs. Politeness**: Configuring delays to be respectful while maintaining reasonable performance
4. **Format Handling Flexibility**: Allowing users to filter by format while handling content negotiation intelligently

## Important Patterns and Preferences
1. **Robust Error Handling**: Multiple fallback mechanisms for various error conditions
2. **Clear User Feedback**: Informative logging, especially for edge cases like format mismatches
3. **Modularity**: Keeping the code organized with clear separation of concerns
4. **Performance Optimization**: Concurrent downloads with appropriate rate limiting

## Learnings and Project Insights
1. **Cloudflare Detection**: Cloudflare and similar services are increasingly sophisticated in bot detection
2. **Content Negotiation Prevalence**: Many modern CDNs serve WebP regardless of requested URL extension
3. **JavaScript Dependency**: More sites are rendering critical content via JavaScript, requiring specialized extraction
4. **Anti-Bot Evolution**: Anti-scraping measures are continuously evolving, requiring ongoing maintenance
