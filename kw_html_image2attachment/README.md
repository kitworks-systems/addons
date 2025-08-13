# HTML Image to Attachment

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: HTML_Image_to_Attachment](https://img.shields.io/badge/docs-HTML_Image_to_Attachment-yellowgreen.png)](https://kitworks.systems/)

This module automatically converts external images and base64-encoded images from HTML fields into proper Odoo attachments, improving performance and data management.

## Key Features

- **External Image Processing**: Downloads external images from URLs and saves them as attachments
- **Base64 Image Conversion**: Converts inline base64 images to attachment references
- **Automatic HTML Updating**: Updates HTML content to reference local attachment URLs
- **Cleanup Management**: Automatically removes unused image attachments
- **Batch Processing**: Includes cron job for processing existing records
- **Mixin Architecture**: Easy integration with any model through inheritance

## Components

### 1. HTML Image Processing Tool (`kw.html_image2attachment.tool`)

Abstract model providing core functionality:

- `download_and_save_image()`: Downloads external images and creates attachments
- `save_base_64_image()`: Converts base64 images to attachments
- `process_images_in_html()`: Processes all images in HTML content
- `clean_unused_images()`: Removes orphaned image attachments
- `mark_attachments()`: Marks attachments as HTML images

### 2. Mixin Model (`kw.html_image2attachment.mixin`)

Abstract mixin for easy integration with any model:

```python
class YourModel(models.Model):
    _name = 'your.model'
    _inherit = ['your.model', 'kw.html_image2attachment.mixin']
    
    # Define which HTML fields should be processed
    _kw_html_image2attachment_fields = ['description', 'notes']
```

### 3. Processing Tasks

- **Task Model**: Manages processing jobs for existing records
- **Cron Job**: Automatically processes pending tasks
- **Batch Processing**: Handles large datasets efficiently

## Usage Examples

### Basic Integration

```python
class ProjectTask(models.Model):
    _inherit = ['project.task', 'kw.html_image2attachment.mixin']
    
    _kw_html_image2attachment_fields = ['description']
```

### Manual Processing

```python
# Process images in HTML content
tool = self.env['kw.html_image2attachment.tool']
processed_html = tool.process_images_in_html(html_content, record)

# Clean up unused images
tool.clean_unused_images(record)
```

## Image Types Supported

### External Images
- **HTTP/HTTPS URLs**: `<img src="https://example.com/image.jpg">`
- **Automatic Download**: Images are downloaded and stored as attachments
- **Error Handling**: Invalid URLs are logged but don't break processing

### Base64 Images
- **Inline Images**: `<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...">`
- **Multiple Formats**: PNG, JPG, GIF, SVG support
- **MIME Type Detection**: Automatic file extension assignment

## Installation

1. Install the module through the Odoo Apps menu
2. The module will create necessary security rules and cron jobs
3. Configure processing tasks in **Settings > Technical > HTML Image Processing**

## Configuration

### Processing Tasks

Navigate to **Settings > Technical > HTML Image Processing > Tasks** to:

- View processing status
- Monitor failed conversions
- Manually trigger processing for specific records

### Cron Job Configuration

The module includes an automated cron job that:

- Runs every hour by default
- Processes pending tasks in batches
- Can be configured in **Settings > Technical > Automation > Scheduled Actions**

## Performance Benefits

### Before Module
- External images loaded from external servers (slow)
- Base64 images embedded in HTML (large database size)
- Network dependency for image display
- Potential security issues with external content

### After Module
- All images stored as Odoo attachments (fast local access)
- HTML contains only attachment references (smaller database records)
- No external network calls for image display
- Centralized image management and security

## Technical Details

- **Dependencies**: `base`, `requests` (Python library)
- **Models**: Task management, Attachment extensions, Processing tools
- **Security**: Access rules for task management
- **Automation**: Cron job for batch processing
- **Error Handling**: Comprehensive logging and error recovery

## Use Cases

- **CRM**: Customer communications with embedded images
- **Projects**: Task descriptions with screenshots and diagrams  
- **E-commerce**: Product descriptions with multiple images
- **Documentation**: Knowledge base articles with illustrations
- **Email Processing**: Convert email images to attachments

## Compatibility

- **Odoo Version**: 18.0
- **Module Version**: 18.0.1.2.1
- **Category**: Customizations
- **License**: LGPL-3

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
