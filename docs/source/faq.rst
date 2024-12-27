FAQ
=====

Frequently asked questions for ``ytmusicapi``. Contributions are welcome, please
`submit a PR <https://github.com/sigma67/ytmusicapi/pulls>`_.

Setup
------------

My library results are empty even though I set up my cookie correctly.
***********************************************************************
Please make sure that you don't have multiple Google accounts. ``ytmusicapi`` might be returning
results from a different account which is currently empty. You can set your account using ``X-Goog-AuthUser``
in your headers file (numeric index) or by providing the id of a brand account with ``ytmusic = YTMusic(headers, "1234..")``.
For more details see the :doc:`reference/index`.

Usage
-----------------------

How do I add content to my library?
***********************************************************************
- **songs**: `edit_song_library_status <reference.html#ytmusicapi.YTMusic.edit_song_library_status>`__ .
  Liking a song using `rate_song <reference.html#ytmusicapi.YTMusic.rate_song>`__
  does *not* add it to your library, only to your liked songs playlist.
- **albums, playlists**: `rate_playlist <reference.html#ytmusicapi.YTMusic.rate_playlist>`__
- **artists**: `subscribe_artists <reference.html#ytmusicapi.YTMusic.subscribe_artists>`__ .
  This will add the artist to your Subscriptions tab. The Artists tab is determined by the songs/albums you have
  added to your library.
- **podcasts**: `rate_playlist <reference.html#ytmusicapi.YTMusic.rate_playlist>`__
- **episodes**: `add_playlist_items("SE", episode_id) <reference.html#ytmusicapi.YTMusic.add_playlist_items>`__



How can I get the radio playlist for a song, video, playlist or album?
***********************************************************************
- **songs, videos**: ``RDAMVM`` + ``videoId``
- **playlists, albums**: ``RDAMPL`` + ``playlistId``

See also `What is a browseId <faq.html#what-is-a-browseid>`__ below.


How can I get the shuffle playlist for a playlist or album?
***********************************************************************
Use `get_watch_playlist_shuffle <reference.html#ytmusicapi.YTMusic.get_watch_playlist_shuffle>`__
with the ``playlistId`` or ``audioPlaylistId`` (albums).

How can I get all my public playlists in a single request?
***********************************************************************
Call `get_user_playlists <reference.html#ytmusicapi.YTMusic.get_user_playlists>`__
with your own ``channelId``.

Can I download songs?
***********************************************************************
You can use `youtube-dl <https://github.com/ytdl-org/youtube-dl/>`_ for this purpose.

How do I package ytmusicapi with ``pyinstaller``?
*************************************************

To package ytmusicapi correctly, you need to add the locales files to your executable.

You can use ``--add-data path-to-ytmusicapi/locales`` or ``--collect-all ytmusicapi`` to accomplish this.


YouTube Music API Internals
------------------------------

Is there a difference between songs and videos?
***********************************************************************
Yes. Videos are regular videos from YouTube, which can be uploaded by any user. Songs are actual songs uploaded by artists.

You can also add songs to your library, while you can't add videos.

Is there a rate limit?
***********************************************************************
There most certainly is, although you shouldn't run into it during normal usage.
See related issues:

- `Creating playlists <https://github.com/sigma67/ytmusicapi/issues/19>`_
- `Uploads <https://github.com/sigma67/ytmusicapi/issues/6>`_


What is a browseId?
***********************************************************************
A ``browseId`` is an internal, globally unique identifier used by YouTube Music for browsable content.

In most cases you can compose it yourself:

+--------+------------+----------------------+
| Prefix | Main       | Content              |
+========+============+======================+
| VM     | playlistId | Playlist             |
+--------+------------+----------------------+
| RDAMVM | playlistId | Video-based Radio    |
+--------+------------+----------------------+
| RDAMPL | videoId    | Playlist-based Radio |
+--------+------------+----------------------+
| MPLA   | channelId  | Artist               |
+--------+------------+----------------------+
| MPRE   | custom     | Album                |
+--------+------------+----------------------+
| MPSP   | playlistId | Podcast              |
+--------+------------+----------------------+
| MPED   | videoId    | Episode              |
+--------+------------+----------------------+


Which videoTypes exist and what do they mean?
***********************************************************************

``videoType`` is prefixed with ``MUSIC_VIDEO_TYPE_``, i.e. ``MUSIC_VIDEO_TYPE_OMV``.
Currently the following variants of ``videoType`` are known:

- ``OMV``: Original Music Video - uploaded by original artist with actual video content
- ``UGC``: User Generated Content - uploaded by regular YouTube user
- ``ATV``: High quality song uploaded by original artist with cover image
- ``OFFICIAL_SOURCE_MUSIC``: Official video content, but not for a single track


Why is ytmusicapi returning more results than requested with the limit parameter?
*********************************************************************************
YouTube Music always returns increments of a specific pagination value, usually between 20 and 100 items at a time.
This is the case if a ytmusicapi method supports the ``limit`` parameter. The default value of the ``limit`` parameter
indicates the server-side pagination increment. ytmusicapi will keep fetching continuations from the server until it has
reached at least the ``limit`` parameter, and return all of these results.


