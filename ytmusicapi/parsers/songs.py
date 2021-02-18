from .utils import *
import re


def parse_song_artists(data, index):
    flex_item = get_flex_column_item(data, index)
    if not flex_item:
        return None
    else:
        runs = flex_item['text']['runs']
        artists = []
        for j in range(int(len(runs) / 2) + 1):
            artists.append({
                'name': runs[j * 2]['text'],
                'id': nav(runs[j * 2], NAVIGATION_BROWSE_ID, True)
            })
        return artists


def parse_song_runs(runs):
    parsed = {'artists': []}
    for run in runs:
        text = run['text']
        if 'navigationEndpoint' in run:  # artist or album
            item = {'name': text, 'id': nav(run, NAVIGATION_BROWSE_ID, True)}

            if item['id'] and item['id'].startswith('MPRE'):  # album
                parsed['album'] = item
            else:  # artist
                parsed['artists'].append(item)

        else:
            # note: YT uses non-breaking space \xa0 to separate number and magnitude
            if re.match(r"^\d([^ ])* [^ ]*$", text):
                parsed['views'] = text.split(' ')[0]

            elif re.match(r"^(\d+:)*\d+:\d+$", text):
                parsed['duration'] = text

            elif re.match(r"^\d{4}$", text):
                parsed['year'] = text

    return parsed


def parse_song_album(data, index):
    flex_item = get_flex_column_item(data, index)
    return None if not flex_item else {
        'name': get_item_text(data, index),
        'id': get_browse_id(flex_item, 0)
    }


def parse_song_menu_tokens(item):
    library_add_token = library_remove_token = None
    toggle_menu = item['toggleMenuServiceItemRenderer']
    service_type = toggle_menu['defaultIcon']['iconType']
    if service_type == "LIBRARY_ADD":
        library_add_token = nav(toggle_menu, ['defaultServiceEndpoint'] + FEEDBACK_TOKEN)
        library_remove_token = nav(toggle_menu, ['toggledServiceEndpoint'] + FEEDBACK_TOKEN)

    elif service_type == "LIBRARY_REMOVE":  # swap if already in library
        library_add_token, library_remove_token = library_remove_token, library_add_token

    return {'add': library_add_token, 'remove': library_remove_token}



