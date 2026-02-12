# KW Widget Autocomplete

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)

Universal autocomplete widget for Odoo 18 with support for multiple data sources. This widget can be used on `char` and `text` fields to provide autocomplete functionality from various backends.

## Key Features

- **Multiple Data Sources**
    - Model Method - call any Odoo model method for suggestions
    - Domain Search - search records using domain filters
    - JSON Endpoint - fetch suggestions from Odoo controllers
    - REST API - integrate with external REST APIs (via proxy)

- **Advanced Options**
    - Cascading dependencies between fields
    - Field mapping for auto-filling related fields
    - Custom callback methods on selection
    - Configurable minimum characters and cache size

## Data Sources

### Model Method

Call a method on any Odoo model to get autocomplete suggestions.

```xml
<field name="city"
       widget="kw_autocomplete"
       options="{
           'source_type': 'model_method',
           'source_config': {
               'model': 'res.city',
               'method': 'autocomplete_search'
           },
           'min_chars': 2
       }"/>
```

The method should return a list of dictionaries:

```python
@api.model
def autocomplete_search(self, query, dep_values=None):
    return [{
        'label': 'Display Text',
        'value': 'Value to save',
        'data': {'extra': 'data'},
    }]
```

### Domain Search

Search records directly using domain filters.

```xml
<field name="partner_name"
       widget="kw_autocomplete"
       options="{
           'source_type': 'domain_search',
           'source_config': {
               'model': 'res.partner',
               'domain': [['is_company', '=', true]],
               'search_field': 'name',
               'display_fields': ['name', 'email'],
               'label_template': '{name} ({email})',
               'value_field': 'name',
               'limit': 10
           },
           'min_chars': 2
       }"/>
```

### JSON Endpoint

Fetch suggestions from an Odoo controller endpoint.

```xml
<field name="product"
       widget="kw_autocomplete"
       options="{
           'source_type': 'json_endpoint',
           'source_config': {
               'endpoint': '/shop/autocomplete',
               'query_param': 'q'
           }
       }"/>
```

### REST API

Integrate with external REST APIs through a proxy method.

```xml
<field name="address"
       widget="kw_autocomplete"
       options="{
           'source_type': 'rest_api',
           'source_config': {
               'credential_model': 'my.api.credential',
               'proxy_method': 'autocomplete_proxy',
               'endpoint': '/api/search',
               'label_field': 'name'
           }
       }"/>
```

## Widget Options

| Option | Type | Description |
|--------|------|-------------|
| `source_type` | string | Data source type: `model_method`, `domain_search`, `json_endpoint`, `rest_api` |
| `source_config` | object | Configuration specific to the data source |
| `min_chars` | int | Minimum characters before search (default: 2) |
| `cache_size` | int | LRU cache size for results (default: 50) |
| `depends_on` | array | Field names for cascading dependencies |
| `on_select_method` | string | Model method to call when option is selected |
| `field_mapping` | object | Map option data fields to record fields |

## Usage Examples

### Cascading Dependencies

```xml
<field name="country_id"/>
<field name="city"
       widget="kw_autocomplete"
       options="{
           'source_type': 'model_method',
           'source_config': {
               'model': 'res.city',
               'method': 'search_by_country'
           },
           'depends_on': ['country_id']
       }"/>
```

### Field Mapping

Auto-fill related fields when an option is selected:

```xml
<field name="partner_name"
       widget="kw_autocomplete"
       options="{
           'source_type': 'domain_search',
           'source_config': {
               'model': 'res.partner',
               'search_field': 'name',
               'display_fields': ['name', 'email', 'phone'],
               'value_field': 'name'
           },
           'field_mapping': {
               'partner_email': 'email',
               'partner_phone': 'phone'
           }
       }"/>
<field name="partner_email" readonly="1"/>
<field name="partner_phone" readonly="1"/>
```

### Custom Callback Method

```xml
<field name="address"
       widget="kw_autocomplete"
       options="{
           'source_type': 'model_method',
           'source_config': {
               'model': 'my.model',
               'method': 'autocomplete_address'
           },
           'on_select_method': 'apply_address_selection'
       }"/>
```

```python
@api.model
def apply_address_selection(self, record_id, data):
    return {
        'street': data.get('street'),
        'city': data.get('city'),
        'zip': data.get('zip'),
    }
```

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
