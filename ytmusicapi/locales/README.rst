Translations
============================================
Translations are required for ytmusicapi since it relies on parsing user interface text.
In some places, for example the search() or get_artist() features, there is no other way to tell which content type is
offered other than parsing display text, which depends on the user's language. Changing the API language is desirable,
since artist and song titles are also language dependent.

This package uses the Linux command line utility xgettext, which you can install for example using your package manager.

Add new translatable texts from code
----------------------------------------

``xgettext -d base -o locales/base.pot ytmusicapi/*.py``

``sed --in-place locales/base.pot --expression=s/CHARSET/UTF-8/``

Create new translation
----------------------
Create the directories (in this case for English, Spanish):

``mkdir -p locales/{en,es}/LC_MESSAGES``

Copy the base template:

``cp locales/base.pot locales/LANG/LC_MESSAGES/base.po``

Update translation
------------------

``msgmerge --update locales/de/LC_MESSAGES/base.po locales/base.pot``

Edit translation
----------------
You can use POEdit or edit the .po file manually

Finalize translation
---------------------
To generate mo files, run

``msgfmt -o locales/de/LC_MESSAGES/base.mo locales/de/LC_MESSAGES/base``