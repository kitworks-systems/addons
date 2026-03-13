# Tree Checkbox Sticky

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)
[![Docs: Tree_Checkbox_Sticky](https://img.shields.io/badge/docs-Tree_Checkbox_Sticky-yellowgreen.png)](https://kitworks.systems/)

This module keeps the checkbox column fixed in list views while scrolling horizontally, making it easier to select multiple records in wide tables.

## Features

- **Fixed Checkbox Column**: The first column containing checkboxes stays visible during horizontal scrolling
- **Improved User Experience**: Users can always see and access record selection checkboxes
- **Visual Consistency**: Maintains proper background colors for header and data rows
- **Cross-browser Compatibility**: Works consistently across modern web browsers
- **Automatic Application**: Applied to all list views with checkboxes without configuration

## How It Works

The module uses CSS positioning to make the checkbox column sticky:

- **Position Sticky**: Uses `position: sticky` with `left: 0px` to fix the column
- **Z-index Management**: Ensures checkbox column appears above other content
- **Background Colors**: Maintains proper visual separation with background colors
- **Responsive Design**: Works with different screen sizes and table widths

## Visual Behavior

### Header Checkbox
- Stays fixed at the left edge during horizontal scroll
- Maintains header background color (`rgb(233, 236, 239)`)
- Remains clickable for "select all" functionality

### Row Checkboxes
- Each row's checkbox column remains visible while scrolling
- White background for normal rows
- Respects selected row highlighting (`table-info` styling)
- Individual selection remains functional

## Installation

1. Install the module through the Odoo Apps menu
2. No configuration required - works automatically
3. Refresh your browser to see the changes in list views

## Usage

Once installed, the module works automatically:

1. Navigate to any list view with many columns (e.g., Sales Orders, Invoices, Products)
2. Use horizontal scroll to navigate through columns
3. Notice that the checkbox column remains fixed on the left
4. Select individual records or use "select all" as usual
5. The checkboxes remain accessible regardless of scroll position

## Technical Implementation

### CSS Rules Applied

```css
/* Sticky positioning for checkbox cells */
html .o_web_client .o_content .table-responsive thead th:first-child:has(input[type="checkbox"]),
html .o_web_client .o_content .table-responsive tbody td:first-child:has(input[type="checkbox"]) {
    position: sticky !important;
    left: 0px !important;
    z-index: 2 !important;
}

/* Background colors for visual consistency */
html .o_web_client .o_content .table-responsive thead th:first-child {
    background-color: rgb(233, 236, 239);
}

html .o_web_client .o_content .table-responsive tbody td:first-child {
    background-color: #fff;
}

html .o_web_client .o_content .table-responsive tbody .table-info td:first-child {
    background-color: var(--table-bg);
}
```

## Use Cases

- **Wide Data Tables**: Product catalogs with many attributes
- **Financial Reports**: Invoices, payments with multiple columns
- **Inventory Management**: Stock movements with detailed information
- **CRM Data**: Lead/opportunity lists with extensive fields
- **Bulk Operations**: Selecting multiple records for batch actions

## Browser Support

- **Chrome**: Full support
- **Firefox**: Full support  
- **Safari**: Full support
- **Edge**: Full support
- **Mobile Browsers**: Responsive behavior maintained

## Compatibility

- **Odoo Version**: 18.0
- **Module Version**: 18.0.0.1.2
- **Category**: Extra Tools
- **License**: LGPL-3
- **Dependencies**: `web` module only

## Performance Impact

- **Minimal Overhead**: Only CSS modifications, no JavaScript processing
- **No Backend Changes**: Purely frontend enhancement
- **Fast Loading**: CSS loaded with standard web assets
- **Memory Efficient**: No additional JavaScript memory usage

## Related Modules

- **kw_tree_header_sticky**: Keeps table headers visible during vertical scrolling
- Together these modules provide complete table navigation enhancement

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).
In case of trouble, please check there if your issue has already been reported.

## Maintainer

This module is maintained by [Kitworks Systems](https://kitworks.systems).

We can provide you further Odoo Support, Odoo implementation, Odoo customization, Odoo 3rd Party development and integration software, consulting services. Our main goal is to provide the best quality product for you.

For any questions [contact us](mailto:support@kitworks.systems).
