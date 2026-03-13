=========================
HTML Image to Attachment
=========================

This module provides functionality to convert images from HTML fields to attachments.

Key Features
-------------
* Automatic conversion of external images and base64-encoded images to attachments
* Configurable task system to process specific models and fields
* Marking of attachments for tracking and management
* Cleaning of unused image attachments
* Support for both batch processing and individual record processing

Changes in version 16.0.2.0.0
-------------------------------
* Removed dependency on BeautifulSoup4, now using regex for HTML parsing
* Added fields parameter to mark_attachments and clean_unused_images methods
* Changed processing order: now marking attachments before processing images
* Improved error handling and logging
* Enhanced performance by reducing unnecessary operations

Bug Tracker
------------
Bugs are tracked on `GitHub Issues <https://github.com/kitworks-systems/kw_html_image2attachment/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
-------

Authors
~~~~~~~
* Kitworks Systems

Contributors
~~~~~~~~~~~~~
* Kitworks Systems Team <info@kitworks.systems>

Maintainers
~~~~~~~~~~~~
This module is maintained by Kitworks Systems.

.. image:: https://kitworks.systems/logo.png
   :alt: Kitworks Systems
   :target: https://kitworks.systems/
