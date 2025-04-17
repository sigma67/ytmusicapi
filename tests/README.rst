Package tests
============================================
Tests use the ``unittest`` framework. Each function has a corresponding unittest.
Sometimes there is a single unittest for multiple functions to ensure there are no permanent changes in the user's
YouTube account (i.e. subscribe and unsubscribe).

Note that there must be a ``browser.json`` and ``oauth.json`` in the ``tests`` folder to run all authenticated tests.
These two files can be easily obtained as the default outputs of running the following commands respectively:

.. code-block:: bash

    ytmusicapi browser
    ytmusicapi oauth



First, run

.. code-block:: bash

    cp tests/test.example.cfg tests/test.cfg

The entry descriptions should be self-explanatory.
For the headers_raw, you need to indent the overflowing lines with a tab character. For the upload test you need a suitable music file in the test directory.
Adjust the file to contain appropriate information for your YouTube account and local setup.

``account_name`` and ``channel_handle`` for test.cfg can be obtained by visiting either YouTube or YouTube Music and
clicking your profile picture icon in the top right while signed in with your test account.

Brand accounts can be created by first signing into the google account you wish to have as the parent/controlling
account then navigating `here. <https://www.youtube.com/create_channel?action_create_new_channel_redirect=true>`_

Once the brand account/channel has been created, you can obtain the account ID needed for your test.cfg by
navigating to your `google account page <https://myaccount.google.com>`_ and selecting the brand account via the
profile drop down in the top right, the brand ID should then be present in the URL.

You can populate the brand account with content using the script provided in ``tests/setup/setup_account.py``.

Coverage badge
--------------
Make sure you installed the dev requirements as explained in `CONTRIBUTING.rst <https://github.com/sigma67/ytmusicapi/blob/master/CONTRIBUTING.rst>`_. Run

.. code-block:: bash

    pdm run pytest


to generate a coverage report.
