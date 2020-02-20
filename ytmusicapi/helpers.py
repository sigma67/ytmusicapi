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
            else:
                videoId = None

            # if playlist is not owned, the playlist item can't be interacted with
            setVideoId = data['playlistItemData']['playlistSetVideoId'] if 'playlistItemData' in data else None

            artist = data['flexColumns'][1]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
            title = data['flexColumns'][0]['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text']
            song = {'videoId': videoId, 'artist': artist, 'title': title, 'setVideoId': setVideoId}
            songs.append(song)
        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs