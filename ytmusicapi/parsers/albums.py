from .utils import *
from ytmusicapi.helpers import to_int
from .songs import parse_song_runs, parse_like_status


def parse_album_header(response):
    header = nav(response, HEADER_DETAIL)
    album = {
        'title': nav(header, TITLE_TEXT),
        'type': nav(header, SUBTITLE),
        'thumbnails': nav(header, THUMBNAIL_CROPPED)
    }
    if "description" in header:
        album["description"] = header["description"]["runs"][0]["text"]

    album_info = parse_song_runs(header['subtitle']['runs'][2:])
    album.update(album_info)

    if len(header['secondSubtitle']['runs']) > 1:
        album['trackCount'] = to_int(header['secondSubtitle']['runs'][0]['text'])
        album['duration'] = header['secondSubtitle']['runs'][2]['text']
    else:
        album['duration'] = header['secondSubtitle']['runs'][0]['text']

    # add to library/uploaded
    menu = nav(header, MENU)
    toplevel = menu['topLevelButtons']
    album['audioPlaylistId'] = nav(toplevel, [0, 'buttonRenderer'] + NAVIGATION_PLAYLIST_ID)
    service = nav(toplevel, [1, 'buttonRenderer', 'defaultServiceEndpoint'], True)
    if service:
        album['likeStatus'] = parse_like_status(service)

    return album
