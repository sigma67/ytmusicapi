Package tests
============================================
Tests use the `unittest` framework. Each function has a corresponding unittest.
Sometimes there is a single unittest for multiple functions to ensure there are no permanent changes in the user's YouTube account (i.e. subscribe and unsubscribe).

Note that there must be a `headers_auth.json` in the project root to run authenticated tests.
For testing the song upload, there also needs to be a file with the name specified in the code in the project root.
For `test_get_owned_playlist` you need to modify the test to

Coverage badge
--------------
Install `coverage` and `coverage-badge` with pip. Run

`coverage run --source=ytmusicapi -m unittest discover tests`

to generate a coverage report in the project root. With

`coverage-badge -o coverage.svg`

you generate the badge. Move both files to the `tests` directory.