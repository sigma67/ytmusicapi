from .utils import *
from typing import List


def parse_playlist_items(results, menu_entries: List[List] = None):
    songs = []
    count = 1
    for result in results:
        count += 1
        if 'musicResponsiveListItemRenderer' not in result:
            continue
        data = result['musicResponsiveListItemRenderer']

        try:
            videoId = setVideoId = None
            like = None

            # if the item has a menu, find its setVideoId
            if 'menu' in data:
                for item in reversed(nav(data, MENU_ITEMS)):
                    if 'menuServiceItemRenderer' in item and 'playlistEditEndpoint' in nav(
                            item, MENU_SERVICE):
                        setVideoId = nav(
                            item, MENU_SERVICE)['playlistEditEndpoint']['actions'][0]['setVideoId']
                        videoId = nav(
                            item,
                            MENU_SERVICE)['playlistEditEndpoint']['actions'][0]['removedVideoId']
                        break

            # if item is not playable, the videoId was retrieved above
            if 'playNavigationEndpoint' in nav(data, PLAY_BUTTON):
                videoId = nav(data,
                              PLAY_BUTTON)['playNavigationEndpoint']['watchEndpoint']['videoId']

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

            if menu_entries:
                for menu_entry in menu_entries:
                    song[menu_entry[-1]] = nav(data, MENU_ITEMS + menu_entry)

            songs.append(song)

        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs
