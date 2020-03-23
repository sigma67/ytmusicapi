ytmusicapi: Unofficial API for YouTube Music
============================================

A work-in-progress API that emulates web requests from the YouTube Music web client.

Currently you need to extract your authentication data from your web browser and provide it through a file for it to work.

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

Setup and Usage
===============

See the `Documentation <https://ytmusicapi.readthedocs.io/en/latest/usage.html>`_ for detailed instructions

Contributing
==============

Pull requests are welcome. There are still lots of features unimplemented, for example retrieving content from the library and other parts of YTMusic.
