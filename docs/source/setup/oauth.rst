OAuth authentication
====================

After you have installed ``ytmusicapi``, simply run

.. code-block:: bash

    ytmusicapi oauth

and follow the instructions. This will create a file ``oauth.json`` in the current directory.

You can pass this file to :py:class:`YTMusic` as explained in :doc:`../usage`.

This OAuth flow uses the
`Google API flow for TV devices <https://developers.google.com/youtube/v3/guides/auth/devices>`_.