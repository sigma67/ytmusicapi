Setup
=====

Installation
------------
.. code-block:: bash

    pip install ytmusicapi

Authenticated requests
----------------------

To run authenticated requests you need to set up you need to copy your request headers from a POST request in your YTMusic Web Client.
To do so, follow these steps:

    - Open https://music.youtube.com in Firefox
    - Go to the developer tools (Ctrl-Shift-I) and find an authenticated POST request. You can filter for /browse to easily find a suitable request.
    - Copy the request headers (right click > copy > copy request headers)

Now call :py:func:`YTMusic.setup()` and paste the request headers and it will create configuration file
in the correct format in the current directory.

Manual file creation
--------------------

Alternatively, you can paste the cookie to `headers_auth.json` below and create your own file:

.. literalinclude:: ../../headers_auth.json.example
  :language: JSON