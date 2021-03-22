ytmusicapi: Unofficial API for YouTube Music
############################################

.. image:: https://img.shields.io/pypi/dm/ytmusicapi?style=flat-square
    :alt: PyPI Downloads
    :target: https://pypi.org/project/ytmusicapi/

.. image:: https://badges.gitter.im/sigma67/ytmusicapi.svg
   :alt: Ask questions at https://gitter.im/sigma67/ytmusicapi
   :target: https://gitter.im/sigma67/ytmusicapi

.. image:: https://img.shields.io/codecov/c/github/sigma67/ytmusicapi?style=flat-square
    :alt: Code coverage
    :target: https://codecov.io/gh/sigma67/ytmusicapi

.. image:: https://img.shields.io/github/v/release/sigma67/ytmusicapi?style=flat-square
    :alt: Latest release
    :target: https://github.com/sigma67/ytmusicapi/releases/latest

.. image:: https://img.shields.io/github/commits-since/sigma67/ytmusicapi/latest?style=flat-square
    :alt: Commits since latest release
    :target: https://github.com/sigma67/ytmusicapi/commits


ytmusicapi is a Python 3 library to send requests to the YouTube Music API.
It emulates YouTube Music web client requests using the user's cookie data for authentication.

.. features

Features
--------
| **Browsing**:

* search (including all filters)
* get artist information and releases (songs, videos, albums, singles, related artists)
* get user information (videos, playlists)
* get albums
* get song metadata
* get watch playlists (playlist that appears when you press play in YouTube Music)
* get song lyrics

| **Library management**:

* get library contents: playlists, songs, artists, albums and subscriptions
* add/remove library content: rate songs, albums and playlists, subscribe/unsubscribe artists

| **Playlists**:

* create and delete playlists
* modify playlists: edit metadata, add/move/remove tracks
* get playlist contents

| **Uploads**:

* Upload songs and remove them again
* List uploaded songs, artists and albums


Usage
------
.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')
    playlistId = ytmusic.create_playlist('test', 'test description')
    search_results = ytmusic.search('Oasis Wonderwall')
    ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId']])

The `tests <https://github.com/sigma67/ytmusicapi/blob/master/tests/test.py>`_ are also a great source of usage examples.

.. end-features

Requirements
==============

- Python 3.5 or higher - https://www.python.org

Setup and Usage
===============

See the `Documentation <https://ytmusicapi.readthedocs.io/en/latest/usage.html>`_ for detailed instructions

Contributing
==============

Pull requests are welcome. There are still some features that are not yet implemented.
Please, refer to `CONTRIBUTING.rst <https://github.com/sigma67/ytmusicapi/blob/master/CONTRIBUTING.rst>`_ for guidance.