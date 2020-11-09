import re
from http.cookies import SimpleCookie
from hashlib import sha1
import time
from functools import wraps
import locale


def prepare_browse_endpoint(type, browseId):
    return {
        'browseEndpointContextSupportedConfigs': {
            "browseEndpointContextMusicConfig": {
                "pageType": "MUSIC_PAGE_TYPE_" + type
            }
        },
        'browseId': browseId
    }


def prepare_like_endpoint(rating):
    if rating == 'LIKE':
        return 'like/like'
    elif rating == 'DISLIKE':
        return 'like/dislike'
    elif rating == 'INDIFFERENT':
        return 'like/removelike'
    else:
        return None


def html_to_txt(html_text):
    tags = re.findall("<[^>]+>", html_text)
    for tag in tags:
        html_text = html_text.replace(tag, '')
    return html_text


def sapisid_from_cookie(raw_cookie):
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    return cookie['__Secure-3PAPISID'].value


# SAPISID Hash reverse engineered by
# https://stackoverflow.com/a/32065323/5726546
def get_authorization(auth):
    sha_1 = sha1()
    unix_timestamp = str(int(time.time()))
    sha_1.update((unix_timestamp + ' ' + auth).encode('utf-8'))
    return "SAPISIDHASH " + unix_timestamp + "_" + sha_1.hexdigest()


def to_int(string):
    number = string.split(' ')[0]
    return locale.atoi(number)


def i18n(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        method.__globals__['_'] = self.lang.gettext
        return method(self, *method_args, **method_kwargs)

    return _impl
