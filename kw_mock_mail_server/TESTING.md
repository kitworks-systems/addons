# Testing Guide for Mock Mail Server

## Overview
This module includes comprehensive tests to ensure the mock mail server functionality works correctly. The tests cover unit testing, integration testing, and error handling scenarios.

## Test Structure

### Test Files
- `test_mock_email.py` - Tests for the `kw.mock.email` model
- `test_fetchmail_server.py` - Tests for the extended `fetchmail.server` model
- `test_integration.py` - End-to-end integration tests

### Test Categories

#### Unit Tests (`test_mock_email.py`)
- **Model Creation**: Test creating mock emails with various configurations
- **Validation**: Test required fields and validation rules
- **State Management**: Test state transitions (draft → queued → processing → processed/error)
- **Message Preparation**: Test raw message generation for email processing
- **Result Processing**: Test updating results after email processing
- **Error Handling**: Test error scenarios and recovery

#### Server Tests (`test_fetchmail_server.py`)
- **Server Type**: Test new server type registration
- **Connection**: Test connection methods for test servers
- **Email Processing**: Test fetch_mail method with various scenarios
- **Batch Processing**: Test processing multiple emails
- **Error Handling**: Test error scenarios during processing
- **Mixed Environments**: Test with both test and regular servers

#### Integration Tests (`test_integration.py`)
- **End-to-End Processing**: Complete workflow from email creation to record creation
- **User Assignment**: Test automatic user assignment based on email recipients
- **Batch Processing**: Test processing multiple emails in sequence
- **Error Recovery**: Test reset and reprocessing functionality
- **Multiple Servers**: Test multiple servers with different configurations

## Running Tests

### Prerequisites
- Ensure the module is installed in your Odoo instance
- CRM module should be installed for lead creation tests
- Test database should be available

### Running All Tests
```bash
# Run all tests for the module
odoo-helper test -m kw_mock_mail_server

# Run with coverage
odoo-helper test --coverage-html -m kw_mock_mail_server
```

### Running Specific Test Classes
```bash
# Run only unit tests
python -m pytest addons/kw_mock_mail_server/tests/test_mock_email.py

# Run only integration tests
python -m pytest addons/kw_mock_mail_server/tests/test_integration.py
```

### Test Configuration
Tests use `TransactionCase` base class which provides:
- Database transaction rollback after each test
- Isolated test environment
- Access to Odoo environment and models

## Test Data

### Test Servers
Tests create temporary fetchmail servers with:
- Server type: `odoo_test_server`
- Target model: `crm.lead` (by default)
- State: `done` (confirmed)

### Test Emails
Tests create mock emails with:
- Various subject lines
- Different sender/recipient combinations
- Different body content
- Different states (draft, queued, processed, error)

### Test Users
Some tests create temporary users for:
- Testing user assignment functionality
- Testing email recipient matching
- Testing access rights

## Test Scenarios

### Basic Functionality
1. Create mock email
2. Queue for processing
3. Process through fetchmail
4. Verify record creation
5. Check processing logs

### Error Scenarios
1. Invalid email formats
2. Missing required fields
3. Processing failures
4. Connection errors
5. Permission issues

### Edge Cases
1. Empty email bodies
2. Very long subject lines
3. Multiple recipients
4. Duplicate processing
5. Concurrent processing

## Extending Tests

### Adding New Test Cases
1. Create test method in appropriate test class
2. Use descriptive test method names (test_specific_scenario)
3. Include docstrings explaining the test purpose
4. Use assertions to verify expected behavior

### Test Method Structure
```python
def test_specific_scenario(self):
    """Test description explaining what is being tested"""
    # Setup
    test_data = self.create_test_data()
    
    # Action
    result = test_data.perform_action()
    
    # Assertions
    self.assertEqual(result.state, 'expected_state')
    self.assertTrue(result.some_field)
    self.assertIn('expected_text', result.log_field)
```

### Mock and Patch Usage
Tests use `unittest.mock` for:
- Mocking external dependencies
- Simulating error conditions
- Controlling test environment
- Isolating units under test

## Common Test Patterns

### Setup Pattern
```python
def setUp(self):
    super().setUp()
    self.test_server = self.env['fetchmail.server'].create({
        'name': 'Test Server',
        'server_type': 'odoo_test_server',
        'state': 'done',
        'object_id': self.env.ref('crm.model_crm_lead').id,
    })
```

### Processing Pattern
```python
# Create mock email
mock_email = self.env['kw.mock.email'].create(email_data)

# Process email
mock_email.action_process_now()

# Verify results
self.assertEqual(mock_email.state, 'processed')
self.assertTrue(mock_email.res_id)
```

### Error Testing Pattern
```python
with self.assertRaises(UserError) as cm:
    mock_email.action_without_server()
    
self.assertIn('expected error message', str(cm.exception))
```

## Test Maintenance

### Regular Updates
- Update tests when adding new features
- Ensure tests cover all code paths
- Update test data when model changes
- Verify tests pass with different Odoo versions

### Performance Considerations
- Use `TransactionCase` for database tests
- Minimize database operations in tests
- Use mocking for external dependencies
- Keep test data minimal but sufficient

## Troubleshooting

### Common Issues
1. **Test Database**: Ensure test database is properly configured
2. **Dependencies**: Verify all required modules are installed
3. **Permissions**: Check that test user has necessary permissions
4. **Environment**: Ensure test environment matches production

### Debug Tips
- Use `pdb` for debugging failing tests
- Check test logs for detailed error information
- Use `--log-level=debug` for verbose output
- Verify test data setup is correct
