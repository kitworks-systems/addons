# Many2Many Click

[![License: OPL-1](https://img.shields.io/badge/license-OPL--1-blue.svg)](https://www.odoo.com/documentation/18.0/legal/licenses.html#odoo-apps)
[![Odoo: 18.0](https://img.shields.io/badge/Odoo-18.0-brightgreen)](https://github.com/odoo/odoo/tree/18.0)

## Description

`kw_many2many_click` is an Odoo 18 web widget for `many2many` fields.

It extends the standard tag-like many2many UI and adds one key behavior:
- click on the item text to open the related record form.

The remove (unlink) behavior remains standard and unchanged.

## Features

- Works with any `many2many` field (not only tags models)
- Keeps native `many2many_tags`-style rendering
- Opens related record form on text click (in current tab)
- Preserves standard unlink/delete icon behavior
- Supports common creation options:
  - `no_create`
  - `no_quick_create`
  - `no_create_edit`
  - `create`
  - `color_field`
- Widget name: `many2many_click`

## Installation

1. Copy module `kw_many2many_click` into your addons path
2. Update Apps List in Odoo
3. Install **Many2many Clickable Records** from Apps

## Usage

Use in form/tree XML views:

```xml
<field name="lot_ids" widget="many2many_click"/>
```

With options:

```xml
<field
    name="lot_ids"
    widget="many2many_click"
    options="{
        'no_create': True,
        'no_quick_create': True,
        'no_create_edit': False,
        'color_field': 'color'
    }"
/>
```

## How it works

1. The widget renders related records in tag-like items
2. Clicking item text triggers an `ir.actions.act_window` form action
3. Odoo opens the related record of the many2many relation in current tab
4. Clicking the delete icon only unlinks the relation (standard behavior)

## Technical details

- Frontend only module (`web` dependency)
- Extends `Many2ManyTagsField`
- Uses custom OWL list component for clickable labels
- Assets are loaded via `web.assets_backend`

## Dependencies

- `web`

## Version

- `18.0.1.1.0`

## License

- OPL-1

## Author

[Kitworks Systems](https://kitworks.systems/)
