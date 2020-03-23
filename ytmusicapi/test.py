import unittest
from ytmusicapi.ytmusic import YTMusic

youtube = YTMusic()
youtube_auth = YTMusic('../headers_auth.json')


class TestYTMusic(unittest.TestCase):
    def test_setup(self):
        YTMusic.setup()

    def test_get_playlists(self):
        playlists = youtube_auth.get_playlists()
        self.assertGreater(len(playlists), 0)

    def test_get_foreign_playlist(self):
        songs = youtube.get_playlist_items("PLw-VjHDlEOgs658kAHR_LAaILBXb-s6Q5")
        self.assertEqual(len(songs), 200)

    def test_get_owned_playlist(self):
        songs = youtube_auth.get_playlist_items('PLQwVIlKxHM6oCeKLTsUx_w9CmWjHKdg68')
        self.assertEqual(len(songs), 64)

    def test_get_history(self):
        songs = youtube_auth.get_history()
        self.assertGreater(len(songs), 0)

    def test_search(self):
        results = youtube_auth.search("Oasis Wonderwall")
        self.assertGreater(len(results), 0)

    def test_get_uploaded_songs(self):
        results = youtube_auth.get_uploaded_songs(50)
        self.assertEqual(len(results), 50)

    def test_upload_song(self):
        response = youtube_auth.upload_song('../12 - Turning Point.mp3')
        self.assertEqual(response, 'OK')

    def test_delete_uploaded_song(self):
        results = youtube_auth.get_uploaded_songs()
        response = youtube_auth.delete_uploaded_song(results[0])
        self.assertEqual(response, 'STATUS_SUCCEEDED')

    # end to end test adding playlist, adding item, deleting item, deleting playlist
    def test_end2end(self):
        playlist = youtube_auth.create_playlist("test", "test description")
        self.assertEqual(len(playlist), 34, "Playlist creation failed")
        response = youtube_auth.add_playlist_items(playlist, ['y0Hhvtmv0gk'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Adding playlist item failed")
        items = youtube_auth.get_playlist_items(playlist)
        self.assertEqual(len(items), 1, "Getting playlist items failed")
        response = youtube_auth.remove_playlist_items(playlist, items)
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist item removal failed")
        response = youtube_auth.delete_playlist(playlist)
        self.assertEqual(response['command']['handlePlaylistDeletionCommand']['playlistId'], playlist, "Playlist removal failed")


if __name__ == '__main__':
    unittest.main()
