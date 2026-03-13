# API Connector Module

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: API_Connector](https://img.shields.io/badge/docs-API_Connector-yellowgreen.png)](https://kitworks.systems/)

This module provides a framework for creating API connectors in Odoo. It can be used by developers to easily implement integrations with external APIs while maintaining consistent logging and error handling.

The module consists of two main abstract models that can be inherited to create specific API integrations:

## Key Features

- **API Connector Model**
    - Base configuration for API endpoints
    - Token management system
    - Flexible authentication methods

- **API Credentials Model**
    - Secure credential storage
    - Company-specific configurations
    - Integration with HTTP request logging

## Usage Examples

1. Create your API connector model:
   
   ```python
   class MyAPIConnector(models.Model):
       _name = 'my.api.connector'
       _inherit = 'kw.api.connector'
       _description = 'My API Connector'
   ```

2. Create your API credentials model:

   ```python
   class MyAPICredential(models.Model):
       _name = 'my.api.credential'
       _inherit = ['kw.api.credential',
                  'generic.mixin.transaction.utils',
                  'kw.http.request.log.source.mixin']
       _description = 'My API Credentials'

       api_connector_id = fields.Many2one(
           'my.api.connector',
           required=True)
   ```

3. Make API requests:

   ```python
   response = credentials.api_request(
       method='GET',
       url='/endpoint',
       headers={'Content-Type': 'application/json'})

   if credentials.is_api_success(response):
       data = response.json()
   ```

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
