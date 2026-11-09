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

Adding a response model
-----------------------

Response-model contributions target the ``ytmusicapi-2`` branch. Keep a contribution
scoped to its tracking issue: model definitions, parser construction, mixin return
annotations and docstrings, and offline tests for that response.

Find the shape and reuse existing models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start with the endpoint's return-value documentation in ``ytmusicapi/mixins/``.
Read the parser that builds that result and its tests, rather than modelling the
raw YouTube Music response directly. Models describe the public, parsed response.
``tests/parsers/data.py`` contains reusable response fixtures, and ``tests/data/``
contains recorded responses and expected outputs. Existing offline tests also
build small response dictionaries for individual parser paths.

The model package currently contains:

* ``ytmusicapi/models/base.py``: ``YTMusicModel``, the common Pydantic base.
* ``ytmusicapi/models/uploads.py``: ``UploadSong`` and ``UploadAlbum``, plus their
  thumbnail, artist, and album reference models.
* ``ytmusicapi/models/content/``: content enums and text-run types. Some existing
  types, including lyrics and text runs, are still awaiting model migration.
* ``ytmusicapi/models/__init__.py``: public exports. Export new public response
  models here, following the existing imports and ``__all__``.

Put endpoint-specific models in the corresponding module under ``models/``.
Reuse an existing model when it describes the same shape; an uploaded song, for
example, is not interchangeable with a regular song simply because both have a
title. The shared leaf-model work in issue #981 moves reusable references into
``models/content/`` and exports them from ``models``. Until that lands, the upload
reference types live in ``models/uploads.py``. Check the target branch for the
current imports before adding another definition. Likewise, reuse the core song,
album, artist, and playlist models from issues #983–#985 as they become available.

Declare fields and defaults
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Derive response models from ``YTMusicModel``, which provides attribute access as
well as dictionary-style access. For example, this is the existing thumbnail
shape from ``models/uploads.py``:

.. code-block:: python

    from ytmusicapi.models import YTMusicModel

    class Thumbnail(YTMusicModel):
        url: str
        width: int | None = None
        height: int | None = None

In Pydantic v2, nullability and whether a field can be omitted are separate:

* ``url: str`` requires a string value; omission and ``None`` are invalid.
* ``name: str | None`` requires the field, but accepts either a string or ``None``.
* ``width: int | None = None`` accepts omission and supplies ``None`` by default.

Choose required fields based on what the parser always supplies. Use a nullable
field with a ``None`` default when data can be absent; making every field optional
would hide unexpected changes in responses.

Every declared field of a constructed model is a key, even when its value defaults
to ``None``:

.. code-block:: python

    thumbnail = Thumbnail(url="https://example.com/image.jpg")
    assert "width" in thumbnail
    assert thumbnail.width is None
    assert thumbnail["width"] is None
    assert thumbnail.get("width") is None

Test ``thumbnail.width is None`` to detect missing data. Testing key membership
cannot distinguish missing API data from a supplied value. This differs from old
dictionary responses that omitted some keys. Required fields do not silently
become ``None``: constructing a model without them raises a validation error.

The base uses ``extra="allow"`` so undeclared parser output is preserved. Declare
the known fields for useful type hints; do not disable extra fields to detect
response drift. ``dict(model)`` retains nested model instances, while
``model.model_dump()`` recursively converts nested models to dictionaries.

Construct models in the parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ytmusicapi/parsers/uploads.py::parse_upload_album`` is a concrete example of
converting an assembled dictionary at the parser boundary. A dictionary-returning
version of the same parsing steps would look like this (``response`` is the raw
API response):

.. code-block:: python

    def parse_upload_album(response: JsonDict) -> JsonDict:
        album = parse_album_header(response)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        album["tracks"] = parse_uploaded_items(results["contents"])
        album["duration_seconds"] = sum_total_duration(album)
        return album

The current implementation keeps that parsing and constructs ``UploadAlbum``:

.. code-block:: python

    from ytmusicapi.models.uploads import UploadAlbum

    def parse_upload_album(response: JsonDict) -> UploadAlbum:
        album = parse_album_header(response)
        results = nav(response, SINGLE_COLUMN_TAB + SECTION_LIST_ITEM + MUSIC_SHELF)
        album["tracks"] = parse_uploaded_items(results["contents"])
        album["duration_seconds"] = sum_total_duration(album)
        return UploadAlbum(**album)

