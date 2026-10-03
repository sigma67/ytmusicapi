from ytmusicapi.models import (
    AlbumRef,
    ArtistRef,
    FeedbackTokens,
    HyperLink,
    LikeStatus,
    PlainText,
    PlaylistRef,
    PrivacyStatus,
    Thumbnail,
    VideoType,
    VoteStatus,
    YTMusicModel,
)
from ytmusicapi.models.content import TextRun
from ytmusicapi.models.uploads import UploadSong


def test_thumbnail_defaults_missing_dimensions_to_none() -> None:
    thumbnail = Thumbnail(url="https://example.test/cover.jpg")

    assert thumbnail == {
        "url": "https://example.test/cover.jpg",
        "width": None,
        "height": None,
    }


def test_named_references_keep_distinct_types() -> None:
    artist = ArtistRef(id="UC123", name="Artist")
    album = AlbumRef(id="MPRE123", name="Album")

    assert isinstance(artist, YTMusicModel)
    assert isinstance(album, YTMusicModel)
    assert artist == {"name": "Artist", "id": "UC123"}
    assert album == {"name": "Album", "id": "MPRE123"}


def test_playlist_reference_matches_menu_playlist_ids() -> None:
    ref = PlaylistRef(shuffleId="RDAO123", radioId="RDEM123")

    assert ref == {"shuffleId": "RDAO123", "radioId": "RDEM123"}
    assert PlaylistRef() == {"shuffleId": None, "radioId": None}


def test_feedback_tokens_allow_unavailable_actions() -> None:
    tokens = FeedbackTokens(add=None, remove="remove-token")

    assert tokens == {"add": None, "remove": "remove-token"}


def test_text_runs_are_models() -> None:
    hyperlink: TextRun = HyperLink(text="Artist", url="https://example.test/artist")
    plain: TextRun = PlainText(text="plain")

    assert isinstance(hyperlink, YTMusicModel)
    assert isinstance(plain, YTMusicModel)
    assert hyperlink == {"text": "Artist", "url": "https://example.test/artist"}
    assert plain == {"text": "plain"}


def test_existing_enums_are_reexported() -> None:
    assert PrivacyStatus.PUBLIC == "PUBLIC"
    assert LikeStatus.LIKE == "LIKE"
    assert VideoType.ATV == "MUSIC_VIDEO_TYPE_ATV"
    assert VoteStatus.UPVOTED == "VOTE_STATUS_UPVOTED"


def test_upload_models_use_shared_leaf_models() -> None:
    song = UploadSong(
        entityId="entity",
        videoId="video",
        artists=[{"id": "UC123", "name": "Artist"}],
        album={"id": "MPRE123", "name": "Album"},
        likeStatus="LIKE",
        thumbnails=[{"url": "https://example.test/cover.jpg"}],
    )

    assert isinstance(song.artists[0], ArtistRef)
    assert isinstance(song.album, AlbumRef)
    assert isinstance(song.thumbnails[0], Thumbnail)
