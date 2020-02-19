from ytmusicapi.ytmusic import YTMusic

# YTMusic.get_playlist_items("PLQwVIlKxHM6qgidcRDp0-KFY1JmdGS206")
youtube = YTMusic()
youtube_auth = YTMusic('../headers_auth.json')

def get_foreign_playlist():
    songs = youtube.get_playlist_items("PLw-VjHDlEOgs658kAHR_LAaILBXb-s6Q5")
    assert (len(songs) == 200)


def get_owned_playlist():
    songs = youtube_auth.get_playlist_items('PLQwVIlKxHM6oCeKLTsUx_w9CmWjHKdg68')
    assert (len(songs) == 64)

def search():
    results = youtube_auth.search("Oasis Wonderwall")
    print(results)

#end to end test adding playlist, adding item, deleting item, deleting playlist
def end2end():
    playlist = youtube_auth.add_playlist("test", "test description", False)
    print(playlist)
    response = youtube_auth.add_playlist_item(playlist, 'y0Hhvtmv0gk')
    assert(response['status'] == 'STATUS_SUCCEEDED')
    items = youtube_auth.get_playlist_items(playlist)
    assert(len(items) == 1)
    response = youtube_auth.remove_playlist_item(playlist, items[0])
    assert(response['status'] == 'STATUS_SUCCEEDED')
    response = youtube_auth.delete_playlist(playlist)
    assert(response['command']['handlePlaylistDeletionCommand']['playlistId'] == playlist)

# youtube.add_playlist_item('PLQwVIlKxHM6p6LRH_53M7tvRXaz0eVzpa', 'y0Hhvtmv0gk')
# songs = youtube.get_playlist_items("PLw-VjHDlEOgs658kAHR_LAaILBXb-s6Q5")
# for song in songs:
#     youtube.add_playlist_item('PLQwVIlKxHM6p6LRH_53M7tvRXaz0eVzpa', song['videoId'])
# songs = youtube.get_playlist_items("PLQwVIlKxHM6p6LRH_53M7tvRXaz0eVzpa")
# for song in songs:
#     youtube.remove_playlist_item("PLQwVIlKxHM6p6LRH_53M7tvRXaz0eVzpa", song['removeAction'])
# id = youtube.add_playlist("test3", "test description", True)
# youtube.remove_playlist_item('PLQwVIlKxHM6rPU4UadJV7UZf9miJcK-hm', 'cilnCQMJudo')
# YTMusic.search('lione revive')

if __name__ == '__main__':
    #end2end()
    search()
