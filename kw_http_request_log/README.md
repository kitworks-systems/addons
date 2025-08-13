# HTTP Request Log Module

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: HTTP_Request_Log](https://img.shields.io/badge/docs-HTTP_Request_Log-yellowgreen.png)](https://kitworks.systems/)

This module provides functionality to log and track HTTP requests in Odoo. It allows storing and managing HTTP request logs with their sources, making it easier to monitor and analyze HTTP traffic in your Odoo instance.

## Key Features

- **HTTP Request Logging**
    - Detailed request information storage
    - Headers and parameters tracking
    - Response status monitoring
    - Large payload handling

- **Source Management**
    - Multiple source support
    - Source-specific retention policies
    - Active/inactive source tracking

- **Automatic Maintenance**
    - Configurable log retention
    - Automatic cleanup of old records
    - Smart storage management

## Usage Examples

1. Create a Log Source:
   
   ```python
   source_id = env['kw.http.request.log.source'].create({
       'name': 'My API Integration',
       'code': 'my_api',
       'active': True,
       'keep_days': 30,  # Keep logs for 30 days
   })
   ```

2. Log a Request:

   ```python
   env['kw.http.request.log'].create_in_new_transaction({
       'log_source_id': source_id.id,
       'method': 'POST',
       'url': 'https://api.example.com/endpoint',
       'request_body': request_data,
       'response_status': 200,
       'response_body': response_data,
   })
   ```

3. Use with HTTP Controller:

   ```python
   from odoo import http
   from odoo.http import request

   class MyController(http.Controller):
       @http.route('/my/endpoint', auth='public')
       def my_endpoint(self):
           source = request.env.ref('my_module.my_source')
           return source.log_request(
               request=request,
               response=response)
   ```

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
