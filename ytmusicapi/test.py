import unittest
from ytmusicapi.ytmusic import YTMusic

youtube = YTMusic()
youtube_auth = YTMusic('../headers_auth.json')


class TestYTMusic(unittest.TestCase):
    def test_setup(self):
        YTMusic.setup()

    ###############
    # BROWSING
    ###############

    def test_search(self):
        results = youtube_auth.search("Oasis Wonderwall")
        self.assertGreater(len(results), 0)

    def test_get_artist(self):
        results = youtube.get_artist("UCmMUZbaYdNH0bEd1PAlAqsA")
        self.assertEqual(len(results), 7)

    def test_get_artist_albums(self):
        artist = youtube.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = youtube.get_artist_albums(artist['albums']['browseId'], artist['albums']['params'])
        self.assertGreater(len(results), 0)

    def test_get_artist_singles(self):
        artist = youtube_auth.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = youtube_auth.get_artist_albums(artist['singles']['browseId'], artist['singles']['params'])
        self.assertGreater(len(results), 0)

    def test_get_album(self):
        results = youtube.get_album("MPREb_BQZvl3BFGay")
        self.assertEqual(len(results), 4)
        self.assertEqual(len(results['tracks']), 7)

    ###############
    # LIBRARY
    ###############

    def test_get_liked_songs(self):
        songs = youtube_auth.get_liked_songs(100)
        self.assertGreater(len(songs), 0)

    def test_get_history(self):
        songs = youtube_auth.get_history()
        self.assertGreater(len(songs), 0)

    def test_rate_song(self):
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'LIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'INDIFFERENT')
        self.assertIn('actions', response)

    def test_rate_playlist(self):
        response = youtube_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4', 'DISLIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4', 'INDIFFERENT')
        self.assertIn('actions', response)

    def test_subscribe_artists(self):
        youtube_auth.subscribe_artists(['UCmMUZbaYdNH0bEd1PAlAqsA', 'UCEPMVbUzImPl4p8k4LkGevA'])
        youtube_auth.unsubscribe_artists(['UCmMUZbaYdNH0bEd1PAlAqsA', 'UCEPMVbUzImPl4p8k4LkGevA'])

    ###############
    # PLAYLISTS
    ###############

    def test_get_playlists(self):
        playlists = youtube_auth.get_playlists()
        self.assertGreater(len(playlists), 0)

    def test_get_foreign_playlist(self):
        songs = youtube.get_playlist_items("PLw-VjHDlEOgs658kAHR_LAaILBXb-s6Q5")
        self.assertEqual(len(songs), 200)

    def test_get_owned_playlist(self):
        songs = youtube_auth.get_playlist_items('PL528pVfw3ao2VzfY6zE1TOZm1cBSdk7Q0')
        self.assertEqual(len(songs), 287)

    ###############
    # UPLOADS
    ###############

    def test_get_uploaded_songs(self):
        results = youtube_auth.get_uploaded_songs(126)
        self.assertEqual(len(results), 126)

    def test_upload_song(self):
        response = youtube_auth.upload_song('../12 - Turning Point 자.mp3')
        self.assertEqual(response, 'STATUS_SUCCEEDED')

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