These excerpts use the existing imports from ``parsers/uploads.py`` for parsing
and navigation. ``UploadAlbum.tracks`` is ``list[UploadSong]``; the item parser
already returns ``UploadSong`` instances. That parser also demonstrates direct
keyword construction and building nested ``ArtistRef`` and ``AlbumRef`` models.
Pydantic can validate nested dictionaries against annotated model fields as well.

Keep parsing and fallback behavior unchanged, including empty lists and ``None``
results. Update the calling mixin's return annotation and return-value documentation
to describe the model, preserving any overloads and literal discriminators. Check
other parser callers for assumptions about dictionaries or mutable results.

Test the response
~~~~~~~~~~~~~~~~~

Use offline fixtures so model validation does not require a YouTube account or
network access. ``tests/parsers/test_uploads.py`` demonstrates raw response builders
and checks both parsed models and missing-field behavior. Keep expectations
independent of the result: do not generate expected values with ``model_dump()``
on the response being tested.

Import ``assert_response_model`` from ``tests.model_helpers``. It checks the model
type, the complete ``model_dump()`` output, and JSON round-tripping. Include all
fields in the expected dictionary, including defaulted ``None`` values and any
extra fields. For example, this can run alongside the existing upload tests using
their ``_upload_song_item`` response builder:

.. code-block:: python

    from tests.model_helpers import assert_response_model
    from ytmusicapi.models.uploads import UploadSong
    from ytmusicapi.parsers.uploads import parse_uploaded_items

    def test_uploaded_song_without_optional_metadata():
        item = _upload_song_item()
        del item["musicResponsiveListItemRenderer"]["fixedColumns"]
        del item["musicResponsiveListItemRenderer"]["flexColumns"][2]
        del item["musicResponsiveListItemRenderer"]["thumbnail"]

        song = parse_uploaded_items([item])[0]
        assert_response_model(song, UploadSong, {
            "entityId": "t_po_CICr2crg7OWpchDpjPjrBA",
            "videoId": "Uise6RPKoek",
            "title": "A Sky Full Of Stars",
            "duration": None,
            "duration_seconds": None,
            "artists": [{"name": "Coldplay", "id": ARTIST_ID}],
            "album": None,
            "likeStatus": "LIKE",
            "thumbnails": None,
        })

Here ``ARTIST_ID`` is also defined in ``tests/parsers/test_uploads.py``. Add explicit
assertions for nested model types and endpoint-specific behavior, since serialized
dictionary equality alone cannot prove that nested values are models. Cover
representative responses, absent optional data, and relevant fallback paths. For
required fields and invalid values, use ``pytest.raises(pydantic.ValidationError)``.
The mapping protocol itself is already covered by ``tests/models/test_base.py``;
new endpoint tests need not repeat that entire suite.

Validate the contribution
~~~~~~~~~~~~~~~~~~~~~~~~~

After installing the development dependencies as described above, run the focused
offline tests and repository checks from the project root:

.. code-block:: bash

    pdm run pytest tests/models tests/parsers/test_uploads.py
    pdm run mypy --strict
    pdm run mypy --strict tests/model_helpers.py
    pdm run ruff check .
    pdm run ruff format --check .

Replace or extend the upload test path with the parser tests affected by your
model. The default mypy configuration checks ``ytmusicapi/``; check new typed test
helpers explicitly too. These focused tests need no credentials. The full suite
also contains live and account-mutating tests: see ``tests/README.rst`` before
running it. Run the pre-commit checks described above before committing.

Youtube Music FE request body compression
-----------------------------------------
Youtube music FE has recently started to compress their POST request body with GZIP, which might make it harder for contributor to find out what needs to be passed into the request body.
In order to decrypt the request, the following will need to be done

1. Make the corresponding request in the youtube music FE.
2. Download the specific request into a HAR file using your browser.
3. Run the following python script with the name of the HAR file being the first command line argument and the name of output file being the second command line argument.

.. code-block::

    import gzip
    import json
    import sys

    fname = sys.argv[1]
    to_save = sys.argv[2]

    with open(fname, encoding='utf8') as f:
    request: dict = json.load(f)


    request_body = request["log"]["entries"][0]["request"]["postData"]["text"]


    raw = request_body.encode("latin1")


    decompressed = gzip.decompress(raw)
    with open(to_save, "w") as f:
    json.dump(json.loads(decompressed.decode("utf-8")), f, indent=2, ensure_ascii=False)
