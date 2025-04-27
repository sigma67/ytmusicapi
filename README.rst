ytmusicapi: Unofficial API for YouTube Music
############################################

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/ytmusicapi?style=flat-square
    :alt: PyPI Downloads
    :target: https://pypi.org/project/ytmusicapi/

.. |gitter| image:: https://badges.gitter.im/sigma67/ytmusicapi.svg
   :alt: Ask questions at https://gitter.im/sigma67/ytmusicapi
   :target: https://gitter.im/sigma67/ytmusicapi

.. |code-coverage| image:: https://img.shields.io/codecov/c/github/sigma67/ytmusicapi?style=flat-square
    :alt: Code coverage
    :target: https://codecov.io/gh/sigma67/ytmusicapi

.. |latest-release| image:: https://img.shields.io/github/v/release/sigma67/ytmusicapi?style=flat-square
    :alt: Latest release
    :target: https://github.com/sigma67/ytmusicapi/releases/latest

.. |commits-since-latest| image:: https://img.shields.io/github/commits-since/sigma67/ytmusicapi/latest?style=flat-square
    :alt: Commits since latest release
    :target: https://github.com/sigma67/ytmusicapi/commits


|pypi-downloads| |gitter| |code-coverage| |latest-release| |commits-since-latest|

ytmusicapi is a Python 3 library to send requests to the YouTube Music API.
It emulates YouTube Music web client requests using the user's cookie data for authentication.

.. features

Features
--------

| **Browsing**:

* search (including all filters) and suggestions
* get artist information and releases (songs, videos, albums, singles, related artists)
* get user information (videos, playlists)
* get albums
* get song metadata
* get watch playlists (next songs when you press play/radio/shuffle in YouTube Music)
* get song lyrics

| **Exploring music**:

* get moods and genres playlists
* get latest charts (globally and per country)

| **Library management**:

* get library contents: playlists, songs, artists, albums and subscriptions, podcasts, channels
* add/remove library content: rate songs, albums and playlists, subscribe/unsubscribe artists
* get and modify play history

| **Playlists**:

* create and delete playlists
* modify playlists: edit metadata, add/move/remove tracks
* get playlist contents
* get playlist suggestions

| **Podcasts**:

* get podcasts
* get episodes
* get channels
* get episodes playlists

| **Uploads**:

* upload songs and remove them again
* list uploaded songs, artists and albums

| **Localization**:

* all regions are supported (see `locations FAQ <https://ytmusicapi.readthedocs.io/en/stable/faq.html#which-values-can-i-use-for-locations>`__
* 16 languages are supported (see `languages FAQ <https://ytmusicapi.readthedocs.io/en/stable/faq.html#which-values-can-i-use-for-languages>`__


If you find something missing or broken,
check the `FAQ <https://ytmusicapi.readthedocs.io/en/stable/faq.html>`__ or
feel free to create an `issue <https://github.com/sigma67/ytmusicapi/issues/new/choose>`__.

Requirements
------------

- Python 3.10 or higher - https://www.python.org

Setup
-----

See the `Documentation <https://ytmusicapi.readthedocs.io/en/stable/usage.html>`_ for detailed instructions

Usage
------
.. code-block:: python

    from ytmusicapi import YTMusic

    yt = YTMusic('oauth.json')
    playlistId = yt.create_playlist('test', 'test description')
    search_results = yt.search('Oasis Wonderwall')
    yt.add_playlist_items(playlistId, [search_results[0]['videoId']])

The `tests <https://github.com/sigma67/ytmusicapi/blob/master/tests/>`_ are also a great source of usage examples.

.. end-features

Contributing
------------

Pull requests are welcome. There are still some features that are not yet implemented.
Please, refer to `CONTRIBUTING.rst <https://github.com/sigma67/ytmusicapi/blob/master/CONTRIBUTING.rst>`_ for guidance.
