FAQ
=====

Frequently asked questions for ``ytmusicapi``. Contributions are welcome, please
`submit a PR <https://github.com/sigma67/ytmusicapi/pulls>`_.

Setup
------------

My library results are empty even though I set up my cookie correctly.
***********************************************************************
Please make sure that you don't have multiple Google accounts. ``ytmusicapi`` might be returning
results from a different account which is currently empty. You can set your account using ``X-Goog-AuthUser``
in your headers file (numeric index) or by providing the id of a brand account with ``ytmusic = YTMusic(headers, "1234..")``.
For more details see the :doc:`reference`.

Usage
-----------------------

How do I add a song, album, artist or playlist to my library?
***********************************************************************
- **songs**: `edit_song_library_status <Reference.html#ytmusicapi.YTMusic.edit_song_library_status>`__ .
  Liking a song using `rate_song <Reference.html#ytmusicapi.YTMusic.rate_song>`__
  does *not* add it to your library, only to your liked songs playlist.
- **albums, playlists**: `rate_playlist <Reference.html#ytmusicapi.YTMusic.rate_playlist>`__
- **artists**: `subscribe_artists <Reference.html#ytmusicapi.YTMusic.subscribe_artists>`__ .
  This will add the artist to your Subscriptions tab. The Artists tab is determined by the songs/albums you have
  added to your library.



How can I get the radio playlist for a song, video, playlist or album?
***********************************************************************
- **songs, videos**: ``RDAMVM`` + ``videoId``
- **playlists, albums**: ``RDAMPL`` + ``playlistId``


How can I get the shuffle playlist for a playlist or album?
***********************************************************************
Use `get_watch_playlist_shuffle <Reference.html#ytmusicapi.YTMusic.get_watch_playlist_shuffle>`__
with the ``playlistId`` or ``audioPlaylistId`` (albums).

How can I get all my public playlists in a single request?
***********************************************************************
Call `get_user_playlists <Reference.html#ytmusicapi.YTMusic.get_user_playlists>`__
with your own ``channelId``.

Can I download songs?
***********************************************************************
You can use `youtube-dl <https://github.com/ytdl-org/youtube-dl/>`_ for this purpose.


YouTube Music API Internals
------------------------------

Is there a difference between songs and videos?
***********************************************************************
Yes. Videos are regular videos from YouTube, which can be uploaded by any user. Songs are actual songs uploaded by artists.

You can also add songs to your library, while you can't add videos.

Is there a rate limit?
***********************************************************************
There most certainly is, although you shouldn't run into it during normal usage.
See related issues:

- `Creating playlists <https://github.com/sigma67/ytmusicapi/issues/19>`_
- `Uploads <https://github.com/sigma67/ytmusicapi/issues/6>`_


What is a browseId?
***********************************************************************
A ``browseId`` is an internal, globally unique identifier used by YouTube Music for browsable content.


Why is ytmusicapi returning more results than requested with the limit parameter?
***********************************************************************
YouTube Music always returns increments of a specific pagination value, usually between 20 and 100 items at a time.
This is the case if a ytmusicapi method supports the ``limit`` parameter. The default value of the ``limit`` parameter
indicates the server-side pagination increment. ytmusicapi will keep fetching continuations from the server until it has
reached at least the ``limit`` parameter, and return all of these results.

