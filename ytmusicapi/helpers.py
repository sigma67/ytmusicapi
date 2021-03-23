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


def validate_order_parameter(order):
    orders = ['a_to_z', 'z_to_a', 'recently_added']
    if order and order not in orders:
        raise Exception(
            "Invalid order provided. Please use one of the following orders or leave out the parameter: "
            + ', '.join(orders))


def prepare_order_params(order):
    orders = ['a_to_z', 'z_to_a', 'recently_added']
    if order is not None:
        # determine order_params via `.contents.singleColumnBrowseResultsRenderer.tabs[0].tabRenderer.content.sectionListRenderer.contents[1].itemSectionRenderer.header.itemSectionTabbedHeaderRenderer.endItems[1].dropdownRenderer.entries[].dropdownItemRenderer.onSelectCommand.browseEndpoint.params` of `/youtubei/v1/browse` response
        order_params = ['ggMGKgQIARAA', 'ggMGKgQIARAB', 'ggMGKgQIABAB']
        return order_params[orders.index(order)]


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
    number_string = string.split(' ')[0]
    try:
        int_value = locale.atoi(number_string)
    except ValueError:
        number_string = number_string.replace(',', '')
        int_value = int(number_string)
    return int_value


def i18n(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        method.__globals__['_'] = self.lang.gettext
        return method(self, *method_args, **method_kwargs)

    return _impl
