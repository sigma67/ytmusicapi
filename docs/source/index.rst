.. ytmusicapi documentation master file, created by
   sphinx-quickstart on Fri Feb 21 12:48:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ytmusicapi: Unofficial API for YouTube Music
==================================================
The purpose of this library is to automate interactions with `YouTube Music <https://music.youtube.com/>`_,
such as retrieving your library content or creating large playlists.

**This project is not supported nor endorsed by Google**

Features
--------
-  Library management: list, create, delete, and modify playlists and playlist items
-  Search: Search for songs on YouTube Music
-  Uploads: Upload songs, list uploaded songs and delete uploaded songs

Usage Example
-------------
For a complete documentation of available functions, refer to the :doc:`Reference <reference>`

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')
    playlistId = ytmusic.create_playlist("test", "test description")
    search_results = ytmusic.search("Oasis Wonderwall")
    ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId'])



Contents
--------

.. toctree::
   :hidden:

   Home <self>

.. toctree::

   setup
   usage
   reference
