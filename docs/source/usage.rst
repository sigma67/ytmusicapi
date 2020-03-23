Usage
=======

Unauthenticated
---------------
Unauthenticated requests for retrieving playlist content or searching:

.. code-block:: python

    from ytmusicapi import YTMusic

    ytmusic = YTMusic()


If an endpoint requires authentication you will receive an error:
``Please provide authentication before using this function``

Authenticated
-------------
For authenticated requests you need to set up your credentials first: :doc:`Setup <setup>`

After you have created the authentication JSON, you can instantiate the class:

.. code-block:: python

    from ytmusicapi import YTMusic
    ytmusic = YTMusic('headers_auth.json')


With the :code:`ytmusic` instance you can now perform authenticated requests:

.. code-block:: python

    playlistId = ytmusic.create_playlist("test", "test description")
    search_results = ytmusic.search("Oasis Wonderwall")
    ytmusic.add_playlist_items(playlistId, [search_results[0]['videoId'])