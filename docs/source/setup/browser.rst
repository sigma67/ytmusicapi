Browser authentication
======================

This method of authentication emulates your browser session by reusing its request headers.
Follow the instructions to have your browser's YouTube Music session request headers parsed 
to a ``ytmusicapi`` configuration file.

Copy authentication headers
---------------------------

To run authenticated requests, set it up by first copying your request headers from an authenticated POST request in your browser.
To do so, follow these steps:

- Open a new tab
- Open the developer tools (Ctrl-Shift-I) and select the "Network" tab
- Go to https://music.youtube.com and ensure you are logged in
- Find an authenticated POST request. The simplest way is to filter by ``/browse`` using the search bar of the developer tools.
  If you don't see the request, try scrolling down a bit or clicking on the library button in the top bar.

.. raw:: html

   <details open>
   <summary><a>Firefox (recommended)</a></summary>

.. container::

    - Verify that the request looks like this: **Status** 200, **Method** POST, **Domain** music.youtube.com, **File** ``browse?...``
    - Copy the request headers (right click > copy > copy request headers)

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>Chromium (Chrome/Edge)</a></summary>

.. container::

    - Verify that the request looks like this: **Status** 200, **Name** ``browse?...``
    - Click on the Name of any matching request. In the "Headers" tab, scroll to the section "Request headers" and copy everything starting from "accept: \*/\*" to the end of the section

.. raw:: html

   </details><br>

Using the headers in your project
---------------------------------

To set up your project, open a console and call

.. code-block:: bash

    ytmusicapi browser

Follow the instructions and paste the request headers to the terminal input.

If you don't want terminal interaction in your project, you can pass the request headers with the ``headers_raw`` parameter:

.. code-block:: python

    import ytmusicapi
    ytmusicapi.setup(filepath="browser.json", headers_raw="<headers copied above>")

The function returns a JSON string with the credentials needed for :doc:`../usage`. Alternatively, if you passed the filepath parameter as described above,
a file called ``browser.json`` will be created in the current directory, which you can pass to ``YTMusic()`` for authentication.

These credentials remain valid as long as your YTMusic browser session is valid (about 2 years unless you log out).

.. raw:: html

   <details>
   <summary><a>MacOS special pasting instructions</a></summary>

.. container::

    - MacOS terminal application can only accept 1024 characters pasted to std input. To paste in terminal, a small utility called pbpaste must be used.
    - In terminal just prefix the command used to run the script you created above with
        ``pbpaste |``
    - This will pipe the contents of the clipboard into the script just as if you had pasted it from the edit menu.

.. raw:: html

   </details><br>

Manual file creation
--------------------

Alternatively, you can create your own file ``browser.json`` and paste the cookie:

.. literalinclude:: headers_auth.json.example
  :language: JSON
