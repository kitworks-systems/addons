# CRM Auto Assign Responsible by Email

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo: 15.0](https://img.shields.io/badge/Odoo-15.0-brightgreen)](https://github.com/odoo/odoo/tree/15.0)

## Description

This module automatically assigns a responsible user to CRM leads created from incoming emails based on the email recipient.

## Features

- Automatically assigns responsible user based on email recipient
- First searches for users with matching email addresses in the 'to' field
- If no match is found in the 'to' field, searches in the 'recipients' field
- Only assigns active users
- Preserves existing CRM behavior when no matching user is found
- Detailed logging for debugging purposes

## How it works

1. When an email is received and processed to create a CRM lead
2. The module searches for active users whose email matches any of the recipients
3. Priority order:
   - First checks recipients in the 'to' field
   - Then checks the 'recipients' field (includes CC, BCC, etc.)
4. If a matching user is found, they are assigned as the responsible user
5. If no matching user is found, the lead is created without a responsible user (standard behavior)

## Installation

1. Copy the module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the module from Apps menu

## Configuration

No configuration required. The module works automatically once installed.

## Technical Details

- Overrides the `message_new` method in the `crm.lead` model
- Uses `email_normalize` for proper email matching
- Includes comprehensive logging for troubleshooting
- Maintains compatibility with standard CRM workflow

## Dependencies

- crm
- mail

## Version

15.0.1.0.0

## License

LGPL-3

## Author

[KW Development](https://kitworks.systems/) - info@kitworks.systems
