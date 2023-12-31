Contributing to ytmusicapi
##########################

Issues
-------
Please make sure to include sufficient details for reproducing your issue.
This includes the version of the library used as well as detailed instructions for reproduction.
If needed, please include the YouTube Music API response as well by debugging the API (responses
may differ based on the user account, so this helps with reproducing new issues).


Pull requests
--------------
Please open an issue before submitting, unless it's just a typo or some other small error.

Before making changes to the code, install the development requirements using

.. code-block::

    pip install pipx
    pipx install pdm pre-commit
    pdm install

Before committing, stage your files and run style and linter checks:

.. code-block::

    git add .
    pre-commit run

pre-commit will unstage any files that do not pass. Fix the issues until all checks pass and commit.

Code structure
---------------
The folder ``ytmusicapi`` contains the main library which is distributed to the users.
Each main library function in ``ytmusic.py`` is covered by a test in the ``tests`` folder.
If you want to contribute a new function, please create a corresponding unittest.