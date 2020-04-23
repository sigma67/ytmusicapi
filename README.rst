ytmusicapi: Unofficial API for YouTube Music
============================================
.. image:: https://img.shields.io/pypi/dw/ytmusicapi?style=flat-square
    :alt PyPI Downloads

.. image:: https://raw.githubusercontent.com/sigma67/ytmusicapi/master/tests/coverage.svg
    :alt Code coverage

A work-in-progress API that emulates web requests from the YouTube Music web client.

Currently you need to extract your authentication data from your web browser and provide it through a file for it to work.

Simple usage example:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')
    playlistId = ytmusic.create_playlist("test", "test description")
    search_results = ytmusic.search("Oasis Wonderwall")
    ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId']])

Features
--------
-  Browsing: get artist information and releases (songs, videos, albums, singles), get albums
-  Library management: list, create, delete, and modify playlists and playlist items
-  Search: Search for songs on YouTube Music
-  Uploads: Upload songs, list uploaded songs and delete uploaded songs

Requirements
==============

- Python 3.5 or higher - https://www.python.org

Setup and Usage
===============

See the `Documentation <https://ytmusicapi.readthedocs.io/en/latest/usage.html>`_ for detailed instructions

Contributing
==============

Pull requests are welcome. There are still some features that are not yet implemented.
