import unittest
import configparser
import sys
sys.path.insert(0, '..')
from ytmusicapi.ytmusic import YTMusic  # noqa: E402

config = configparser.RawConfigParser()
config.read('./test.cfg', 'utf-8')

youtube = YTMusic(requests_session=False)
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
        results = youtube.search(query)
        self.assertGreater(len(results), 10)
        results = youtube_auth.search(query, 'songs')
        self.assertGreater(len(results), 10)
        results = youtube_auth.search(query, 'videos')
        self.assertGreater(len(results), 10)
        results = youtube_auth.search(query, 'albums', limit=40)
        self.assertGreater(len(results), 20)
        results = youtube_auth.search(query, 'artists')
        self.assertGreater(len(results), 0)
        results = youtube_auth.search(query, 'playlists')
        self.assertGreater(len(results), 5)

    def test_search_ignore_spelling(self):
        query = "Martin Stig Andersen - Deteriation"
        results = youtube_auth.search(query, ignore_spelling=True)
        self.assertGreater(len(results), 0)

    def test_search_uploads(self):
        results = youtube_auth.search('audiomachine', 'uploads', limit=40)
        self.assertGreater(len(results), 20)

    def test_get_artist(self):
        results = youtube.get_artist("MPLAUCmMUZbaYdNH0bEd1PAlAqsA")
        self.assertEqual(len(results), 14)

        # test correctness of related artists
        related = results['related']['results']

        self.assertEqual(
            len([
                x for x in related
                if set(x.keys()) == {"browseId", "subscribers", "title", "thumbnails"}
            ]), len(related))

        results = youtube.get_artist("UCLZ7tlKC06ResyDmEStSrOw")  # no album year
        self.assertGreaterEqual(len(results), 11)
        results = youtube.get_artist(
            "UCDAPd3S5CBIEKXn-tvy57Lg")  # no thumbnail, albums, subscribe count
        self.assertGreaterEqual(len(results), 11)

    def test_get_artist_for_non_youtube_music_channel(self):
        # all YouTube channel IDs can be looked up in YouTube Music, but the page they return will not necessarily return any music content
        non_music_channel_id = "UCUcpVoi5KkJmnE3bvEhHR0Q"  # e.g. https://music.youtube.com/channel/UCUcpVoi5KkJmnE3bvEhHR0Q
        self.assertRaises(ValueError, youtube.get_artist, non_music_channel_id)

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
        results = youtube_auth.get_album("MPREb_4pL8gzRtw1p")
        self.assertEqual(len(results), 9)
        self.assertTrue(results['tracks'][0]['isExplicit'])
        self.assertIn('feedbackTokens', results['tracks'][0])
        results = youtube.get_album("MPREb_BQZvl3BFGay")
        self.assertEqual(len(results['tracks']), 7)

    def test_get_song(self):
        song = youtube.get_song("ZrOKjDZOtkA")
        self.assertGreaterEqual(len(song), 16)

    def test_get_streaming_data(self):
        streaming_data = youtube_auth.get_streaming_data("ZrOKjDZOtkA")
        self.assertGreaterEqual(len(streaming_data), 3)

    def test_get_lyrics(self):
        playlist = youtube.get_watch_playlist("ZrOKjDZOtkA")
        lyrics_song = youtube.get_lyrics(playlist["lyrics"])
        self.assertIsNotNone(lyrics_song["lyrics"])
        self.assertIsNotNone(lyrics_song["source"])

        playlist = youtube.get_watch_playlist("9TnpB8WgW4s")
        self.assertIsNone(playlist["lyrics"])
        self.assertRaises(Exception, youtube.get_lyrics, playlist["lyrics"])

    ###############
    # WATCH
    ###############

    def test_get_watch_playlist(self):
        playlist = youtube_auth.get_watch_playlist("9mWr4c_ig54", limit=50)
        self.assertGreater(len(playlist['tracks']), 45)
        playlist = youtube_auth.get_watch_playlist("UoAf_y9Ok4k")  # private track
        self.assertGreaterEqual(len(playlist['tracks']), 25)

    def test_get_watch_playlist_shuffle(self):
        playlist = youtube.get_watch_playlist_shuffle(
            playlistId="OLAK5uy_lKgoGvlrWhX0EIPavQUXxyPed8Cj38AWc")
        self.assertEqual(len(playlist['tracks']), 12)

    def test_get_watch_playlist_shuffle_playlist(self):
        playlist = youtube_auth.get_watch_playlist_shuffle(
            videoId="u6XiiXJD0jg", playlistId="PL528pVfw3ao2VzfY6zE1TOZm1cBSdk7Q0", limit=99)
        self.assertGreaterEqual(len(playlist['tracks']), 80)

    ###############
    # LIBRARY
    ###############

    def test_get_library_playlists(self):
        playlists = youtube_brand.get_library_playlists(50)
        self.assertGreater(len(playlists), 25)

    def test_get_library_songs(self):
        songs = youtube_brand.get_library_songs(100)
        self.assertGreaterEqual(len(songs), 100)
        songs = youtube_auth.get_library_songs(200, validate_responses=True)
        self.assertGreaterEqual(len(songs), 200)
        songs = youtube_auth.get_library_songs(order='a_to_z')
        self.assertGreaterEqual(len(songs), 25)
        songs = youtube_auth.get_library_songs(order='z_to_a')
        self.assertGreaterEqual(len(songs), 25)
        songs = youtube_auth.get_library_songs(order='recently_added')
        self.assertGreaterEqual(len(songs), 25)

    def test_get_library_albums(self):
        albums = youtube_auth.get_library_albums(100)
        self.assertGreater(len(albums), 50)
        albums = youtube_brand.get_library_albums(100, order='a_to_z')
        self.assertGreater(len(albums), 50)
        albums = youtube_brand.get_library_albums(100, order='z_to_a')
        self.assertGreater(len(albums), 50)
        albums = youtube_brand.get_library_albums(100, order='recently_added')
        self.assertGreater(len(albums), 50)

    def test_get_library_artists(self):
        artists = youtube_brand.get_library_artists(50)
        self.assertGreater(len(artists), 40)
        artists = youtube_brand.get_library_artists(order='a_to_z', limit=50)
        self.assertGreater(len(artists), 40)
        artists = youtube_brand.get_library_artists(order='z_to_a')
        self.assertGreater(len(artists), 20)
        artists = youtube_brand.get_library_artists(order='recently_added')
        self.assertGreater(len(artists), 20)

    def test_get_library_subscriptions(self):
        artists = youtube_brand.get_library_subscriptions(50)
        self.assertGreater(len(artists), 40)
        artists = youtube_brand.get_library_subscriptions(order='a_to_z')
        self.assertGreater(len(artists), 20)
        artists = youtube_brand.get_library_subscriptions(order='z_to_a')
        self.assertGreater(len(artists), 20)
        artists = youtube_brand.get_library_subscriptions(order='recently_added')
        self.assertGreater(len(artists), 20)

    def test_get_liked_songs(self):
        songs = youtube_brand.get_liked_songs(200)
        self.assertGreater(len(songs['tracks']), 100)

    def test_get_history(self):
        songs = youtube_auth.get_history()
        self.assertGreater(len(songs), 0)

    @unittest.skip
    def test_remove_history_items(self):
        songs = youtube_auth.get_history()
        response = youtube_auth.remove_history_items(
            [songs[0]['feedbackToken'], songs[1]['feedbackToken']])
        self.assertIn('feedbackResponses', response)

    def test_rate_song(self):
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'LIKE')
        self.assertIn('actions', response)
        response = youtube_auth.rate_song('ZrOKjDZOtkA', 'INDIFFERENT')
        self.assertIn('actions', response)

    def test_edit_song_library_status(self):
        album = youtube_brand.get_album('MPREb_9nqEki4ZDpp')
        response = youtube_brand.edit_song_library_status(
            album['tracks'][2]['feedbackTokens']['add'])
        self.assertTrue(response['feedbackResponses'][0]['isProcessed'])
        response = youtube_brand.edit_song_library_status(
            album['tracks'][2]['feedbackTokens']['remove'])
        self.assertTrue(response['feedbackResponses'][0]['isProcessed'])

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
        response = youtube_auth.add_playlist_items(
            playlistId, ['y0Hhvtmv0gk', 'y0Hhvtmv0gk'],
            source_playlist='OLAK5uy_nvjTE32aFYdFN7HCyMv3cGqD3wqBb4Jow',
            duplicates=True)
        self.assertEqual(response["status"], 'STATUS_SUCCEEDED', "Adding playlist item failed")
        self.assertGreater(len(response["playlistEditResults"]), 0, "Adding playlist item failed")
        playlist = youtube_auth.get_playlist(playlistId)
        self.assertEqual(len(playlist['tracks']), 46, "Getting playlist items failed")
        response = youtube_auth.remove_playlist_items(playlistId, playlist['tracks'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist item removal failed")
        response = youtube_auth.delete_playlist(playlistId)
        self.assertEqual(response['command']['handlePlaylistDeletionCommand']['playlistId'],
                         playlistId, "Playlist removal failed")

    ###############
    # UPLOADS
    ###############

    def test_get_library_upload_songs(self):
        results = youtube_auth.get_library_upload_songs(50)
        self.assertGreater(len(results), 25)

    @unittest.skip("Must not have any uploaded songs to pass")
    def test_get_library_upload_songs_empty(self):
        results = youtube_auth.get_library_upload_songs(100)
        self.assertEquals(len(results), 0)

    def test_get_library_upload_albums(self):
        results = youtube_auth.get_library_upload_albums(50)
        self.assertGreater(len(results), 40)

    @unittest.skip("Must not have any uploaded albums to pass")
    def test_get_library_upload_albums_empty(self):
        results = youtube_auth.get_library_upload_albums(100)
        self.assertEquals(len(results), 0)

    def test_get_library_upload_artists(self):
        results = youtube_auth.get_library_upload_artists(50)
        self.assertGreater(len(results), 25)
        results = youtube_auth.get_library_upload_artists(50, order='a_to_z')
        self.assertGreater(len(results), 25)
        results = youtube_auth.get_library_upload_artists(50, order='z_to_a')
        self.assertGreater(len(results), 25)
        results = youtube_auth.get_library_upload_artists(50, order='recently_added')
        self.assertGreater(len(results), 25)

    @unittest.skip("Must not have any uploaded artsts to pass")
    def test_get_library_upload_artists_empty(self):
        results = youtube_auth.get_library_upload_artists(100)
        self.assertEquals(len(results), 0)

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
        tracks = youtube_auth.get_library_upload_artist(config['uploads']['private_artist_id'],
                                                        100)
        self.assertGreater(len(tracks), 0)


if __name__ == '__main__':
    unittest.main()
