# Changelog for version 1.1.0

## Core Changes
- Removed dependency on BeautifulSoup4, now using regex for HTML parsing
- Added fields parameter to mark_attachments and clean_unused_images methods
- Changed processing order: now marking attachments before processing images

## Improvements
- Improved error handling and logging
- Enhanced performance by reducing unnecessary operations
