import itertools
from contextlib import suppress
from pathlib import Path

from conftest import get_config

from ytmusicapi import YTMusic

config = get_config()

# To get started, go to https://www.youtube.com/account and create a new channel (=brand account)
brand_account = "114511851949139689139"

# run ytmusicapi browser in tests/setup, paste headers from your test account
yt_brand = YTMusic(Path(__file__).parent.joinpath("oauth.json").as_posix(), brand_account)


def populate_music():
    """idempotent requests to populate an account"""
    # library
    playlist_id = "RDCLAK5uy_l9ex2d91-Qb1i-W7d0MLCEl_ZjRXss0Dk"  # fixed playlist with many artists
    yt_playlist = yt_brand.get_playlist(playlist_id)
    artists = [track["artists"] for track in yt_playlist["tracks"]]
    unique_artists = list(set(artist["id"] for artist in itertools.chain.from_iterable(artists)))
    with suppress(Exception):
        for artist in unique_artists:
            print(f"Adding artist {artist}")
            yt_brand.subscribe_artists([artist])  # add one by one to avoid "requested entity not found"

    # add some albums, which also populates songs and artists as a side effect
    unique_albums = set(track["album"]["id"] for track in yt_playlist["tracks"])
    albums = [yt_brand.get_album(album) for album in unique_albums if album]
    playlist_ids = [album["audioPlaylistId"] for album in albums]
    for playlist_id in playlist_ids:
        print(f"Adding album {playlist_id}")
        yt_brand.rate_playlist(playlist_id, "LIKE")

    # like some songs
    videoIds = list(
        set(
            track["videoId"] for track in itertools.chain.from_iterable([album["tracks"] for album in albums])
        )
    )
    for videoId in videoIds[:200]:
        print(f"Liking track {videoId}")
        yt_brand.rate_song(videoId, "LIKE")

    # create own playlist
    playlistId = yt_brand.create_playlist(
        title="ytmusicapi test playlist don't delete",
        description="description",
        source_playlist="PLJZsotfVeN2D3pHlgWT_FFSYsJe_thVmh",
    )
    print(f"Created playlist {playlistId}, don't forget to set this in test.cfg playlists/own")


def populate_podcasts():
    yt_brand.rate_playlist(config["podcasts"]["podcast_id"], rating="LIKE")
    yt_brand.add_playlist_items("SE", [config["podcasts"]["episode_id"]])
    podcasts = yt_brand.search("podcast", filter="podcasts", limit=40)
    for podcast in podcasts:
        playlist_id = podcast["browseId"][4:]
        yt_brand.rate_playlist(playlist_id, rating="LIKE")
        podcast = yt_brand.get_podcast(playlist_id)
        yt_brand.subscribe_artists([podcast["author"]["id"]])


if __name__ == "__main__":
    populate_music()
    populate_podcasts()
