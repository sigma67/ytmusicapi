FILTERED_PARAM1 = 'EgWKAQI'


def get_search_params(filter, scope, ignore_spelling):
    params = None
    if filter is None and scope is None and not ignore_spelling:
        return params

    if scope == 'uploads':
        params = 'agIYAw%3D%3D'

    if scope == 'library':
        if filter:
            param1 = FILTERED_PARAM1
            param2 = _get_param2(filter)
            param3 = 'AWoKEAUQCRADEAoYBA%3D%3D'
        else:
            params = 'agIYBA%3D%3D'

    if scope is None and filter:
        if filter == 'playlists':
            params = 'Eg-KAQwIABAAGAAgACgB'
            if not ignore_spelling:
                params += 'MABqChAEEAMQCRAFEAo%3D'
            else:
                params += 'MABCAggBagoQBBADEAkQBRAK'

        elif 'playlists' in filter:
            param1 = 'EgeKAQQoA'
            if filter == 'featured_playlists':
                param2 = 'Dg'
            else:  # community_playlists
                param2 = 'EA'

            if not ignore_spelling:
                param3 = 'BagwQDhAKEAMQBBAJEAU%3D'
            else:
                param3 = 'BQgIIAWoMEA4QChADEAQQCRAF'

        else:
            param1 = FILTERED_PARAM1
            param2 = _get_param2(filter)
            if not ignore_spelling:
                param3 = 'AWoMEA4QChADEAQQCRAF'
            else:
                param3 = 'AUICCAFqDBAOEAoQAxAEEAkQBQ%3D%3D'

    if not scope and not filter and ignore_spelling:
        params = 'EhGKAQ4IARABGAEgASgAOAFAAUICCAE%3D'

    return params if params else param1 + param2 + param3


def _get_param2(filter):
    filter_params = {'songs': 'I', 'videos': 'Q', 'albums': 'Y', 'artists': 'g', 'playlists': 'o'}
    return filter_params[filter]