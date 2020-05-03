Package tests
============================================
Tests use the `unittest` framework. Each function has a corresponding unittest.
Sometimes there is a single unittest for multiple functions to ensure there are no permanent changes in the user's YouTube account (i.e. subscribe and unsubscribe).

Note that there must be a `headers_auth.json` in the project root to run authenticated tests.
For testing the song upload, there also needs to be a file with the name specified in the code in the project root.

Copy `tests/test.cfg.example` to `test.cfg` in the project root to run tests with coverage.
Adjust the file to contain appropriate information for your YouTube account and local setup.

Coverage badge
--------------
Install `coverage` and `coverage-badge` with pip. Run

`coverage run --source=ytmusicapi -m unittest discover tests`

to generate a coverage report in the project root. With

`coverage-badge -o tests/coverage.svg -f`

you generate the badge.