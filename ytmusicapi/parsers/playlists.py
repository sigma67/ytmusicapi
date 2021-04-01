from .utils import *
from .songs import *
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
            feedback_tokens = None

            # if the item has a menu, find its setVideoId
            if 'menu' in data:
                for item in nav(data, MENU_ITEMS):
                    if 'menuServiceItemRenderer' in item:
                        menu_service = nav(item, MENU_SERVICE)
                        if 'playlistEditEndpoint' in menu_service:
                            setVideoId = menu_service['playlistEditEndpoint']['actions'][0][
                                'setVideoId']
                            videoId = menu_service['playlistEditEndpoint']['actions'][0][
                                'removedVideoId']

                    if TOGGLE_MENU in item:
                        feedback_tokens = parse_song_menu_tokens(item)

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
                if 'simpleText' in get_fixed_column_item(data, 0)['text']:
                    duration = get_fixed_column_item(data, 0)['text']['simpleText']
                else:
                    duration = get_fixed_column_item(data, 0)['text']['runs'][0]['text']

            thumbnails = None
            if 'thumbnail' in data:
                thumbnails = nav(data, THUMBNAILS)

            isAvailable = True
            if 'musicItemRendererDisplayPolicy' in data:
                isAvailable = data[
                    'musicItemRendererDisplayPolicy'] != 'MUSIC_ITEM_RENDERER_DISPLAY_POLICY_GREY_OUT'

            isExplicit = nav(data, BADGE_LABEL, True) == 'Explicit'

            song = {
                'videoId': videoId,
                'title': title,
                'artists': artists,
                'album': album,
                'likeStatus': like,
                'thumbnails': thumbnails,
                'isAvailable': isAvailable,
                'isExplicit': isExplicit
            }
            if duration:
                song['duration'] = duration
            if setVideoId:
                song['setVideoId'] = setVideoId
            if feedback_tokens:
                song['feedbackTokens'] = feedback_tokens

            if menu_entries:
                for menu_entry in menu_entries:
                    song[menu_entry[-1]] = nav(data, MENU_ITEMS + menu_entry)

            songs.append(song)

        except Exception as e:
            print("Item " + str(count) + ": " + str(e))

    return songs
