# Chatter User Comment Only

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: Chatter_User_Comment_Only](https://img.shields.io/badge/docs-Chatter_User_Comment_Only-yellowgreen.png)](https://kitworks.systems/)

This module modifies the chatter functionality to show only user-created messages and hide system-generated messages for a cleaner communication view.

## Features

- **Filtered Message Display**: Only shows messages of type 'comment' in the chatter
- **Hide System Messages**: Automatically filters out system-generated notifications, status updates, and automated messages
- **Clean Communication View**: Provides a focused view of actual user conversations
- **Seamless Integration**: Works with existing chatter functionality without breaking other features

## How It Works

The module overrides the `_message_fetch` method in the `mail.message` model to automatically add a domain filter that only includes messages with `message_type = 'comment'`. This ensures that:

- User comments and manual posts are displayed
- System notifications (like status changes, field updates) are hidden
- Automated messages from workflows are filtered out
- The chatter remains clean and focused on human communication

## Installation

1. Install the module through the Odoo Apps menu
2. No additional configuration is required
3. The filtering will be applied automatically to all chatter instances

## Usage

Once installed, the module works automatically:

1. Navigate to any record with a chatter (e.g., Sales Orders, Invoices, Projects)
2. The chatter will only display user-generated comments
3. System messages will be hidden from view but remain in the database
4. Users can continue to post comments normally

## Technical Details

- **Modified Model**: `mail.message`
- **Override Method**: `_message_fetch()`
- **Filter Applied**: `[('message_type', '=', 'comment')]`
- **Dependencies**: `mail` module

## Use Cases

- **Customer Service**: Focus on actual customer communication without system noise
- **Project Management**: See only team discussions and important updates
- **Sales Process**: Track meaningful conversations with prospects and clients
- **Support Tickets**: Maintain clean communication threads

## Compatibility

- **Odoo Version**: 18.0
- **Module Version**: 18.0.0.1.2
- **Category**: Social
- **License**: LGPL-3

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
