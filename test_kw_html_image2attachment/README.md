# Test KW HTML Image to Attachment

[![License: OPL-1](https://img.shields.io/badge/license-OPL--1-red.png)](https://www.odoo.com/documentation/17.0/legal/licenses.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: Test_KW_HTML_Image2Attachment](https://img.shields.io/badge/docs-Test_KW_HTML_Image2Attachment-yellowgreen.png)](https://kitworks.systems/)

This test module provides comprehensive testing infrastructure for the `kw_html_image2attachment` module functionality, ensuring reliable image processing and attachment management.

## Purpose

This module is specifically designed to test the HTML image to attachment conversion functionality by providing:

- **Test Models**: Example models that inherit the HTML image processing mixin
- **Test Cases**: Comprehensive unit tests for all image processing scenarios
- **Mock Data**: Test data for validating conversion workflows
- **Integration Tests**: End-to-end testing of the complete image processing pipeline

## Test Coverage

### Core Functionality Tests
- **External Image Download**: Testing HTTP/HTTPS image URL processing
- **Base64 Image Conversion**: Testing inline image data conversion
- **HTML Content Processing**: Testing complete HTML field processing
- **Attachment Management**: Testing attachment creation and cleanup
- **Error Handling**: Testing invalid URLs and malformed data

### Mixin Integration Tests
- **Model Inheritance**: Testing proper mixin integration with various models
- **Field Processing**: Testing automatic processing on create/write operations
- **Cleanup Operations**: Testing orphaned attachment removal
- **Batch Processing**: Testing large dataset handling

## Test Models

The module includes test models that demonstrate proper usage:

```python
class TestHtmlImageAttachment(models.Model):
    _name = 'test.html.image.attachment'
    _inherit = ['test.html.image.attachment', 'kw.html_image2attachment.mixin']
    
    _kw_html_image2attachment_fields = ['description', 'notes']
    
    description = fields.Html('Description')
    notes = fields.Html('Notes')
```

## Running Tests

### Unit Tests
```bash
# Run all tests for this module
odoo-helper test --module test_kw_html_image2attachment

# Run specific test class
odoo-helper test --module test_kw_html_image2attachment --test-class TestHtmlImageAttachmentMixin

# Run with coverage
odoo-helper test --module test_kw_html_image2attachment --coverage
```

### Test Categories

#### Image Processing Tests
- Valid external image URLs
- Invalid/broken image URLs
- Base64 image data processing
- Mixed content (external + base64) processing
- Large image handling

#### Mixin Functionality Tests
- Create operation with image processing
- Write operation with image processing
- Field-specific processing
- Multiple field processing
- Error recovery and logging

#### Integration Tests
- Complete workflow testing
- Database integrity verification
- Performance benchmarking
- Memory usage validation

## Test Data

The module provides various test scenarios:

### Valid Test Cases
- PNG, JPG, GIF, SVG images
- Different image sizes and formats
- Various URL patterns and protocols
- Complex HTML structures with multiple images

### Error Test Cases
- Invalid image URLs (404, 500 errors)
- Malformed base64 data
- Unsupported image formats
- Network timeout scenarios
- Large file size limits

## Development Usage

### For Module Developers

This test module serves as:

1. **Reference Implementation**: Shows how to properly integrate the HTML image processing mixin
2. **Validation Tool**: Ensures your implementation works correctly
3. **Debugging Aid**: Provides isolated test environment for troubleshooting

### For Quality Assurance

1. **Regression Testing**: Ensures changes don't break existing functionality
2. **Performance Testing**: Validates processing speed and resource usage
3. **Edge Case Testing**: Tests unusual but valid scenarios

## Test Configuration

### Environment Setup
```python
# Test database configuration
'db_name': 'test_html_image2attachment'
'test_enable': True
'test_tags': 'html_image_processing'
```

### Mock Services
The module includes mocks for:
- HTTP requests to external image servers
- File system operations
- Database transaction management
- Error simulation scenarios

## Continuous Integration

### Automated Testing
- Runs automatically on code commits
- Tests all supported Odoo versions
- Validates cross-platform compatibility
- Generates coverage reports

### Performance Benchmarks
- Image processing speed tests
- Memory usage validation
- Batch processing performance
- Database query optimization

## Installation

**Note**: This is a test module and should only be installed in development/testing environments.

1. Install in test/development environment only
2. Requires `kw_html_image2attachment` module
3. Provides additional test models and data
4. Should not be installed in production

## Compatibility

- **Odoo Version**: 18.0
- **Module Version**: 18.0.1.0.1
- **Category**: Hidden (Test Module)
- **License**: OPL-1
- **Dependencies**: `kw_html_image2attachment`

## Security

- **Access Rules**: Provides test-specific access rules
- **Test Data**: Includes security test scenarios
- **Isolated Environment**: Runs in controlled test environment
- **No Production Data**: Uses only mock/test data

## Contributing

### Adding New Tests

1. Create test methods in the appropriate test class
2. Follow naming convention: `test_functionality_scenario`
3. Include both positive and negative test cases
4. Add appropriate assertions and error checking

### Test Documentation

- Document test purpose and expected outcomes
- Include sample data and expected results
- Explain complex test scenarios
- Maintain test coverage reports

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
