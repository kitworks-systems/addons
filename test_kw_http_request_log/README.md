# Test KW HTTP Request Log

[![License: OPL-1](https://img.shields.io/badge/license-OPL--1-red.png)](https://www.odoo.com/documentation/17.0/legal/licenses.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: Test_KW_HTTP_Request_Log](https://img.shields.io/badge/docs-Test_KW_HTTP_Request_Log-yellowgreen.png)](https://kitworks.systems/)

This test module provides comprehensive testing infrastructure for the `kw_http_request_log` module, ensuring reliable HTTP request logging and monitoring functionality.

## Purpose

This module is designed to thoroughly test the HTTP request logging capabilities by providing:

- **Test Models**: Example models that inherit HTTP request logging mixins
- **Integration Tests**: Complete workflow testing for HTTP request logging
- **Mock Services**: Simulated HTTP services for controlled testing
- **Performance Tests**: Validation of logging performance and resource usage
- **Error Scenario Testing**: Comprehensive error handling validation

## Test Coverage

### Core Logging Functionality
- **Request Logging**: Testing HTTP request capture and storage
- **Response Logging**: Testing HTTP response processing and storage
- **Error Handling**: Testing timeout, connection, and HTTP error scenarios
- **Data Integrity**: Testing log data accuracy and completeness
- **Performance Impact**: Testing logging overhead on normal operations

### Mixin Integration Tests
- **Source Mixin**: Testing `kw.http.request.log.source.mixin` integration
- **Generic Mixin**: Testing integration with `generic_mixin` functionality
- **Multi-model Support**: Testing logging across different model types
- **Transaction Management**: Testing logging within database transactions

## Test Models

### HTTP Request Log Source Test Model

The module includes test models demonstrating proper mixin usage:

```python
class TestLogSource(models.Model):
    _name = 'test.kw.http.request.log.source'
    _inherit = ['test.kw.http.request.log.source', 
                'kw.http.request.log.source.mixin',
                'generic.mixin.transaction.utils']
    _description = 'Test Model for HTTP Request Log Source'
```

### Test Scenarios

#### HTTP Request Types
- GET requests with various parameters
- POST requests with JSON/form data
- PUT/PATCH requests for updates
- DELETE requests for resource removal
- File upload requests with multipart data

#### Authentication Testing
- Basic authentication logging
- API key authentication
- OAuth token authentication
- Custom header authentication
- Anonymous requests

## Running Tests

### Complete Test Suite
```bash
# Run all HTTP request log tests
odoo-helper test --module test_kw_http_request_log

# Run specific test classes
odoo-helper test --module test_kw_http_request_log --test-class TestKwHttpRequestLog
odoo-helper test --module test_kw_http_request_log --test-class TestKwHttpRequestLogSource

# Run with detailed coverage
odoo-helper test --module test_kw_http_request_log --coverage --verbose
```

### Specific Test Categories

#### Core Functionality Tests
```bash
# Test basic logging functionality
python -m pytest tests/test_kw_http_request_log.py::TestKwHttpRequestLog::test_basic_logging

# Test error handling
python -m pytest tests/test_kw_http_request_log.py::TestKwHttpRequestLog::test_error_scenarios
```

#### Integration Tests
```bash
# Test mixin integration
python -m pytest tests/test_kw_http_request_log_source.py::TestKwHttpRequestLogSource::test_mixin_integration

# Test transaction handling
python -m pytest tests/test_kw_http_request_log_source.py::TestKwHttpRequestLogSource::test_transaction_utils
```

## Test Scenarios

### Successful Request Logging
- **Standard Requests**: Testing normal HTTP request/response cycles
- **Large Payloads**: Testing handling of large request/response bodies
- **Complex Headers**: Testing various header configurations
- **Different Content Types**: JSON, XML, form data, binary content

### Error Condition Testing
- **Network Errors**: Connection timeouts, DNS failures
- **HTTP Errors**: 4xx client errors, 5xx server errors
- **Malformed Data**: Invalid JSON, corrupted responses
- **Resource Limits**: Memory limits, request size limits

### Performance Testing
- **High Volume**: Testing logging performance under load
- **Concurrent Requests**: Testing thread safety and concurrency
- **Memory Usage**: Testing memory efficiency of logging operations
- **Database Performance**: Testing log storage efficiency

## Mock Services

### HTTP Mock Server
The module includes mock HTTP services for testing:

```python
class MockHTTPService:
    """Mock HTTP service for controlled testing"""
    
    def simulate_success_response(self):
        """Returns successful HTTP response"""
        
    def simulate_error_response(self, status_code):
        """Returns error response with specified status"""
        
    def simulate_timeout(self):
        """Simulates network timeout"""
        
    def simulate_large_response(self, size_mb):
        """Returns large response for performance testing"""
```

### Database Mocking
- Transaction isolation for test independence
- Rollback mechanisms for clean test environments
- Performance monitoring for database operations
- Data integrity validation

## Development Usage

### For API Developers

This test module provides:

1. **Reference Implementation**: Shows proper HTTP request logging integration
2. **Validation Framework**: Ensures your API logging works correctly
3. **Performance Benchmarks**: Validates logging performance impact
4. **Error Handling Examples**: Demonstrates proper error logging patterns

### For Integration Testing

1. **End-to-End Validation**: Tests complete request/response logging workflows
2. **Cross-Module Testing**: Validates integration with other modules
3. **Production Simulation**: Tests realistic usage scenarios
4. **Monitoring Validation**: Ensures logging data is useful for monitoring

## Security Testing

### Data Privacy
- **Sensitive Data Filtering**: Testing removal of passwords, tokens
- **PII Protection**: Testing personal information filtering
- **Compliance Validation**: Testing GDPR/privacy compliance
- **Access Control**: Testing log access restrictions

### Security Scenarios
- **Authentication Failures**: Testing failed login attempt logging
- **Authorization Errors**: Testing permission denial logging
- **Injection Attempts**: Testing SQL/XSS injection attempt logging
- **Rate Limiting**: Testing abuse detection and logging

## Installation

**Note**: This is a test module and should only be installed in development/testing environments.

### Requirements
1. Install only in test/development environments
2. Requires `kw_http_request_log` and `generic_mixin` modules
3. Provides test models and mock services
4. Should never be installed in production

### Test Environment Setup
```bash
# Create test database
createdb test_http_request_log

# Install with test modules
odoo-helper --db test_http_request_log install test_kw_http_request_log

# Run test suite
odoo-helper test --db test_http_request_log --module test_kw_http_request_log
```

## Compatibility

- **Odoo Version**: 18.0
- **Module Version**: 18.0.1.1.1
- **Category**: Extra Tools (Test Module)
- **License**: OPL-1
- **Dependencies**: `kw_http_request_log`, `generic_mixin`

## Configuration

### Test Settings
```python
# Test configuration
TEST_HTTP_TIMEOUT = 5  # seconds
TEST_MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
TEST_LOG_RETENTION_DAYS = 1  # Keep test logs for 1 day
TEST_CONCURRENT_REQUESTS = 10
```

### Logging Levels
- **DEBUG**: Detailed test execution information
- **INFO**: Test progress and results
- **WARNING**: Test warnings and performance issues
- **ERROR**: Test failures and critical errors

## Continuous Integration

### Automated Testing Pipeline
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Cross-module functionality testing
3. **Performance Tests**: Load and stress testing
4. **Security Tests**: Vulnerability and compliance testing
5. **Regression Tests**: Ensuring existing functionality remains intact

### Quality Metrics
- **Code Coverage**: Minimum 90% coverage required
- **Performance Benchmarks**: Response time and memory usage limits
- **Error Rate**: Maximum acceptable error rates for different scenarios
- **Documentation Coverage**: All test scenarios must be documented

## Contributing

### Adding New Tests

1. **Test Naming**: Follow `test_<functionality>_<scenario>` convention
2. **Documentation**: Include docstrings explaining test purpose
3. **Assertions**: Use descriptive assertion messages
4. **Cleanup**: Ensure proper test data cleanup

### Test Guidelines

- Write both positive and negative test cases
- Include edge cases and boundary conditions
- Test error handling and recovery scenarios
- Validate performance implications
- Ensure test independence and repeatability

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
