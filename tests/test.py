import unittest
import configparser
import sys
sys.path.insert(0, '..')
from ytmusicapi.ytmusic import YTMusic  # noqa: E402

config = configparser.RawConfigParser()
config.read('./test.cfg', 'utf-8')

youtube = YTMusic()
youtube_auth = YTMusic(config['auth']['headers_file'])
youtube_brand = YTMusic(config['auth']['headers'], config['auth']['brand_account'])


class TestYTMusic(unittest.TestCase):
    def test_init(self):
        self.assertRaises(Exception, YTMusic, "{}")

    def test_setup(self):
        YTMusic.setup(config['auth']['headers_file'], config['auth']['headers_raw'])

    ###############
    # BROWSING
    ###############

    def test_search(self):
        query = "Oasis Wonderwall"
        self.assertRaises(Exception, youtube_auth.search, query, "song")
        results = youtube_auth.search(query)
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'songs')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'videos')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'albums')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'artists')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'playlists')
        self.assertGreater(len(results), 0)

    def test_get_artist(self):
        results = youtube.get_artist("UCmMUZbaYdNH0bEd1PAlAqsA")
        self.assertEqual(len(results), 11)
        results = youtube.get_artist("UCLZ7tlKC06ResyDmEStSrOw")  # no album year
        self.assertGreaterEqual(len(results), 10)
        results = youtube.get_artist(
            "UCDAPd3S5CBIEKXn-tvy57Lg")  # no thumbnail, albums, subscribe count
        self.assertGreaterEqual(len(results), 9)

    def test_get_artist_albums(self):
        artist = youtube.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = youtube.get_artist_albums(artist['albums']['browseId'],
                                            artist['albums']['params'])
        self.assertGreater(len(results), 0)

    def test_get_artist_singles(self):
        artist = youtube_auth.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = youtube_auth.get_artist_albums(artist['singles']['browseId'],
                                                 artist['singles']['params'])
        self.assertGreater(len(results), 0)

    def test_get_user(self):
        results = youtube.get_user("UC44hbeRoCZVVMVg5z0FfIww")
        self.assertEqual(len(results), 3)

    def test_get_user_playlists(self):
        results = youtube.get_user("UCPVhZsC2od1xjGhgEc2NEPQ")
        results = youtube.get_user_playlists("UCPVhZsC2od1xjGhgEc2NEPQ",
                                             results['playlists']['params'])
        self.assertGreater(len(results), 100)

    def test_get_album(self):
        results = youtube_auth.get_album("MPREb_BQZvl3BFGay")
        self.assertEqual(len(results), 9)
        self.assertEqual(len(results['tracks']), 7)

    def test_get_song(self):
        song = youtube.get_song("ZrOKjDZOtkA")
        self.assertGreaterEqual(len(song), 17)

    ###############
    # WATCH
    ###############

    def test_get_watch_playlist(self):
        playlist = youtube.get_watch_playlist("4y33h81phKU", limit=50)
        self.assertGreater(len(playlist), 50)

    def test_get_watch_playlist_shuffle(self):
        playlist = youtube.get_watch_playlist_shuffle(
            playlistId="OLAK5uy_lKgoGvlrWhX0EIPavQUXxyPed8Cj38AWc")
        self.assertEqual(len(playlist), 12)

    def test_get_watch_playlist_shuffle_playlist(self):
        playlist = youtube.get_watch_playlist_shuffle(
            playlistId="PL528pVfw3ao0x8jlW3kwdIx1FEMMeeghb", limit=99)
        self.assertGreaterEqual(len(playlist), 99)

    ###############
    # LIBRARY
    ###############

    def test_get_library_playlists(self):
        playlists = youtube_brand.get_library_playlists(50)
        self.assertGreater(len(playlists), 0)

    def test_get_library_songs(self):
        songs = youtube_brand.get_library_songs(100)
        self.assertGreater(len(songs), 0)

    def test_get_library_albums(self):
        albums = youtube_brand.get_library_albums(100)
        self.assertGreater(len(albums), 0)

    def test_get_library_artists(self):
        artists = youtube_brand.get_library_artists(100)
        self.assertGreater(len(artists), 0)

    def test_get_library_subscriptions(self):
        artists = youtube_brand.get_library_subscriptions(50)
        self.assertGreater(len(artists), 0)

    def test_get_liked_songs(self):
        songs = youtube_brand.get_liked_songs(200)
        self.assertGreater(len(songs['tracks']), 100)

    def test_get_history(self):
        songs = youtube_auth.get_history()
        self.assertGreater(len(songs), 0)

    def test_rate_song(self):
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'LIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'INDIFFERENT')
        self.assertIn('actions', response)

    def test_rate_playlist(self):
        response = youtube_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4', 'LIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4',
                                              'INDIFFERENT')
        self.assertIn('actions', response)

    def test_subscribe_artists(self):
        youtube_auth.subscribe_artists(['UCUDVBtnOQi4c7E8jebpjc9Q', 'UCiMhD4jzUqG-IgPzUmmytRQ'])
        youtube_auth.unsubscribe_artists(['UCUDVBtnOQi4c7E8jebpjc9Q', 'UCiMhD4jzUqG-IgPzUmmytRQ'])

    ###############
    # PLAYLISTS
    ###############

    def test_get_foreign_playlist(self):
        playlist = youtube.get_playlist("PL6bPxvf5dW5clc3y9wAoslzqUrmkZ5c-u", 300)
        self.assertGreater(len(playlist['tracks']), 200)

    def test_get_owned_playlist(self):
        playlist = youtube_auth.get_playlist(config['playlists']['own'], 300)
        self.assertGreater(len(playlist['tracks']), 200)

    def test_edit_playlist(self):
        playlist = youtube_auth.get_playlist(config['playlists']['own'])
        response = youtube_auth.edit_playlist(playlist['id'],
                                              title='',
                                              description='',
                                              privacyStatus='PRIVATE',
                                              moveItem=(playlist['tracks'][1]['setVideoId'],
                                                        playlist['tracks'][0]['setVideoId']))
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist edit failed")
        youtube_auth.edit_playlist(playlist['id'],
                                   title=playlist['title'],
                                   description=playlist['description'],
                                   privacyStatus=playlist['privacy'],
                                   moveItem=(playlist['tracks'][0]['setVideoId'],
                                             playlist['tracks'][1]['setVideoId']))
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist edit failed")

    # end to end test adding playlist, adding item, deleting item, deleting playlist
    def test_end2end(self):
        playlistId = youtube_auth.create_playlist(
            "test",
            "test description",
            source_playlist="OLAK5uy_lGQfnMNGvYCRdDq9ZLzJV2BJL2aHQsz9Y")
        self.assertEqual(len(playlistId), 34, "Playlist creation failed")
        response = youtube_auth.add_playlist_items(playlistId, ['y0Hhvtmv0gk'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Adding playlist item failed")
        playlist = youtube_auth.get_playlist(playlistId)
        self.assertEqual(len(playlist['tracks']), 41, "Getting playlist items failed")
        response = youtube_auth.remove_playlist_items(playlistId, playlist['tracks'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist item removal failed")
        response = youtube_auth.delete_playlist(playlistId)
        self.assertEqual(response['command']['handlePlaylistDeletionCommand']['playlistId'],
                         playlistId, "Playlist removal failed")

    ###############
    # UPLOADS
    ###############

    def test_get_library_upload_songs(self):
        results = youtube_auth.get_library_upload_songs(100)
        self.assertGreater(len(results), 25)

    def test_get_library_upload_albums(self):
        results = youtube_auth.get_library_upload_albums(50)
        self.assertGreater(len(results), 25)

    def test_get_library_upload_artists(self):
        results = youtube_auth.get_library_upload_artists(50)
        self.assertGreater(len(results), 25)

    def test_upload_song(self):
        self.assertRaises(Exception, youtube_auth.upload_song, 'song.wav')
        response = youtube_auth.upload_song(config['uploads']['file'])
        self.assertEqual(response.status_code, 409)

    @unittest.skip("Do not delete uploads")
    def test_delete_upload_entity(self):
        results = youtube_auth.get_library_upload_songs()
        response = youtube_auth.delete_upload_entity(results[0]['entityId'])
        self.assertEqual(response, 'STATUS_SUCCEEDED')

    def test_get_library_upload_album(self):
        album = youtube_auth.get_library_upload_album(config['uploads']['private_album_id'])
        self.assertGreater(len(album['tracks']), 0)

    def test_get_library_upload_artist(self):
        tracks = youtube_auth.get_library_upload_artist(config['uploads']['private_artist_id'])
        self.assertGreater(len(tracks), 0)


if __name__ == '__main__':
    unittest.main()
