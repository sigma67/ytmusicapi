import json
import locale
import re
import time
import unicodedata
from hashlib import sha1
from http.cookies import SimpleCookie

from ytmusicapi.constants import *


def initialize_headers():
    return {
        "user-agent": USER_AGENT,
        "accept": "*/*",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
        "content-encoding": "gzip",
        "origin": YTM_DOMAIN,
    }


def initialize_context():
    return {
        "context": {
            "client": {
                "clientName": "WEB_REMIX",
                "clientVersion": "1." + time.strftime("%Y%m%d", time.gmtime()) + ".01.00",
            },
            "user": {},
        }
    }


def get_visitor_id(request_func):
    response = request_func(YTM_DOMAIN)
    matches = re.findall(r"ytcfg\.set\s*\(\s*({.+?})\s*\)\s*;", response.text)
    visitor_id = ""
    if len(matches) > 0:
        ytcfg = json.loads(matches[0])
        visitor_id = ytcfg.get("VISITOR_DATA")
    return {"X-Goog-Visitor-Id": visitor_id}


def sapisid_from_cookie(raw_cookie):
    cookie = SimpleCookie()
    cookie.load(raw_cookie.replace('"', ""))
    return cookie["__Secure-3PAPISID"].value


# SAPISID Hash reverse engineered by
# https://stackoverflow.com/a/32065323/5726546
def get_authorization(auth):
    sha_1 = sha1()
    unix_timestamp = str(int(time.time()))
    sha_1.update((unix_timestamp + " " + auth).encode("utf-8"))
    return "SAPISIDHASH " + unix_timestamp + "_" + sha_1.hexdigest()


def to_int(string):
    string = unicodedata.normalize("NFKD", string)
    number_string = re.sub(r"\D", "", string)
    try:
        int_value = locale.atoi(number_string)
    except ValueError:
        number_string = number_string.replace(",", "")
        int_value = int(number_string)
    return int_value


def sum_total_duration(item):
    if "tracks" not in item:
        return 0
    return sum([track["duration_seconds"] if "duration_seconds" in track else 0 for track in item["tracks"]])
