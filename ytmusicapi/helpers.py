## Static helper methods

def parse_songs(results):
    songs = []
    count = 1
    for result in results:
        count += 1
        if not 'musicResponsiveListItemRenderer' in result:
            continue
        data = result['musicResponsiveListItemRenderer']
        try:
            # if item is not playable, there is not videoId
            if 'playNavigationEndpoint' in data['overlay']['musicItemThumbnailOverlayRenderer']['content']['musicPlayButtonRenderer']:
                videoId = data['overlay']['musicItemThumbnailOverlayRenderer']['content']['musicPlayButtonRenderer']['playNavigationEndpoint']['watchEndpoint']['videoId']

                # if playlist is not owned, removal is not possible
                if 'menuServiceItemRenderer' in data['menu']['menuRenderer']['items'][4]:
                    removeAction = \
                        data['menu']['menuRenderer']['items'][4]['menuServiceItemRenderer']['serviceEndpoint']['playlistEditEndpoint']['actions'][0]
                else:
                    removeAction = None

            else:
                videoId = None

            artist = data['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
            title = data['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
            song = {'videoId': videoId, 'artist': artist, 'title': title, 'removeAction': removeAction}
            songs.append(song)
        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs