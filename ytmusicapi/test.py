from ytmusicapi.ytmusic import YTMusic

youtube = YTMusic()
youtube_auth = YTMusic('../headers_auth.json')


def get_playlists():
    playlists = youtube.get_playlists()
    print(playlists)


def get_foreign_playlist():
    songs = youtube.get_playlist_items("PLw-VjHDlEOgs658kAHR_LAaILBXb-s6Q5")
    assert (len(songs) == 200)


def get_owned_playlist():
    songs = youtube_auth.get_playlist_items('PLQwVIlKxHM6oCeKLTsUx_w9CmWjHKdg68')
    assert (len(songs) == 64)


def get_history():
    songs = youtube_auth.get_history()
    assert (len(songs) > 0)

def search():
    results = youtube_auth.search("Oasis Wonderwall")
    print(results)


#end to end test adding playlist, adding item, deleting item, deleting playlist
def end2end():
    playlist = youtube_auth.create_playlist("test", "test description")
    print(playlist)
    response = youtube_auth.add_playlist_items(playlist,['y0Hhvtmv0gk'])
    assert(response == 'STATUS_SUCCEEDED')
    items = youtube_auth.get_playlist_items(playlist)
    assert(len(items) == 1)
    response = youtube_auth.remove_playlist_items(playlist, items)
    assert(response == 'STATUS_SUCCEEDED')
    response = youtube_auth.delete_playlist(playlist)
    assert(response['command']['handlePlaylistDeletionCommand']['playlistId'] == playlist)


if __name__ == '__main__':
    end2end()
    #get_history()
    #search()
    #get_owned_playlist()
