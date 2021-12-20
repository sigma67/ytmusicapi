import unittest
import unittest.mock
import configparser
import sys
sys.path.insert(0, '..')
from ytmusicapi.ytmusic import YTMusic  # noqa: E402

config = configparser.RawConfigParser()
config.read('./test.cfg', 'utf-8')

sample_album = "MPREb_4pL8gzRtw1p"  # Eminem - Revival
sample_video = "ZrOKjDZOtkA"  # Oasis - Wonderwall (Remastered)
sample_playlist = "PL6bPxvf5dW5clc3y9wAoslzqUrmkZ5c-u"  # very large playlist


class TestYTMusic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.yt = YTMusic(requests_session=False)
        cls.yt_auth = YTMusic(config['auth']['headers_file'])
        cls.yt_brand = YTMusic(config['auth']['headers'], config['auth']['brand_account'])

    def test_init(self):
        self.assertRaises(Exception, YTMusic, "{}")

    def test_setup(self):
        headers = YTMusic.setup(config['auth']['headers_file'], config['auth']['headers_raw'])
        self.assertGreaterEqual(len(headers), 2)
        headers_raw = config['auth']['headers_raw'].split('\n')
        with unittest.mock.patch('builtins.input', side_effect=(headers_raw + [EOFError()])):
            headers = YTMusic.setup(config['auth']['headers_file'])
            self.assertGreaterEqual(len(headers), 2)

    ###############
    # BROWSING
    ###############

    def test_search(self):
        query = "edm playlist"
        self.assertRaises(Exception, self.yt_auth.search, query, filter="song")
        self.assertRaises(Exception, self.yt_auth.search, query, scope="upload")
        results = self.yt.search(query)
        self.assertGreater(len(results), 10)
        results = self.yt_auth.search('Martin Stig Andersen - Deteriation', ignore_spelling=True)
        self.assertGreater(len(results), 0)
        results = self.yt_auth.search(query, filter='songs')
        self.assertGreater(len(results), 10)
        results = self.yt_auth.search(query, filter='videos')
        self.assertGreater(len(results), 10)
        results = self.yt_auth.search(query, filter='albums', limit=40)
        self.assertGreater(len(results), 20)
        results = self.yt_auth.search('project-2', filter='artists', ignore_spelling=True)
        self.assertGreater(len(results), 0)
        results = self.yt_auth.search("classical music", filter='playlists')
        self.assertGreater(len(results), 5)
        results = self.yt_auth.search("clasical music", filter='playlists', ignore_spelling=True)
        self.assertGreater(len(results), 5)
        results = self.yt_auth.search("clasic rock", filter='community_playlists', ignore_spelling=True)
        self.assertGreater(len(results), 5)
        results = self.yt_auth.search("hip hop", filter='featured_playlists')
        self.assertGreater(len(results), 5)

    def test_search_uploads(self):
        results = self.yt_auth.search('audiomachine', scope='uploads', limit=40)
        self.assertGreater(len(results), 20)

    def test_search_library(self):
        results = self.yt_auth.search('garrix', scope='library')
        self.assertGreater(len(results), 5)
        results = self.yt_auth.search('bergersen', filter='songs', scope='library', limit=40)
        self.assertGreater(len(results), 10)
        results = self.yt_auth.search('garrix', filter='albums', scope='library', limit=40)
        self.assertGreaterEqual(len(results), 4)
        results = self.yt_auth.search('garrix', filter='artists', scope='library', limit=40)
        self.assertGreaterEqual(len(results), 1)
        results = self.yt_auth.search('garrix', filter='playlists', scope='library')
        self.assertGreaterEqual(len(results), 1)

    def test_get_artist(self):
        results = self.yt.get_artist("MPLAUCmMUZbaYdNH0bEd1PAlAqsA")
        self.assertEqual(len(results), 14)

        # test correctness of related artists
        related = results['related']['results']
        self.assertEqual(
            len([
                x for x in related
                if set(x.keys()) == {"browseId", "subscribers", "title", "thumbnails"}
            ]), len(related))

        results = self.yt.get_artist("UCLZ7tlKC06ResyDmEStSrOw")  # no album year
        self.assertGreaterEqual(len(results), 11)

    def test_get_artist_for_non_youtube_music_channel(self):
        # all YouTube channel IDs can be looked up in YouTube Music, but the page they return will not necessarily return any music content
        non_music_channel_id = "UCUcpVoi5KkJmnE3bvEhHR0Q"  # e.g. https://music.youtube.com/channel/UCUcpVoi5KkJmnE3bvEhHR0Q
        self.assertRaises(ValueError, self.yt.get_artist, non_music_channel_id)

    def test_get_artist_albums(self):
        artist = self.yt.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = self.yt.get_artist_albums(artist['albums']['browseId'],
                                            artist['albums']['params'])
        self.assertGreater(len(results), 0)

    def test_get_artist_singles(self):
        artist = self.yt_auth.get_artist("UCAeLFBCQS7FvI8PvBrWvSBg")
        results = self.yt_auth.get_artist_albums(artist['singles']['browseId'],
                                                 artist['singles']['params'])
        self.assertGreater(len(results), 0)

    def test_get_user(self):
        results = self.yt.get_user("UC44hbeRoCZVVMVg5z0FfIww")
        self.assertEqual(len(results), 3)

    def test_get_user_playlists(self):
        results = self.yt.get_user("UCPVhZsC2od1xjGhgEc2NEPQ")
        results = self.yt.get_user_playlists("UCPVhZsC2od1xjGhgEc2NEPQ",
                                             results['playlists']['params'])
        self.assertGreater(len(results), 100)

    def test_get_album_browse_id(self):
        browse_id = self.yt.get_album_browse_id("OLAK5uy_nMr9h2VlS-2PULNz3M3XVXQj_P3C2bqaY")
        self.assertEqual(browse_id, sample_album)

    def test_get_album(self):
        results = self.yt_auth.get_album(sample_album)
        self.assertGreaterEqual(len(results), 9)
        self.assertTrue(results['tracks'][0]['isExplicit'])
        self.assertIn('feedbackTokens', results['tracks'][0])
        results = self.yt.get_album("MPREb_BQZvl3BFGay")
        self.assertEqual(len(results['tracks']), 7)

    def test_get_song(self):
        song = self.yt_auth.get_song("AjXQiKP5kMs")  # private upload
        self.assertEqual(len(song), 4)
        song = self.yt.get_song(sample_video)
        self.assertGreaterEqual(len(song['streamingData']['adaptiveFormats']), 10)

    def test_get_lyrics(self):
        playlist = self.yt.get_watch_playlist(sample_video)
        lyrics_song = self.yt.get_lyrics(playlist["lyrics"])
        self.assertIsNotNone(lyrics_song["lyrics"])
        self.assertIsNotNone(lyrics_song["source"])

        playlist = self.yt.get_watch_playlist("9TnpB8WgW4s")
        self.assertIsNone(playlist["lyrics"])
        self.assertRaises(Exception, self.yt.get_lyrics, playlist["lyrics"])

    def test_get_signatureTimestamp(self):
        signatureTimestamp = self.yt.get_signatureTimestamp()
        self.assertIsNotNone(signatureTimestamp)

    ###############
    # EXPLORE
    ###############

    def test_get_mood_playlists(self):
        categories = self.yt.get_mood_categories()
        self.assertGreater(len(list(categories)), 0)
        cat = list(categories)[0]
        self.assertGreater(len(categories[cat]), 0)
        playlists = self.yt.get_mood_playlists(categories[cat][0]["params"])
        self.assertGreater(len(playlists), 0)

    def test_get_charts(self):
        charts = self.yt_auth.get_charts()
        self.assertEqual(len(charts), 4)
        charts = self.yt_auth.get_charts(country='US')
        self.assertEqual(len(charts), 6)
        charts = self.yt.get_charts(country='BE')
        self.assertEqual(len(charts), 4)

    ###############
    # WATCH
    ###############

    def test_get_watch_playlist(self):
        playlist = self.yt_auth.get_watch_playlist(playlistId="OLAK5uy_ln_o1YXFqK4nfiNuTfhJK2XcRNCxml0fY", limit=90)
        self.assertGreaterEqual(len(playlist['tracks']), 90)
        playlist = self.yt_auth.get_watch_playlist("9mWr4c_ig54", limit=50)
        self.assertGreater(len(playlist['tracks']), 45)
        playlist = self.yt_auth.get_watch_playlist("UoAf_y9Ok4k")  # private track
        self.assertGreaterEqual(len(playlist['tracks']), 25)

    def test_get_watch_playlist_shuffle(self):
        playlist = self.yt.get_watch_playlist_shuffle(
            playlistId="OLAK5uy_lKgoGvlrWhX0EIPavQUXxyPed8Cj38AWc")
        self.assertEqual(len(playlist['tracks']), 12)

    def test_get_watch_playlist_shuffle_playlist(self):
        playlist = self.yt_brand.get_watch_playlist_shuffle(playlistId=config['playlists']['own'])
        self.assertEqual(len(playlist['tracks']), 4)

    ###############
    # LIBRARY
    ###############

    def test_get_library_playlists(self):
        playlists = self.yt_auth.get_library_playlists(50)
        self.assertGreater(len(playlists), 25)

    def test_get_library_songs(self):
        songs = self.yt_brand.get_library_songs(100)
        self.assertGreaterEqual(len(songs), 100)
        songs = self.yt_auth.get_library_songs(200, validate_responses=True)
        self.assertGreaterEqual(len(songs), 200)
        songs = self.yt_auth.get_library_songs(order='a_to_z')
        self.assertGreaterEqual(len(songs), 25)
        songs = self.yt_auth.get_library_songs(order='z_to_a')
        self.assertGreaterEqual(len(songs), 25)
        songs = self.yt_auth.get_library_songs(order='recently_added')
        self.assertGreaterEqual(len(songs), 25)

    def test_get_library_albums(self):
        albums = self.yt_auth.get_library_albums(100)
        self.assertGreater(len(albums), 50)
        albums = self.yt_brand.get_library_albums(100, order='a_to_z')
        self.assertGreater(len(albums), 50)
        albums = self.yt_brand.get_library_albums(100, order='z_to_a')
        self.assertGreater(len(albums), 50)
        albums = self.yt_brand.get_library_albums(100, order='recently_added')
        self.assertGreater(len(albums), 50)

    def test_get_library_artists(self):
        artists = self.yt_brand.get_library_artists(50)
        self.assertGreater(len(artists), 40)
        artists = self.yt_brand.get_library_artists(order='a_to_z', limit=50)
        self.assertGreater(len(artists), 40)
        artists = self.yt_brand.get_library_artists(order='z_to_a')
        self.assertGreater(len(artists), 20)
        artists = self.yt_brand.get_library_artists(order='recently_added')
        self.assertGreater(len(artists), 20)

    def test_get_library_subscriptions(self):
        artists = self.yt_brand.get_library_subscriptions(50)
        self.assertGreater(len(artists), 40)
        artists = self.yt_brand.get_library_subscriptions(order='a_to_z')
        self.assertGreater(len(artists), 20)
        artists = self.yt_brand.get_library_subscriptions(order='z_to_a')
        self.assertGreater(len(artists), 20)
        artists = self.yt_brand.get_library_subscriptions(order='recently_added')
        self.assertGreater(len(artists), 20)

    def test_get_liked_songs(self):
        songs = self.yt_brand.get_liked_songs(200)
        self.assertGreater(len(songs['tracks']), 100)

    def test_get_history(self):
        songs = self.yt_auth.get_history()
        self.assertGreater(len(songs), 0)

    @unittest.skip
    def test_remove_history_items(self):
        songs = self.yt_auth.get_history()
        response = self.yt_auth.remove_history_items(
            [songs[0]['feedbackToken'], songs[1]['feedbackToken']])
        self.assertIn('feedbackResponses', response)

    def test_rate_song(self):
        response = self.yt_auth.rate_song(sample_video, 'LIKE')
        self.assertIn('actions', response)
        response = self.yt_auth.rate_song(sample_video, 'INDIFFERENT')
        self.assertIn('actions', response)

    def test_edit_song_library_status(self):
        album = self.yt_brand.get_album(sample_album)
        response = self.yt_brand.edit_song_library_status(
            album['tracks'][2]['feedbackTokens']['add'])
        self.assertTrue(response['feedbackResponses'][0]['isProcessed'])
        response = self.yt_brand.edit_song_library_status(
            album['tracks'][2]['feedbackTokens']['remove'])
        self.assertTrue(response['feedbackResponses'][0]['isProcessed'])

    def test_rate_playlist(self):
        response = self.yt_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4', 'LIKE')
        self.assertIn('actions', response)
        response = self.yt_auth.rate_playlist('OLAK5uy_l3g4WcHZsEx_QuEDZzWEiyFzZl6pL0xZ4',
                                              'INDIFFERENT')
        self.assertIn('actions', response)

    def test_subscribe_artists(self):
        self.yt_auth.subscribe_artists(['UCUDVBtnOQi4c7E8jebpjc9Q', 'UCiMhD4jzUqG-IgPzUmmytRQ'])
        self.yt_auth.unsubscribe_artists(['UCUDVBtnOQi4c7E8jebpjc9Q', 'UCiMhD4jzUqG-IgPzUmmytRQ'])

    ###############
    # PLAYLISTS
    ###############

    def test_get_foreign_playlist(self):
        playlist = self.yt.get_playlist(sample_playlist, 300)
        self.assertGreater(len(playlist['tracks']), 200)

    def test_get_owned_playlist(self):
        playlist = self.yt_brand.get_playlist(config['playlists']['own'])
        self.assertLess(len(playlist['tracks']), 100)
        if not playlist['suggestions_token']:
            self.skipTest("Suggestions not available")
        suggestions = self.yt_brand.get_playlist_suggestions(playlist['suggestions_token'])
        self.assertGreater(len(suggestions['tracks']), 5)
        refresh = self.yt_brand.get_playlist_suggestions(suggestions['refresh_token'])
        self.assertGreater(len(refresh['tracks']), 5)

    def test_edit_playlist(self):
        playlist = self.yt_brand.get_playlist(config['playlists']['own'])
        response = self.yt_brand.edit_playlist(playlist['id'],
                                               title='',
                                               description='',
                                               privacyStatus='PRIVATE',
                                               moveItem=(playlist['tracks'][1]['setVideoId'],
                                                         playlist['tracks'][0]['setVideoId']))
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist edit failed")
        self.yt_brand.edit_playlist(playlist['id'],
                                    title=playlist['title'],
                                    description=playlist['description'],
                                    privacyStatus=playlist['privacy'],
                                    moveItem=(playlist['tracks'][0]['setVideoId'],
                                              playlist['tracks'][1]['setVideoId']))
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist edit failed")

    # end to end test adding playlist, adding item, deleting item, deleting playlist
    def test_end2end(self):
        playlistId = self.yt_auth.create_playlist(
            "test",
            "test description",
            source_playlist="OLAK5uy_lGQfnMNGvYCRdDq9ZLzJV2BJL2aHQsz9Y")
        self.assertEqual(len(playlistId), 34, "Playlist creation failed")
        response = self.yt_auth.add_playlist_items(
            playlistId, ['y0Hhvtmv0gk', sample_video],
            source_playlist='OLAK5uy_nvjTE32aFYdFN7HCyMv3cGqD3wqBb4Jow',
            duplicates=True)
        self.assertEqual(response["status"], 'STATUS_SUCCEEDED', "Adding playlist item failed")
        self.assertGreater(len(response["playlistEditResults"]), 0, "Adding playlist item failed")
        playlist = self.yt_auth.get_playlist(playlistId)
        self.assertEqual(len(playlist['tracks']), 46, "Getting playlist items failed")
        response = self.yt_auth.remove_playlist_items(playlistId, playlist['tracks'])
        self.assertEqual(response, 'STATUS_SUCCEEDED', "Playlist item removal failed")
        response = self.yt_auth.delete_playlist(playlistId)
        self.assertEqual(response['command']['handlePlaylistDeletionCommand']['playlistId'],
                         playlistId, "Playlist removal failed")

    ###############
    # UPLOADS
    ###############

    def test_get_library_upload_songs(self):
        results = self.yt_auth.get_library_upload_songs(50, order='z_to_a')
        self.assertGreater(len(results), 25)

    @unittest.skip("Must not have any uploaded songs to pass")
    def test_get_library_upload_songs_empty(self):
        results = self.yt_auth.get_library_upload_songs(100)
        self.assertEquals(len(results), 0)

    def test_get_library_upload_albums(self):
        results = self.yt_auth.get_library_upload_albums(50, order='a_to_z')
        self.assertGreater(len(results), 40)

    @unittest.skip("Must not have any uploaded albums to pass")
    def test_get_library_upload_albums_empty(self):
        results = self.yt_auth.get_library_upload_albums(100)
        self.assertEquals(len(results), 0)

    def test_get_library_upload_artists(self):
        results = self.yt_auth.get_library_upload_artists(50)
        self.assertGreater(len(results), 25)
        results = self.yt_auth.get_library_upload_artists(50, order='a_to_z')
        self.assertGreater(len(results), 25)
        results = self.yt_auth.get_library_upload_artists(50, order='z_to_a')
        self.assertGreater(len(results), 25)
        results = self.yt_auth.get_library_upload_artists(50, order='recently_added')
        self.assertGreater(len(results), 25)

    @unittest.skip("Must not have any uploaded artsts to pass")
    def test_get_library_upload_artists_empty(self):
        results = self.yt_auth.get_library_upload_artists(100)
        self.assertEquals(len(results), 0)

    def test_upload_song(self):
        self.assertRaises(Exception, self.yt_auth.upload_song, 'song.wav')
        response = self.yt_auth.upload_song(config['uploads']['file'])
        self.assertEqual(response.status_code, 409)

    @unittest.skip("Do not delete uploads")
    def test_delete_upload_entity(self):
        results = self.yt_auth.get_library_upload_songs()
        response = self.yt_auth.delete_upload_entity(results[0]['entityId'])
        self.assertEqual(response, 'STATUS_SUCCEEDED')

    def test_get_library_upload_album(self):
        album = self.yt_auth.get_library_upload_album(config['uploads']['private_album_id'])
        self.assertGreater(len(album['tracks']), 0)

    def test_get_library_upload_artist(self):
        tracks = self.yt_auth.get_library_upload_artist(config['uploads']['private_artist_id'],
                                                        100)
        self.assertGreater(len(tracks), 0)


if __name__ == '__main__':
    unittest.main()
