# Testing Documentation for kw_crm_responsible_by_recipient

## Overview

This module contains comprehensive tests for the CRM Auto Assign Responsible by Email functionality.

## Test Structure

### test_crm_lead.py
Unit tests for the core functionality:
- `TestCrmLeadResponsibleByRecipient` - 25 unit tests covering:
  - Email search functionality
  - User matching by login and partner email
  - Priority handling (to vs recipients)
  - Edge cases and error handling
  - Email normalization
  - Multiple email parsing

### test_integration.py
Integration tests for real-world scenarios:
- `TestCrmLeadIntegration` - 13 integration tests covering:
  - End-to-end lead creation workflow
  - Complex email parsing scenarios
  - Performance with multiple emails
  - Custom values integration
  - Case insensitive matching
  - Concurrent lead creation

## Total Test Coverage

**38 tests** covering:
- ✅ Core email search functionality
- ✅ User matching algorithms
- ✅ Priority handling
- ✅ Email normalization
- ✅ Error handling
- ✅ Edge cases
- ✅ Integration scenarios
- ✅ Performance considerations

## Running Tests

### Run all tests for the module:
```bash
odoo-helper test -m kw_crm_responsible_by_recipient --create-test-db
```

### Run with coverage:
```bash
odoo-helper test -m kw_crm_responsible_by_recipient --create-test-db --coverage-html
```

### Run specific test class:
```bash
odoo-helper test -m kw_crm_responsible_by_recipient --create-test-db -k TestCrmLeadResponsibleByRecipient
```

## Test Scenarios Covered

### Email Search Tests
1. **Empty/None email strings** - Handles gracefully
2. **Single email matching** - By login and partner email
3. **Multiple emails** - Finds first matching user
4. **No matches** - Returns False appropriately
5. **Inactive users** - Correctly excludes them
6. **Malformed emails** - Handles invalid formats

### User Assignment Tests
7. **'to' field priority** - Takes precedence over recipients
8. **Recipients fallback** - When 'to' has no match
9. **No user assignment** - When no emails match
10. **Custom values integration** - Works with additional data

### Integration Tests
11. **End-to-end workflow** - Complete lead creation process
12. **Partner email matching** - Users found by partner email
13. **Complex email formats** - Handles display names, etc.
14. **Case insensitive** - Uppercase/lowercase emails work
15. **Performance** - Efficient with many emails

### Edge Cases
16. **Empty message dict** - Minimal required data
17. **Missing email fields** - Handles absent to/recipients
18. **Whitespace handling** - Cleans email formatting
19. **Email normalization** - Proper email standardization
20. **Priority conflicts** - Correct user selection order

## Expected Results

All tests should pass with:
- ✅ 0 failures
- ✅ 0 errors
- ✅ Complete functionality coverage
- ✅ Performance validation
- ✅ Error handling verification

## Test Data

Tests create realistic test data:
- Multiple users with different email configurations
- Active and inactive users
- Users with partner emails different from login
- Sales teams and CRM-related data
- Complex email message dictionaries

## Dependencies

Tests require:
- `crm` module (CRM functionality)
- `mail` module (email processing)
- Standard Odoo test framework
- TransactionCase for database transactions
