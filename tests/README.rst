Package tests
============================================
Tests use the ``unittest`` framework. Each function has a corresponding unittest.
Sometimes there is a single unittest for multiple functions to ensure there are no permanent changes in the user's YouTube account (i.e. subscribe and unsubscribe).

Note that there must be a ``headers_auth.json`` in the `tests` folder to run authenticated tests.
For testing the song upload, there also needs to be a file with the name specified in the code in the project root.

Copy ``tests/test.cfg.example`` to ``tests/test.cfg`` to run the tests. The entry descriptions should be self-explanatory.
For the headers_raw, you need to indent the overflowing lines with a tab character. For the upload test you need a suitable music file in the test directory.
Adjust the file to contain appropriate information for your YouTube account and local setup.

Coverage badge
--------------
Make sure you installed the dev requirements as explained in `CONTRIBUTING.rst <https://github.com/sigma67/ytmusicapi/blob/master/CONTRIBUTING.rst>`_. Run

.. code-block:: bash

    cd tests
    coverage run -m unittest test.py


to generate a coverage report.