Which values can I use for languages?
*************************************

The ``language`` parameter determines the language of the returned results.
``ytmusicapi`` only supports a subset of the languages supported by YouTube Music, as translations need to be done manually.
Contributions are welcome, see `here for instructions <https://github.com/sigma67/ytmusicapi/tree/master/ytmusicapi/locales>`__.

For the list of values you can use for the ``language`` parameter, see below:

.. raw:: html

   <details>
   <br>
   <summary><a>Supported locations</a></summary>

.. container::

    .. list-table::

        * - **Language**
          - **Value**
        * - Arabic
          - ar
        * - German
          - de
        * - English (default)
          - en
        * - Spanish
          - es
        * - French
          - fr
        * - Hindi
          - hi
        * - Italian
          - it
        * - Japanese
          - ja
        * - Korean
          - ko
        * - Dutch
          - nl
        * - Portuguese
          - pt
        * - Russian
          - ru
        * - Turkish
          - tr
        * - Urdu
          - ur
        * - Chinese (Mainland)
          - zh_CN
        * - Chinese (Taiwan)
          - zh_TW


.. raw:: html

   </details>
   </br>



Which values can I use for locations?
*************************************

Pick a value from the list below for your desired location and pass it using the ``location`` parameter.

.. raw:: html

   <details>
   <br>
   <summary><a>Supported locations</a></summary>

.. container::

    .. list-table::

        * - **Location**
          - **Value**
        * - Algeria
          - DZ
        * - Argentina
          - AR
        * - Australia
          - AU
        * - Austria
          - AT
        * - Azerbaijan
          - AZ
        * - Bahrain
          - BH
        * - Bangladesh
          - BD
        * - Belarus
          - BY
        * - Belgium
          - BE
        * - Bolivia
          - BO
        * - Bosnia and Herzegovina
          - BA
        * - Brazil
          - BR
        * - Bulgaria
          - BG
        * - Cambodia
          - KH
        * - Canada
          - CA
        * - Chile
          - CL
        * - Colombia
          - CO
        * - Costa Rica
          - CR
        * - Croatia
          - HR
        * - Cyprus
          - CY
        * - Czechia
          - CZ
        * - Denmark
          - DK
        * - Dominican Republic
          - DO
        * - Ecuador
          - EC
        * - Egypt
          - EG
        * - El Salvador
          - SV
        * - Estonia
          - EE
        * - Finland
          - FI
        * - France
          - FR
        * - Georgia
          - GE
        * - Germany
          - DE
        * - Ghana
          - GH
        * - Greece
          - GR
        * - Guatemala
          - GT
        * - Honduras
          - HN
        * - Hong Kong
          - HK
        * - Hungary
          - HU
        * - Iceland
          - IS
        * - India
          - IN
        * - Indonesia
          - ID
        * - Iraq
          - IQ
        * - Ireland
          - IE
        * - Israel
          - IL
        * - Italy
          - IT
        * - Jamaica
          - JM
        * - Japan
          - JP
        * - Jordan
          - JO
        * - Kazakhstan
          - KZ
        * - Kenya
          - KE
        * - Kuwait
          - KW
        * - Laos
          - LA
        * - Latvia
          - LV
        * - Lebanon
          - LB
        * - Libya
          - LY
        * - Liechtenstein
          - LI
        * - Lithuania
          - LT
        * - Luxembourg
          - LU
        * - Malaysia
          - MY
        * - Malta
          - MT
        * - Mexico
          - MX
        * - Montenegro
          - ME
        * - Morocco
          - MA
        * - Nepal
          - NP
        * - Netherlands
          - NL
        * - New Zealand
          - NZ
        * - Nicaragua
          - NI
        * - Nigeria
          - NG
        * - North Macedonia
          - MK
        * - Norway
          - NO
        * - Oman
          - OM
        * - Pakistan
          - PK
        * - Panama
          - PA
        * - Papua New Guinea
          - PG
        * - Paraguay
          - PY
        * - Peru
          - PE
        * - Philippines
          - PH
        * - Poland
          - PL
        * - Portugal
          - PT
        * - Puerto Rico
          - PR
        * - Qatar
          - QA
        * - Romania
          - RO
        * - Russia
          - RU
        * - Saudi Arabia
          - SA
        * - Senegal
          - SN
        * - Serbia
          - RS
        * - Singapore
          - SG
        * - Slovakia
          - SK
        * - Slovenia
          - SI
        * - South Africa
          - ZA
        * - South Korea
          - KR
        * - Spain
          - ES
        * - Sri Lanka
          - LK
        * - Sweden
          - SE
        * - Switzerland
          - CH
        * - Taiwan
          - TW
        * - Tanzania
          - TZ
        * - Thailand
          - TH
        * - Tunisia
          - TN
        * - Turkey
          - TR
        * - Uganda
          - UG
        * - Ukraine
          - UA
        * - United Arab Emirates
          - AE
        * - United Kingdom
          - GB
        * - United States
          - US
        * - Uruguay
          - UY
        * - Venezuela
          - VE
        * - Vietnam
          - VN
        * - Yemen
          - YE
        * - Zimbabwe
          - ZW

.. raw:: html

   </details>
   </br>
