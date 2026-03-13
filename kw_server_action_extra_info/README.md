# Server Action Extra Info

This module restores Server Action functionality that was available in Odoo 16 but removed in Odoo 17.

## Features

* **Data to Write Tab**: Configure field-value mappings for 'Create a new Record' and 'Update the Record' server actions
* **Security Tab**: Restrict server action execution to specific user groups
* **Multiple Value Types**: Support for direct values, record references, and Python expressions
* **Seamless Integration**: Works with existing server actions without migration

## Use Cases

* Automate record creation with predefined field values
* Update records based on dynamic Python expressions
* Reference existing records in field assignments
* Control which user groups can execute specific server actions

## Configuration

1. Install the module
2. Navigate to Settings -> Technical -> Automation -> Server Actions
3. Create or edit a server action with type "Create a new Record" or "Update the Record"
4. Use the "Data to Write" tab to configure field mappings
5. Use the "Security" tab to restrict access to specific user groups

## Value Types

* **Value**: Direct text value to be written to the field
* **Reference**: Select an existing record to link
* **Python expression**: Dynamic value using Python code with access to `record`, `env`, `time`, `datetime`, etc.

## Bug Tracker

Bugs are tracked on [https://kitworks.systems/requests](https://kitworks.systems/requests). In case of trouble, please check there if your issue has already been reported.

## Maintainer

KitWorks Systems - [https://kitworks.systems](https://kitworks.systems)

We provide Odoo Support, implementation, customization, 3rd Party development and integration software, consulting services.

For any questions [contact us](mailto:info@kitworks.systems).
