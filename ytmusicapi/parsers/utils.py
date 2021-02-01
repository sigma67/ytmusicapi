from . import *
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
            item = {
                'name': text,
                'id': nav(run, NAVIGATION_BROWSE_ID, True)
            }

            if item['id'] and item['id'].startswith('MPRE'):  # album
                parsed['album'] = item
            else:  # artist
                parsed['artists'].append(item)

        else:
            if text.endswith(' views'):
                parsed['views'] = text.split(' ')[0]

            elif re.match(r"^\d+:\d+$", text):
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


def parse_menu_playlists(data, result):
    watch_menu = find_objects_by_key(nav(data, MENU_ITEMS), 'menuNavigationItemRenderer')
    for item in [_x['menuNavigationItemRenderer'] for _x in watch_menu]:
        icon = nav(item, ['icon', 'iconType'])
        if icon == 'MUSIC_SHUFFLE':
            watch_key = 'shuffleId'
        elif icon == 'MIX':
            watch_key = 'radioId'
        else:
            continue

        watch_id = nav(item, ['navigationEndpoint', 'watchPlaylistEndpoint', 'playlistId'], True)
        if not watch_id:
            watch_id = nav(item, ['navigationEndpoint', 'watchEndpoint', 'playlistId'], True)
        if watch_id:
            result[watch_key] = watch_id


def get_item_text(item, index, run_index=0, none_if_absent=False):
    column = get_flex_column_item(item, index)
    if not column:
        return None
    if none_if_absent and len(column['text']['runs']) < run_index + 1:
        return None
    return column['text']['runs'][run_index]['text']


def get_flex_column_item(item, index):
    if 'text' not in item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer'] or \
            'runs' not in item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer']['text']:
        return None

    return item['flexColumns'][index]['musicResponsiveListItemFlexColumnRenderer']


def get_fixed_column_item(item, index):
    if 'text' not in item['fixedColumns'][index]['musicResponsiveListItemFixedColumnRenderer'] or \
            'runs' not in item['fixedColumns'][index]['musicResponsiveListItemFixedColumnRenderer']['text']:
        return None

    return item['fixedColumns'][index]['musicResponsiveListItemFixedColumnRenderer']


def get_browse_id(item, index):
    if 'navigationEndpoint' not in item['text']['runs'][index]:
        return None
    else:
        return nav(item['text']['runs'][index], NAVIGATION_BROWSE_ID)


def get_continuations(results, continuation_type, limit, request_func, parse_func, ctoken_path=""):
    items = []
    while 'continuations' in results and len(items) < limit:
        additionalParams = get_continuation_params(results, ctoken_path)
        response = request_func(additionalParams)
        if 'continuationContents' in response:
            results = response['continuationContents'][continuation_type]
        else:
            break
        contents = get_continuation_contents(results, parse_func)
        if len(contents) == 0:
            break
        items.extend(contents)

    return items


def get_validated_continuations(results,
                                continuation_type,
                                limit,
                                per_page,
                                request_func,
                                parse_func,
                                ctoken_path=""):
    items = []
    while 'continuations' in results and len(items) < limit:
        additionalParams = get_continuation_params(results, ctoken_path)
        wrapped_parse_func = lambda raw_response: get_parsed_continuation_items(
            raw_response, parse_func, continuation_type)
        validate_func = lambda parsed: validate_response(parsed, per_page, limit, len(items))

        response = resend_request_until_parsed_response_is_valid(request_func, additionalParams,
                                                                 wrapped_parse_func, validate_func,
                                                                 3)
        results = response['results']
        items.extend(response['parsed'])

    return items


def get_parsed_continuation_items(response, parse_func, continuation_type):
    results = response['continuationContents'][continuation_type]
    return {'results': results, 'parsed': get_continuation_contents(results, parse_func)}


def get_continuation_params(results, ctoken_path):
    ctoken = nav(results,
                 ['continuations', 0, 'next' + ctoken_path + 'ContinuationData', 'continuation'])
    return "&ctoken=" + ctoken + "&continuation=" + ctoken


def get_continuation_contents(continuation, parse_func):
    for term in ['contents', 'items']:
        if term in continuation:
            return parse_func(continuation[term])

    return []


def resend_request_until_parsed_response_is_valid(request_func, request_additional_params,
                                                  parse_func, validate_func, max_retries):
    response = request_func(request_additional_params)
    parsed_object = parse_func(response)
    retry_counter = 0
    while not validate_func(parsed_object) and retry_counter < max_retries:
        response = request_func(request_additional_params)
        attempt = parse_func(response)
        if len(attempt['parsed']) > len(parsed_object['parsed']):
            parsed_object = attempt
        retry_counter += 1

    return parsed_object


def validate_response(response, per_page, limit, current_count):
    remaining_items_count = limit - current_count
    expected_items_count = min(per_page, remaining_items_count)

    # response is invalid, if it has less items then minimal expected count
    return len(response['parsed']) >= expected_items_count


def nav(root, items, none_if_absent=False):
    """Access a nested object in root by item sequence."""
    try:
        for k in items:
            root = root[k]
        return root
    except Exception as err:
        if none_if_absent:
            return None
        else:
            raise err


def find_object_by_key(object_list, key, nested=None, is_key=False):
    for item in object_list:
        if nested:
            item = item[nested]
        if key in item:
            return item[key] if is_key else item
    return None


def find_objects_by_key(object_list, key, nested=None):
    objects = []
    for item in object_list:
        if nested:
            item = item[nested]
        if key in item:
            objects.append(item)
    return objects
