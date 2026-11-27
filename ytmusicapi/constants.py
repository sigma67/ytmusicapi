YTM_DOMAIN = "https://music.youtube.com"
YTM_BASE_API = YTM_DOMAIN + "/youtubei/v1/"
YTM_PARAMS = "?alt=json"
YTM_PARAMS_KEY = "&key=AIzaSyC9XL3ZjWddXya6X74dJoCTL-WEYFDNX30"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
# fmt: off
SUPPORTED_LANGUAGES = {
    "ar", "cs", "de", "en", "es", "fr", "hi", "it", "ja", "ko", "nl", "pt", "ru", "tr", "ur", "zh_CN",
    "zh_TW"
}
SUPPORTED_LOCATIONS = {
    "AE", "AR", "AT", "AU", "AZ", "BA", "BD", "BE", "BG", "BH", "BO", "BR", "BY", "CA", "CH", "CL",
    "CO", "CR", "CY", "CZ", "DE", "DK", "DO", "DZ", "EC", "EE", "EG", "ES", "FI", "FR", "GB", "GE",
    "GH", "GR", "GT", "HK", "HN", "HR", "HU", "ID", "IE", "IL", "IN", "IQ", "IS", "IT", "JM", "JO",
    "JP", "KE", "KH", "KR", "KW", "KZ", "LA", "LB", "LI", "LK", "LT", "LU", "LV", "LY", "MA", "ME",
    "MK", "MT", "MX", "MY", "NG", "NI", "NL", "NO", "NP", "NZ", "OM", "PA", "PE", "PG", "PH", "PK",
    "PL", "PR", "PT", "PY", "QA", "RO", "RS", "RU", "SA", "SE", "SG", "SI", "SK", "SN", "SV", "TH",
    "TN", "TR", "TW", "TZ", "UA", "UG", "US", "UY", "VE", "VN", "YE", "ZA", "ZW"
}
# fmt: on
OAUTH_SCOPE = "https://www.googleapis.com/auth/youtube"
OAUTH_CODE_URL = "https://www.youtube.com/o/oauth2/device/code"
OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
OAUTH_USER_AGENT = USER_AGENT + " Cobalt/Version"
# OAuth tokens are only accepted by YouTube's TV client, see #813
TV_CLIENT_NAME = "TVHTML5"
TV_CLIENT_VERSION = "7.20250923.13.00"
TV_USER_AGENT = "Mozilla/5.0 (ChromiumStylePlatform) Cobalt/Version"
YT_DATA_API = "https://www.googleapis.com/youtube/v3/"
# functions the TV client has no equivalent for
TV_UNSUPPORTED = [
    "get_home",
    "get_album",
    "get_album_browse_id",
    "get_artist_albums",
    "get_song",
    "get_song_related",
    "get_lyrics",
    "get_basejs_url",
    "get_signatureTimestamp",
    "get_user",
    "get_user_playlists",
    "get_user_videos",
    "get_history",
    "add_history_item",
    "remove_history_items",
    "get_account_info",
    "get_search_suggestions",
    "remove_search_suggestions",
    "get_charts",
    "get_explore",
    "get_mood_categories",
    "get_mood_playlists",
    "get_tasteprofile",
    "set_tasteprofile",
    "get_library_artists",
    "get_library_podcasts",
    "get_library_channels",
    "get_library_upload_songs",
    "get_library_upload_albums",
    "get_library_upload_artists",
    "get_library_upload_artist",
    "get_library_upload_album",
    "edit_song_library_status",
    "get_saved_episodes",
    "get_podcast",
    "get_episode",
    "get_episodes_playlist",
    "get_channel",
    "get_channel_episodes",
]
