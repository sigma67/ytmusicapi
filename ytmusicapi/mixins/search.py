from typing import Any, Dict, List, Optional, Union

from ytmusicapi.continuations import get_continuations
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.search import *


class SearchMixin(MixinProtocol):
    def search(
        self,
        query: str,
        filter: Optional[str] = None,
        scope: Optional[str] = None,
        limit: int = 20,
        ignore_spelling: bool = False,
    ) -> List[Dict]:
        """
        Search YouTube music
        Returns results within the provided category.

        :param query: Query string, i.e. 'Oasis Wonderwall'
        :param filter: Filter for item types. Allowed values: ``songs``, ``videos``, ``albums``, ``artists``, ``playlists``, ``community_playlists``, ``featured_playlists``, ``uploads``.
          Default: Default search, including all types of items.
        :param scope: Search scope. Allowed values: ``library``, ``uploads``.
            Default: Search the public YouTube Music catalogue.
            Changing scope from the default will reduce the number of settable filters. Setting a filter that is not permitted will throw an exception.
            For uploads, no filter can be set.
            For library, community_playlists and featured_playlists filter cannot be set.
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
              },
              {
                "category": "Profiles",
                "resultType": "profile",
                "title": "Taylor Swift Time",
                "name": "@TaylorSwiftTime",
                "browseId": "UCSCRK7XlVQ6fBdEl00kX6pQ",
                "thumbnails": ...
              }
            ]


        """
        body = {"query": query}
        endpoint = "search"
        search_results: List[Dict[str, Any]] = []
        filters = [
            "albums",
            "artists",
            "playlists",
            "community_playlists",
            "featured_playlists",
            "songs",
            "videos",
            "profiles",
            "podcasts",
            "episodes",
        ]
        if filter and filter not in filters:
            raise Exception(
                "Invalid filter provided. Please use one of the following filters or leave out the parameter: "
                + ", ".join(filters)
            )

        scopes = ["library", "uploads"]
        if scope and scope not in scopes:
            raise Exception(
                "Invalid scope provided. Please use one of the following scopes or leave out the parameter: "
                + ", ".join(scopes)
            )

        if scope == scopes[1] and filter:
            raise Exception(
                "No filter can be set when searching uploads. Please unset the filter parameter when scope is set to "
                "uploads. "
            )

        if scope == scopes[0] and filter in filters[3:5]:
            raise Exception(
                f"{filter} cannot be set when searching library. "
                f"Please use one of the following filters or leave out the parameter: "
                + ", ".join(filters[0:3] + filters[5:])
            )

        params = get_search_params(filter, scope, ignore_spelling)
        if params:
            body["params"] = params

        response = self._send_request(endpoint, body)

        # no results
        if "contents" not in response:
            return search_results

        if "tabbedSearchResultsRenderer" in response["contents"]:
            tab_index = 0 if not scope or filter else scopes.index(scope) + 1
            results = response["contents"]["tabbedSearchResultsRenderer"]["tabs"][tab_index]["tabRenderer"][
                "content"
            ]
        else:
            results = response["contents"]

        results = nav(results, SECTION_LIST)

        # no results
        if len(results) == 1 and "itemSectionRenderer" in results:
            return search_results

        # set filter for parser
        if filter and "playlists" in filter:
            filter = "playlists"
        elif scope == scopes[1]:
            filter = scopes[1]

        for res in results:
            if "musicCardShelfRenderer" in res:
                top_result = parse_top_result(
                    res["musicCardShelfRenderer"], self.parser.get_search_result_types()
                )
                search_results.append(top_result)
                if results := nav(res, ["musicCardShelfRenderer", "contents"], True):
                    category = None
                    # category "more from youtube" is missing sometimes
                    if "messageRenderer" in results[0]:
                        category = nav(results.pop(0), ["messageRenderer", *TEXT_RUN_TEXT])
                    type = None
                else:
                    continue

            elif "musicShelfRenderer" in res:
                results = res["musicShelfRenderer"]["contents"]
                type_filter = filter
                category = nav(res, MUSIC_SHELF + TITLE_TEXT, True)
                if not type_filter and scope == scopes[0]:
                    type_filter = category

                type = type_filter[:-1].lower() if type_filter else None

            else:
                continue

            search_result_types = self.parser.get_search_result_types()
            search_results.extend(parse_search_results(results, search_result_types, type, category))

            if filter:  # if filter is set, there are continuations

                def request_func(additionalParams):
                    return self._send_request(endpoint, body, additionalParams)

                def parse_func(contents):
                    return parse_search_results(contents, search_result_types, type, category)

                search_results.extend(
                    get_continuations(
                        res["musicShelfRenderer"],
                        "musicShelfContinuation",
                        limit - len(search_results),
                        request_func,
                        parse_func,
                    )
                )

        return search_results

    def get_search_suggestions(self, query: str, detailed_runs=False) -> Union[List[str], List[Dict]]:
        """
        Get Search Suggestions

        :param query: Query string, i.e. 'faded'
        :param detailed_runs: Whether to return detailed runs of each suggestion.
            If True, it returns the query that the user typed and the remaining
            suggestion along with the complete text (like many search services
            usually bold the text typed by the user).
            Default: False, returns the list of search suggestions in plain text.
        :return: List of search suggestion results depending on ``detailed_runs`` param.

          Example response when ``query`` is 'fade' and ``detailed_runs`` is set to ``False``::

              [
                "faded",
                "faded alan walker lyrics",
                "faded alan walker",
                "faded remix",
                "faded song",
                "faded lyrics",
                "faded instrumental"
              ]

          Example response when ``detailed_runs`` is set to ``True``::

              [
                {
                  "text": "faded",
                  "runs": [
                    {
                      "text": "fade",
                      "bold": true
                    },
                    {
                      "text": "d"
                    }
                  ]
                },
                {
                  "text": "faded alan walker lyrics",
                  "runs": [
                    {
                      "text": "fade",
                      "bold": true
                    },
                    {
                      "text": "d alan walker lyrics"
                    }
                  ]
                },
                {
                  "text": "faded alan walker",
                  "runs": [
                    {
                      "text": "fade",
                      "bold": true
                    },
                    {
                      "text": "d alan walker"
                    }
                  ]
                },
                ...
              ]
        """

        body = {"input": query}
        endpoint = "music/get_search_suggestions"

        response = self._send_request(endpoint, body)
        search_suggestions = parse_search_suggestions(response, detailed_runs)

        return search_suggestions
