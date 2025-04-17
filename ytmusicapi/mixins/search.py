from ytmusicapi.continuations import get_continuations
from ytmusicapi.exceptions import YTMusicUserError
from ytmusicapi.mixins._protocol import MixinProtocol
from ytmusicapi.parsers.search import *
from ytmusicapi.type_alias import JsonList, ParseFuncType, RequestFuncType


class SearchMixin(MixinProtocol):
    def search(
        self,
        query: str,
        filter: str | None = None,
        scope: str | None = None,
        limit: int = 20,
        ignore_spelling: bool = False,
    ) -> JsonList:
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
          albumId, channelId and playlistId (browseId=`VL`+playlistId)

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
                "browseId": "MPREb_IInSY5QXXrW",
                "playlistId": "OLAK5uy_kunInnOpcKECWIBQGB0Qj6ZjquxDvfckg",
                "title": "(What's The Story) Morning Glory?",
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
        search_results: JsonList = []
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
            raise YTMusicUserError(
                "Invalid filter provided. Please use one of the following filters or leave out the parameter: "
                + ", ".join(filters)
            )

        scopes = ["library", "uploads"]
        if scope and scope not in scopes:
            raise YTMusicUserError(
                "Invalid scope provided. Please use one of the following scopes or leave out the parameter: "
                + ", ".join(scopes)
            )

        if scope == scopes[1] and filter:
            raise YTMusicUserError(
                "No filter can be set when searching uploads. Please unset the filter parameter when scope is set to "
                "uploads. "
            )

        if scope == scopes[0] and filter in filters[3:5]:
            raise YTMusicUserError(
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

        section_list = nav(results, SECTION_LIST)

        # no results
        if len(section_list) == 1 and "itemSectionRenderer" in section_list:
            return search_results

        # set filter for parser
        result_type = None
        if filter and "playlists" in filter:
            filter = "playlists"
        elif scope == scopes[1]:  # uploads
            filter = scopes[1]
            result_type = scopes[1][:-1]

        for res in section_list:
            category = None

            if "musicCardShelfRenderer" in res:
                top_result = parse_top_result(
                    res["musicCardShelfRenderer"], self.parser.get_search_result_types()
                )
                search_results.append(top_result)
                if not (shelf_contents := nav(res, ["musicCardShelfRenderer", "contents"], True)):
                    continue
                # if "more from youtube" is present, remove it - it's not parseable
                if "messageRenderer" in shelf_contents[0]:
                    category = nav(shelf_contents.pop(0), ["messageRenderer", *TEXT_RUN_TEXT])

            elif "musicShelfRenderer" in res:
                shelf_contents = res["musicShelfRenderer"]["contents"]
                category = nav(res, MUSIC_SHELF + TITLE_TEXT, True)

                # if we know the filter it's easy to set the result type
                # unfortunately uploads is modeled as a filter (historical reasons),
                #  so we take care to not set the result type for that scope
                if filter and not scope == scopes[1]:
                    result_type = filter[:-1].lower()

            else:
                continue

            api_search_result_types = self.parser.get_api_result_types()

            search_results.extend(
                parse_search_results(shelf_contents, api_search_result_types, result_type, category)
            )

            if filter:  # if filter is set, there are continuations
                request_func: RequestFuncType = lambda additionalParams: self._send_request(
                    endpoint, body, additionalParams
                )
                parse_func: ParseFuncType = lambda contents: parse_search_results(
                    contents, api_search_result_types, result_type, category
                )

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

    def get_search_suggestions(self, query: str, detailed_runs: bool = False) -> list[str] | JsonList:
        """
        Get Search Suggestions

        :param query: Query string, i.e. 'faded'
        :param detailed_runs: Whether to return detailed runs of each suggestion.
            If True, it returns the query that the user typed and the remaining
            suggestion along with the complete text (like many search services
            usually bold the text typed by the user).
            Default: False, returns the list of search suggestions in plain text.
        :return: A list of search suggestions. If ``detailed_runs`` is False, it returns plain text suggestions.
              If ``detailed_runs`` is True, it returns a list of dictionaries with detailed information.

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
                  ],
                  "fromHistory": true,
                  "feedbackToken": "AEEJK..."
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
                  ],
                  "fromHistory": false,
                  "feedbackToken": None
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
                  ],
                  "fromHistory": false,
                  "feedbackToken": None
                },
                ...
              ]
        """
        body = {"input": query}
        endpoint = "music/get_search_suggestions"

        response = self._send_request(endpoint, body)

        return parse_search_suggestions(response, detailed_runs)

    def remove_search_suggestions(self, suggestions: JsonList, indices: list[int] | None = None) -> bool:
        """
        Remove search suggestion from the user search history.

        :param suggestions: The dictionary obtained from the :py:func:`get_search_suggestions`
            (with detailed_runs=True)`
        :param indices: Optional. The indices of the suggestions to be removed. Default: remove all suggestions.
        :return: True if the operation was successful, False otherwise.

          Example usage::

              # Removing suggestion number 0
              suggestions = ytmusic.get_search_suggestions(query="fade", detailed_runs=True)
              success = ytmusic.remove_search_suggestions(suggestions=suggestions, indices=[0])
              if success:
                  print("Suggestion removed successfully")
              else:
                  print("Failed to remove suggestion")
        """
        if not any(run["fromHistory"] for run in suggestions):
            raise YTMusicUserError(
                "No search result from history provided. "
                "Please run get_search_suggestions first to retrieve suggestions. "
                "Ensure that you have searched a similar term before."
            )

        if indices is None:
            indices = list(range(len(suggestions)))

        if any(index >= len(suggestions) for index in indices):
            raise YTMusicUserError("Index out of range. Index must be smaller than the length of suggestions")

        feedback_tokens = [suggestions[index]["feedbackToken"] for index in indices]
        if all(feedback_token is None for feedback_token in feedback_tokens):
            return False

        # filter None tokens
        feedback_tokens = [token for token in feedback_tokens if token is not None]

        body = {"feedbackTokens": feedback_tokens}
        endpoint = "feedback"

        response = self._send_request(endpoint, body)

        return bool(nav(response, ["feedbackResponses", 0, "isProcessed"], none_if_absent=True))
