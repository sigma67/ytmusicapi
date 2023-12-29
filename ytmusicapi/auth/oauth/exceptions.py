class BadOAuthClient(Exception):
    """
    OAuth client request failure.
    Ensure provided client_id and secret are correct and YouTubeData API is enabled.
    """


class UnauthorizedOAuthClient(Exception):
    """
    OAuth client lacks permissions for specified token.
    Token can only be refreshed by OAuth credentials used for its creation.
    """
