OAuth authentication
====================

.. attention::

   As of November 2024, YouTube Music requires a Client Id and Secret for the YouTube Data API to connect to the API.

   Go to the `YouTube Data API docs <https://developers.google.com/youtube/registering_an_application>`_ to
   obtain the credentials. This requires a Google Cloud Console account and project.

   For your new credentials, select ``OAuth client ID`` and pick ``TVs and Limited Input devices``.

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
