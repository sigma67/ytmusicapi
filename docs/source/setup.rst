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
    - Go to the developer tools (Ctrl-Shift-I) and open the "Network" tab.
    - Find an authenticated POST request (Status: 200, Method: POST, Domain: music.youtube.com, File: log_event?...). You can filter for /browse to easily find a suitable request.
    - Copy the request headers (right click > copy > copy request headers)

Now open a python console and call :py:func:`YTMusic.setup` with the parameter ``filepath=headers_auth.json`` and follow the instructions and paste the request headers to the terminal input:

.. code-block:: python

    from ytmusicapi import YTMusic
    YTMusic.setup(filepath=headers_auth.json)

If you don't want terminal interaction you can pass the request headers with the ``headers_raw`` parameter:

.. code-block:: python

    from ytmusicapi import YTMusic
    YTMusic.setup(filepath=headers_auth.json, headers_raw="very long string")
    
The function returns a JSON string with the credentials needed for :doc:`Usage <usage>`. Alternatively, if you passed the filepath parameter as described above,
a file called ``headers_auth.json`` will be created in the current directory, which you can pass to ``YTMusic()`` for authentication.

These credentials remain valid as long as your YTMusic browser session is valid (about 2 years unless you log out).

Manual file creation
--------------------

Alternatively, you can paste the cookie to ``headers_auth.json`` below and create your own file:

.. literalinclude:: ../../headers_auth.json.example
  :language: JSON
