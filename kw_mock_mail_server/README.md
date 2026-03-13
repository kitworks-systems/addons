# Mock Mail Server

## Overview
The Mock Mail Server module provides a comprehensive toolset for testing incoming email processing in Odoo. It allows developers and testers to emulate receiving emails without the need for actual email servers, making it easier to test and debug email-related functionality.

## Features
- **Test Email Creation**: Create mock emails with custom subjects, senders, recipients, and body content
- **Email Processing Simulation**: Emulate the process of receiving and processing emails through Odoo's mail gateway
- **Integration Testing**: Test email-based workflows such as:
  - Lead creation from emails
  - User assignment based on email recipients
  - Email routing and processing rules
- **Debugging Tools**: Track the processing status and results of test emails
- **Error Handling**: Capture and display errors that occur during email processing

## Technical Details
The module extends Odoo's fetchmail functionality by adding a new server type called "Odoo Test Server" which doesn't require actual connection to an email server. Instead, it processes mock emails created within the system.

## Usage

### Setting up a Test Mail Server
1. Go to Settings > Technical > Email > Incoming Mail Servers
2. Create a new server with type "Odoo Test Server"
3. Configure the target model that should process the incoming emails
4. Set the server to "Confirmed" state

### Creating and Processing Test Emails
1. Navigate to the test emails interface through the test server
2. Create a new test email with required fields (From, To, Subject, Body)
3. Queue the email for processing or process it immediately
4. Review the processing results and any created records

### Monitoring and Debugging
- Track the state of test emails (Draft, Queued, Processing, Processed, Error)
- View detailed processing logs for each test email
- Check error messages when processing fails
- See which records were created and which users were assigned

## Integration
This module integrates with Odoo's standard mail processing system and can be used to test any module that processes incoming emails, such as CRM lead creation, support ticket generation, or custom email-based workflows.

## Dependencies
- fetchmail

## Technical Information
- Version: 15.0.1.0.0
- License: LGPL-3
- Author: Kitworks Systems
