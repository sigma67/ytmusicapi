ytmusicapi: Unofficial API for YouTube Music
============================================

A work-in-progress API that emulates web requests from the YouTube Music web client.

Currently you need to extract your authentication data from your web browser and provide it through a file for it to work.

Note: I have not tested this with any account other than my own. Please let me know if it works for you.

Simple usage example:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')
    playlistId = ytmusic.create_playlist("test", "test description")
    search_results = ytmusic.search("Oasis Wonderwall")
    ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId'])

Requirements
==============

- Python 3 - https://www.python.org

Setup
=======

``pip install git+https://github.com/sigma67/ytmusicapi``

**Authenticated requests**

To run authenticated requests you need to copy your request headers from a POST request in your YTMusic Web Client. 

To do so, follow these steps: 
    - Copy ``headers_auth.json.example`` to ``headers_auth.json``
    - Open YTMusic in Firefox
    - Go to the developer tools (Ctrl-Shift-I) and right click a POST request.
    - Copy the request headers (right click > copy > copy request headers)
    - Paste the three missing items to `headers_auth.json`

Usage
=======

Unauthenticated requests for retrieving playlist content or searching:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic()



Authenticated request to interact with your playlist (requires setting up your credentials in ``headers_auth.json``):

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')


Contributing
==============

Pull requests are welcome. There are still lots of features unimplemented, for example retrieving content from the library and other parts of YTMusic.
