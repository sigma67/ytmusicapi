Setup
=====
.. code-block:: bash

    pip install ytmusicapi

**Authenticated requests**

To run authenticated requests you need to copy your request headers from a POST request in your YTMusic Web Client.

To do so, follow these steps:

    - Copy ``headers_auth.json.example`` to ``headers_auth.json``
    - Open YTMusic in Firefox
    - Go to the developer tools (Ctrl-Shift-I) and right click a POST request.
    - Copy the request headers (right click > copy > copy request headers)
    - Paste the three missing items to `headers_auth.json`