filters = [
    'albums', 'artists', 'playlists', 'community_playlists', 'featured_playlists', 'songs',
    'videos'
]    

def filter_exception(filter):

    if filter and filter not in filters:
        raise Exception(
            "Invalid filter provided. Please use one of the following filters or leave out the parameter: "
            + ', '.join(filters))        