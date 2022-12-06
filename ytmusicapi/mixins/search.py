from typing import List, Dict
from ytmusicapi.navigation import *
from ytmusicapi.continuations import get_continuations
from ytmusicapi.parsers.search_params import *
from raise_utils import filter_exception, scope_exception, set_exception


class SearchMixin:
    def search(self,
               query: str,
               filter: str = None,
               scope: str = None,
               limit: int = 20,
               ignore_spelling: bool = False) -> List[Dict]:
        """
        Search YouTube music
        Returns results within the provided category.

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :param filter: Filter for item types. Allowed values: ``songs``, ``videos``, ``albums``, ``artists``, ``playlists``, ``community_playlists``, ``featured_playlists``, ``uploads``.
          Default: Default search, including all types of items.
        :param scope: Search scope. Allowed values: ``library``, ``uploads``.
            For uploads, no filter can be set! An exception will be thrown if you attempt to do so.
            Default: Search the public YouTube Music catalogue.
        :param limit: Number of search results to return
          Default: 20
        :param ignore_spelling: Whether to ignore YTM spelling suggestions.
          If True, the exact search term will be searched for, and will not be corrected.
          This does not have any effect when the filter is set to ``uploads``.
          Default: False, will use YTM's default behavior of autocorrecting the search.
        :return: List of results depending on filter.
          resultType specifies the type of item (important for default search).
          albums, artists and playlists additionally contain a browseId, corresponding to
          albumId, channelId and playlistId (browseId=``VL``+playlistId)

          Example list for default search with one result per resultType for brevity. Normally
          there are 3 results per resultType and an additional ``thumbnails`` key::

            [
              {
                "category": "Top result",
                "resultType": "video",
                "videoId": "vU05Eksc_iM",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "views": "1.4M",
                "videoType": "MUSIC_VIDEO_TYPE_OMV",
                "duration": "4:38",
                "duration_seconds": 278
              },
              {
                "category": "Songs",
                "resultType": "song",
                "videoId": "ZrOKjDZOtkA",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "album": {
                  "name": "(What's The Story) Morning Glory? (Remastered)",
                  "id": "MPREb_9nqEki4ZDpp"
                },
                "duration": "4:19",
                "duration_seconds": 259
                "isExplicit": false,
                "feedbackTokens": {
                  "add": null,
                  "remove": null
                }
              },
              {
                "category": "Albums",
                "resultType": "album",
                "browseId": "MPREb_9nqEki4ZDpp",
                "title": "(What's The Story) Morning Glory? (Remastered)",
                "type": "Album",
                "artist": "Oasis",
                "year": "1995",
                "isExplicit": false
              },
              {
                "category": "Community playlists",
                "resultType": "playlist",
                "browseId": "VLPLK1PkWQlWtnNfovRdGWpKffO1Wdi2kvDx",
                "title": "Wonderwall - Oasis",
                "author": "Tate Henderson",
                "itemCount": "174"
              },
              {
                "category": "Videos",
                "resultType": "video",
                "videoId": "bx1Bh8ZvH84",
                "title": "Wonderwall",
                "artists": [
                  {
                    "name": "Oasis",
                    "id": "UCmMUZbaYdNH0bEd1PAlAqsA"
                  }
                ],
                "views": "386M",
                "duration": "4:38",
                "duration_seconds": 278
              },
              {
                "category": "Artists",
                "resultType": "artist",
                "browseId": "UCmMUZbaYdNH0bEd1PAlAqsA",
                "artist": "Oasis",
                "shuffleId": "RDAOkjHYJjL1a3xspEyVkhHAsg",
                "radioId": "RDEMkjHYJjL1a3xspEyVkhHAsg"
              }
            ]


        """
        body = {'query': query}
        endpoint = 'search'
        search_results = []
        filter_exception(filter)
        scope_exception(scope)
        set_exception(scope, filter)

        params = get_search_params(filter, scope, ignore_spelling)
        if params:
            body['params'] = params

        response = self._send_request(endpoint, body)

        # no results
        if 'contents' not in response:
            return search_results

        if 'tabbedSearchResultsRenderer' in response['contents']:
            tab_index = 0 if not scope or filter else scopes.index(scope) + 1
            results = response['contents']['tabbedSearchResultsRenderer']['tabs'][tab_index][
                'tabRenderer']['content']
        else:
            results = response['contents']

        results = nav(results, SECTION_LIST)

        # no results
        if len(results) == 1 and 'itemSectionRenderer' in results:
            return search_results

        # set filter for parser
        if filter and 'playlists' in filter:
            filter = 'playlists'
        elif scope == scopes[1]:
            filter = scopes[1]

        for res in results:
            if 'musicShelfRenderer' in res:
                results = res['musicShelfRenderer']['contents']
                original_filter = filter
                category = nav(res, MUSIC_SHELF + TITLE_TEXT, True)
                if not filter and scope == scopes[0]:
                    filter = category

                type = filter[:-1].lower() if filter else None
                search_results.extend(self.parser.parse_search_results(results, type, category))
                filter = original_filter

                if 'continuations' in res['musicShelfRenderer']:
                    request_func = lambda additionalParams: self._send_request(
                        endpoint, body, additionalParams)

                    parse_func = lambda contents: self.parser.parse_search_results(
                        contents, type, category)

                    search_results.extend(
                        get_continuations(res['musicShelfRenderer'], 'musicShelfContinuation',
                                          limit - len(search_results), request_func, parse_func))

        return search_results
