Usage
=======

**Unauthenticated** requests for retrieving playlist content or searching:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic()


If an endpoint requires authentication you will receive an error:
``Please provide authentication before using this function``

For authenticated requests you need to set up your credentials first: `Setup <setup>`_

**Authenticated** request to interact with your playlist:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')


Detailed example with authenticated requests:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic('headers_auth.json')
    playlistId = ytmusic.create_playlist("test", "test description")
    search_results = ytmusic.search("Oasis Wonderwall")
    ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId'])