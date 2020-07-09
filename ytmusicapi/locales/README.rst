Translations
============================================
Translations use the Linux command line utility xgettext, which you can install for example using your package manager.

Add new translatable texts from code
----------------------------------------

xgettext -d base -o locales/base.pot ytmusicapi/*.py
sed --in-place locales/base.pot --expression=s/CHARSET/UTF-8/

Create new translation
----------------------
mkdir -p locales/{en,es}/LC_MESSAGES
cp locales/base.pot locales/LANG/LC_MESSAGES/base.po

Update translation
----------------

msgmerge --update locales/de/LC_MESSAGES/base.po locales/base.pot

Edit translation
----------------
You can use POEdit

Finalize translation
---------------------
To generate mo files, run

msgfmt -o locales/de/LC_MESSAGES/base.mo locales/de/LC_MESSAGES/base