from .utils import *


def parse_playlist_items(results):
    songs = []
    count = 1
    for result in results:
        count += 1
        if 'musicResponsiveListItemRenderer' not in result:
            continue
        data = result['musicResponsiveListItemRenderer']

        try:
            # if playlist is not owned, the playlist item can't be interacted with
            videoId = setVideoId = None
            like = None

            # if item is not playable, there is no videoId
            if 'playNavigationEndpoint' in nav(data, PLAY_BUTTON):
                videoId = nav(data,
                              PLAY_BUTTON)['playNavigationEndpoint']['watchEndpoint']['videoId']

                for item in nav(data, MENU_ITEMS):
                    if 'menuServiceItemRenderer' in item and 'playlistEditEndpoint' in nav(
                            item, MENU_SERVICE):
                        setVideoId = nav(
                            item, MENU_SERVICE)['playlistEditEndpoint']['actions'][0]['setVideoId']
                        break

                if 'menu' in data:
                    like = nav(data, MENU_LIKE_STATUS, True)

            title = get_item_text(data, 0)
            if title == 'Song deleted':
                continue

            artists = parse_song_artists(data, 1)

            album = parse_song_album(data, 2)

            duration = None
            if 'fixedColumns' in data:
                if 'simpleText' in data['fixedColumns'][0][
                        'musicResponsiveListItemFixedColumnRenderer']['text']:
                    duration = data['fixedColumns'][0][
                        'musicResponsiveListItemFixedColumnRenderer']['text']['simpleText']
                else:
                    duration = data['fixedColumns'][0][
                        'musicResponsiveListItemFixedColumnRenderer']['text']['runs'][0]['text']

            thumbnails = None
            if 'thumbnail' in data:
                thumbnails = nav(data, THUMBNAILS)

            song = {
                'videoId': videoId,
                'title': title,
                'artists': artists,
                'album': album,
                'likeStatus': like,
                'thumbnails': thumbnails
            }
            if duration:
                song['duration'] = duration
            if setVideoId:
                song['setVideoId'] = setVideoId

            songs.append(song)

        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs
