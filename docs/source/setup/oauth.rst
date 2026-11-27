OAuth authentication
====================

.. attention::

   As of November 2024, YouTube Music requires a Client Id and Secret for the YouTube Data API to connect to the API.

   Go to the `YouTube Data API docs <https://developers.google.com/youtube/registering_an_application>`_ to
   obtain the credentials. This requires a Google Cloud Console account and project.

   For your new credentials, select ``OAuth client ID`` and pick ``TVs and Limited Input devices``.

.. warning::

   Since August 2025, YouTube Music only accepts OAuth tokens from YouTube's TV client.
   With OAuth authentication, ``ytmusicapi`` therefore sends its requests as that client, which only
   supports a subset of the API and returns less detailed results (for example no album or like status
   for playlist items). Currently supported with OAuth:

   - :py:func:`get_library_playlists`, :py:func:`get_playlist`, :py:func:`get_liked_songs`
   - :py:func:`get_library_songs`, :py:func:`get_library_albums`, :py:func:`get_library_subscriptions`
     (subscriptions only contain the artist name and ``radioId``)
   - :py:func:`get_artist`, which returns the artist's shelves as a list of ``sections`` instead of the
     usual keys. Albums are returned as playlists: pass their ``playlistId`` to :py:func:`get_playlist`
   - :py:func:`get_watch_playlist` (without ``lyrics`` and ``related``)
   - :py:func:`search` (searches all of YouTube; only the ``songs``, ``videos``, ``albums``, ``artists``
     and ``playlists`` filters, no scopes)
   - :py:func:`edit_playlist`, :py:func:`add_playlist_items`, :py:func:`remove_playlist_items`
   - :py:func:`create_playlist` and :py:func:`delete_playlist`, which use the YouTube Data API
     and consume quota of your OAuth client
   - :py:func:`rate_song`, :py:func:`rate_playlist`, :py:func:`subscribe_artist` and
     :py:func:`unsubscribe_artists`

   Known differences of the supported functions:

   - :py:func:`add_playlist_items` does not return the ``setVideoId`` of the added items.
     Use :py:func:`get_playlist` to retrieve them.
   - :py:func:`get_liked_songs` may return fewer items than the playlist's ``trackCount``.
   - Changes can take a few seconds until they are returned by other functions. For example,
     :py:func:`get_playlist` may raise a :py:class:`YTMusicServerError` right after :py:func:`create_playlist`.

   Functions without an equivalent on the TV client, such as :py:func:`get_home`, :py:func:`get_album`,
   :py:func:`get_history` or uploads, raise a :py:class:`YTMusicUserError`.
   Use :doc:`browser` authentication if you need the full API.

After you have installed ``ytmusicapi``, run

.. code-block:: bash

    ytmusicapi oauth

and follow the instructions. This will create a file ``oauth.json`` in the current directory.

You can pass this file to :py:class:`YTMusic` as explained in :doc:`../usage`.

You will also need to pass ``client_id`` and ``client_secret`` to :py:class:`YTMusic`:

.. code-block::

    from ytmusicapi import YTMusic, OAuthCredentials

    ytmusic = YTMusic('oauth.json', oauth_credentials=OAuthCredentials(client_id=client_id, client_secret=client_secret))

This OAuth flow uses the
`Google API flow for TV devices <https://developers.google.com/youtube/v3/guides/auth/devices>`_.
