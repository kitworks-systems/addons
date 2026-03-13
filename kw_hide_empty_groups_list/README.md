# Hide Empty Groups in Grouped Lists

[![License: LGPL-3](https://img.shields.io/badge/license-LGPL--3-blue.png)](http://www.gnu.org/licenses/lgpl-3.0-standalone.html)
[![Maintainer: Kitworks](https://img.shields.io/badge/maintainer-Kitworks-purple.png)](https://kitworks.systems/)

This module hides empty groups in grouped list views for users who enable the setting in their profile.

## Features

- Adds user setting **Hide empty groups in grouped lists**
- Exposes this setting to frontend session (`session_info`)
- Registers custom list js_class: `kw_filtered_grouped_list`
- Filters out groups with no records/subgroups/count

## Usage

1. Install the module
2. Enable **Hide empty groups in grouped lists** on the user Preferences page
3. Use `js_class="kw_filtered_grouped_list"` in list views where grouping is used

Example:

```xml
<list js_class="kw_filtered_grouped_list">
    ...
</list>
```

## Bug Tracker

Bugs are tracked on [Kitworks Support](https://kitworks.systems/requests).

## Maintainer

[Kitworks Systems](https://kitworks.systems/)
