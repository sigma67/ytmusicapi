from ytmusicapi import YTMusic
import time
from threading import Thread

ytmusic = YTMusic()
ytmusic_auth = YTMusic("oauth.json")


class Endpoints:

    def __init__(self, ytmusic):
        self.ytmusic = ytmusic

        self.endpoints_search = [(ytmusic.search, {
            "query": "Oasis Wonderwall"
        }), (ytmusic.get_search_suggestions, {
            "query": "faded"
        })]

        self.endpoints_browse = [
            (ytmusic.get_home, {}),
            (ytmusic.get_artist, {
                "channelId": "UCUDVBtnOQi4c7E8jebpjc9Q"
            }),
            (ytmusic.get_artist_albums, {
                "channelId":
                "UCUDVBtnOQi4c7E8jebpjc9Q",
                "params":
                "6gPgAUdxVUJXcFlCQ3BNQkNpUjVkRjl3WVdkbFgzTnVZWEJ6YUc5MFgyMTFjMmxqWDNCaFoyVmZjbVZuYVc5dVlXd1NIMWw2TWxSU1JXcG1VbkIzV2pCSVNUTmhYMEpDVEdaYWRYVmtRVkZwZUdjYVNnQUFaVzRBQVZWVEFBRlZVd0FCQUVaRmJYVnphV05mWkdWMFlXbHNYMkZ5ZEdsemRBQUJBVU1BQUFFQUFBRUJBRlZEVlVSV1FuUnVUMUZwTkdNM1JUaHFaV0p3YW1NNVVRQUI4dHF6cWdvR1FBRklBRkFT"
            }),
            (ytmusic.get_album, {
                "browseId": "MPREb_6uHkr4FTpt8"
            }),
            (ytmusic.get_album_browse_id, {
                "audioPlaylistId": "OLAK5uy_mgMw8a_badAdsaMtKyNkWQ4-qqGO8bjyM"
            }),
            (ytmusic.get_user, {
                "channelId": "UCS4-R22Nn-0j_-OZCYdxsvQ"
            }),
            (ytmusic.get_user_playlists, {
                "channelId":
                "UCS4-R22Nn-0j_-OZCYdxsvQ",
                "params":
                "6gPgAUdxVUJXcFlCQ3BNQkNpUjVkRjl3WVdkbFgzTnVZWEJ6YUc5MFgyMTFjMmxqWDNCaFoyVmZjbVZuYVc5dVlXd1NIMWw2TWxSU1JXcG1VbkIzV2pCSVNUTmhYMEpDVEdaaWRYSkRUVkpwZUdjYVNnQUFaVzRBQVZWVEFBRlZVd0FCQUVaRmJYVnphV05mWkdWMFlXbHNYMkZ5ZEdsemRBQUJBVU1BQUFFQUFBRUJBRlZEVXpRdFVqSXlUbTR0TUdwZkxVOWFRMWxrZUhOMlVRQUI4dHF6cWdvR1FBRklBRkFV"
            }),
            (ytmusic.get_song, {
                "videoId": "pleeYqFVR4E"
            }),
            (ytmusic.get_song_related, {
                "browseId": "MPREb_WNGQWp5czjD"
            }),
            (ytmusic.get_lyrics, {
                "browseId": "MPREb_WNGQWp5czjD"
            }),
            (ytmusic.get_tasteprofile, {}),
            (ytmusic.set_tasteprofile, {
                "artists": ["Leo Dan"],
                "taste_profile": {
                    "Drake": {
                        "selectionValue": "tastebuilder_selection=/m/05mt_q",
                        "impressionValue": "tastebuilder_impression=/m/05mt_q"
                    },
                    "Lil Baby": {
                        "selectionValue": "tastebuilder_selection=/g/11gglqnpms",
                        "impressionValue": "tastebuilder_impression=/g/11gglqnpms"
                    },
                    "Future": {
                        "selectionValue": "tastebuilder_selection=/m/0hhwdgn",
                        "impressionValue": "tastebuilder_impression=/m/0hhwdgn"
                    },
                    "Lil Wayne": {
                        "selectionValue": "tastebuilder_selection=/m/016kjs",
                        "impressionValue": "tastebuilder_impression=/m/016kjs"
                    },
                    "Kevin Gates": {
                        "selectionValue": "tastebuilder_selection=/m/0dy5g5q",
                        "impressionValue": "tastebuilder_impression=/m/0dy5g5q"
                    },
                    "21 Savage": {
                        "selectionValue": "tastebuilder_selection=/g/11cn3ch719",
                        "impressionValue": "tastebuilder_impression=/g/11cn3ch719"
                    },
                    "Moneybagg Yo": {
                        "selectionValue": "tastebuilder_selection=/g/11f08lll0b",
                        "impressionValue": "tastebuilder_impression=/g/11f08lll0b"
                    },
                    "Young Thug": {
                        "selectionValue": "tastebuilder_selection=/g/11jpzjw5yz",
                        "impressionValue": "tastebuilder_impression=/g/11jpzjw5yz"
                    },
                    "Gucci Mane": {
                        "selectionValue": "tastebuilder_selection=/m/078wwr",
                        "impressionValue": "tastebuilder_impression=/m/078wwr"
                    },
                    "DaBaby": {
                        "selectionValue": "tastebuilder_selection=/g/11fkcb0cxl",
                        "impressionValue": "tastebuilder_impression=/g/11fkcb0cxl"
                    },
                    "Boosie Badazz": {
                        "selectionValue": "tastebuilder_selection=/m/01s36sp",
                        "impressionValue": "tastebuilder_impression=/m/01s36sp"
                    },
                    "T.I.": {
                        "selectionValue": "tastebuilder_selection=/m/03f7lp0",
                        "impressionValue": "tastebuilder_impression=/m/03f7lp0"
                    },
                    "T-Pain": {
                        "selectionValue": "tastebuilder_selection=/m/0837ql",
                        "impressionValue": "tastebuilder_impression=/m/0837ql"
                    },
                    "Quavo": {
                        "selectionValue": "tastebuilder_selection=/m/0zg_3ns",
                        "impressionValue": "tastebuilder_impression=/m/0zg_3ns"
                    },
                    "Yo Gotti": {
                        "selectionValue": "tastebuilder_selection=/m/01wgdfz",
                        "impressionValue": "tastebuilder_impression=/m/01wgdfz"
                    },
                    "Meek Mill": {
                        "selectionValue": "tastebuilder_selection=/m/0gkzp28",
                        "impressionValue": "tastebuilder_impression=/m/0gkzp28"
                    },
                    "Ludacris": {
                        "selectionValue": "tastebuilder_selection=/m/01vw37m",
                        "impressionValue": "tastebuilder_impression=/m/01vw37m"
                    },
                    "Lil Jon": {
                        "selectionValue": "tastebuilder_selection=/m/01vw_dv",
                        "impressionValue": "tastebuilder_impression=/m/01vw_dv"
                    },
                    "GloRilla": {
                        "selectionValue": "tastebuilder_selection=/g/11h04mj4p4",
                        "impressionValue": "tastebuilder_impression=/g/11h04mj4p4"
                    },
                    "YG": {
                        "selectionValue": "tastebuilder_selection=/m/0g9_hlg",
                        "impressionValue": "tastebuilder_impression=/m/0g9_hlg"
                    },
                    "G-Eazy": {
                        "selectionValue": "tastebuilder_selection=/m/0hr594p",
                        "impressionValue": "tastebuilder_impression=/m/0hr594p"
                    },
                    "Tyga": {
                        "selectionValue": "tastebuilder_selection=/m/0414qmv",
                        "impressionValue": "tastebuilder_impression=/m/0414qmv"
                    },
                    "Joyner Lucas": {
                        "selectionValue": "tastebuilder_selection=/g/11d_8tdmhj",
                        "impressionValue": "tastebuilder_impression=/g/11d_8tdmhj"
                    },
                    "Big Sean": {
                        "selectionValue": "tastebuilder_selection=/m/03f771p",
                        "impressionValue": "tastebuilder_impression=/m/03f771p"
                    },
                    "Trey Songz": {
                        "selectionValue": "tastebuilder_selection=/m/074vr1",
                        "impressionValue": "tastebuilder_impression=/m/074vr1"
                    },
                    "Takeoff": {
                        "selectionValue": "tastebuilder_selection=/m/0zjjy3n",
                        "impressionValue": "tastebuilder_impression=/m/0zjjy3n"
                    },
                    "Webbie": {
                        "selectionValue": "tastebuilder_selection=/m/01rz_gh",
                        "impressionValue": "tastebuilder_impression=/m/01rz_gh"
                    },
                    "K Camp": {
                        "selectionValue": "tastebuilder_selection=/m/0wtgr1j",
                        "impressionValue": "tastebuilder_impression=/m/0wtgr1j"
                    },
                    "Rae Sremmurd": {
                        "selectionValue": "tastebuilder_selection=/m/0115czh1",
                        "impressionValue": "tastebuilder_impression=/m/0115czh1"
                    },
                    "B.o.B": {
                        "selectionValue": "tastebuilder_selection=/m/047ts85",
                        "impressionValue": "tastebuilder_impression=/m/047ts85"
                    },
                    "UGK": {
                        "selectionValue": "tastebuilder_selection=/m/01sbhnj",
                        "impressionValue": "tastebuilder_impression=/m/01sbhnj"
                    },
                    "Rich the Kid": {
                        "selectionValue": "tastebuilder_selection=/m/0127fsy9",
                        "impressionValue": "tastebuilder_impression=/m/0127fsy9"
                    },
                    "Waka Flocka Flame": {
                        "selectionValue": "tastebuilder_selection=/m/09gnjnz",
                        "impressionValue": "tastebuilder_impression=/m/09gnjnz"
                    },
                    "Hitkidd": {
                        "selectionValue": "tastebuilder_selection=/g/11g0gmysm5",
                        "impressionValue": "tastebuilder_impression=/g/11g0gmysm5"
                    },
                    "Ying Yang Twins": {
                        "selectionValue": "tastebuilder_selection=/m/01mtrhv",
                        "impressionValue": "tastebuilder_impression=/m/01mtrhv"
                    },
                    "Larry June": {
                        "selectionValue": "tastebuilder_selection=/g/11c5wml3rt",
                        "impressionValue": "tastebuilder_impression=/g/11c5wml3rt"
                    },
                    "Master P": {
                        "selectionValue": "tastebuilder_selection=/m/016ksk",
                        "impressionValue": "tastebuilder_impression=/m/016ksk"
                    },
                    "Mystikal": {
                        "selectionValue": "tastebuilder_selection=/m/018n7d",
                        "impressionValue": "tastebuilder_impression=/m/018n7d"
                    },
                    "Mike WiLL Made-It": {
                        "selectionValue": "tastebuilder_selection=/m/0n4brdy",
                        "impressionValue": "tastebuilder_impression=/m/0n4brdy"
                    },
                    "Cam'ron": {
                        "selectionValue": "tastebuilder_selection=/m/03f17nl",
                        "impressionValue": "tastebuilder_impression=/m/03f17nl"
                    },
                    "Bobby Shmurda": {
                        "selectionValue": "tastebuilder_selection=/m/0114dc4f",
                        "impressionValue": "tastebuilder_impression=/m/0114dc4f"
                    },
                    "Ace Hood": {
                        "selectionValue": "tastebuilder_selection=/m/049f6kl",
                        "impressionValue": "tastebuilder_impression=/m/049f6kl"
                    },
                    "Montana of 300": {
                        "selectionValue": "tastebuilder_selection=/m/012xgkrf",
                        "impressionValue": "tastebuilder_impression=/m/012xgkrf"
                    },
                    "Quality Control": {
                        "selectionValue": "tastebuilder_selection=/g/11bt_5hj7r",
                        "impressionValue": "tastebuilder_impression=/g/11bt_5hj7r"
                    },
                    "Bow Wow": {
                        "selectionValue": "tastebuilder_selection=/m/01wbsdz",
                        "impressionValue": "tastebuilder_impression=/m/01wbsdz"
                    },
                    "Dreezy": {
                        "selectionValue": "tastebuilder_selection=/g/11c580ywn_",
                        "impressionValue": "tastebuilder_impression=/g/11c580ywn_"
                    },
                    "Fat Pat": {
                        "selectionValue": "tastebuilder_selection=/m/01qbbj0",
                        "impressionValue": "tastebuilder_impression=/m/01qbbj0"
                    },
                    "Rowdy Rebel": {
                        "selectionValue": "tastebuilder_selection=/m/0121_ny5",
                        "impressionValue": "tastebuilder_impression=/m/0121_ny5"
                    },
                    "Gorilla Zoe": {
                        "selectionValue": "tastebuilder_selection=/m/03j01xr",
                        "impressionValue": "tastebuilder_impression=/m/03j01xr"
                    },
                    "BlocBoy JB": {
                        "selectionValue": "tastebuilder_selection=/g/11hcj0v_jy",
                        "impressionValue": "tastebuilder_impression=/g/11hcj0v_jy"
                    },
                    "King Combs": {
                        "selectionValue": "tastebuilder_selection=/m/04g5fcb",
                        "impressionValue": "tastebuilder_impression=/m/04g5fcb"
                    },
                    "Premo Rice": {
                        "selectionValue": "tastebuilder_selection=/g/11cjm49yjl",
                        "impressionValue": "tastebuilder_impression=/g/11cjm49yjl"
                    },
                    "Grupo Firme": {
                        "selectionValue": "tastebuilder_selection=/g/11nxd610l7",
                        "impressionValue": "tastebuilder_impression=/g/11nxd610l7"
                    },
                    "Carin Leon": {
                        "selectionValue": "tastebuilder_selection=/g/11f5d4v2p1",
                        "impressionValue": "tastebuilder_impression=/g/11f5d4v2p1"
                    },
                    "Vicente Fern\u00e1ndez": {
                        "selectionValue": "tastebuilder_selection=/m/067swc",
                        "impressionValue": "tastebuilder_impression=/m/067swc"
                    },
                    "Christian Nodal": {
                        "selectionValue": "tastebuilder_selection=/g/11fx8hgh71",
                        "impressionValue": "tastebuilder_impression=/g/11fx8hgh71"
                    },
                    "Marco Antonio Sol\u00eds": {
                        "selectionValue": "tastebuilder_selection=/m/01lzr4j",
                        "impressionValue": "tastebuilder_impression=/m/01lzr4j"
                    },
                    "Juan Gabriel": {
                        "selectionValue": "tastebuilder_selection=/m/01ztqk",
                        "impressionValue": "tastebuilder_impression=/m/01ztqk"
                    },
                    "Luis Angel \"El Flaco\"": {
                        "selectionValue": "tastebuilder_selection=/g/11j2j0nmt3",
                        "impressionValue": "tastebuilder_impression=/g/11j2j0nmt3"
                    },
                    "Selena": {
                        "selectionValue": "tastebuilder_selection=/m/01l72d6",
                        "impressionValue": "tastebuilder_impression=/m/01l72d6"
                    },
                    "Julion Alvarez y Su Norte\u00f1o Banda": {
                        "selectionValue": "tastebuilder_selection=/g/1q6lb1lnm",
                        "impressionValue": "tastebuilder_impression=/g/1q6lb1lnm"
                    },
                    "Luis Antonio L\u00f3pez \"El Mimoso\"": {
                        "selectionValue": "tastebuilder_selection=/m/0pkz3v8",
                        "impressionValue": "tastebuilder_impression=/m/0pkz3v8"
                    },
                    "Intocable": {
                        "selectionValue": "tastebuilder_selection=/m/070v4h",
                        "impressionValue": "tastebuilder_impression=/m/070v4h"
                    },
                    "Ana Gabriel": {
                        "selectionValue": "tastebuilder_selection=/m/03xdn9",
                        "impressionValue": "tastebuilder_impression=/m/03xdn9"
                    },
                    "Pancho Barraza": {
                        "selectionValue": "tastebuilder_selection=/m/03f7n2l",
                        "impressionValue": "tastebuilder_impression=/m/03f7n2l"
                    },
                    "\u00c1ngela Aguilar": {
                        "selectionValue": "tastebuilder_selection=/g/11f8p2yv1b",
                        "impressionValue": "tastebuilder_impression=/g/11f8p2yv1b"
                    },
                    "Valent\u00edn Elizalde": {
                        "selectionValue": "tastebuilder_selection=/m/01rrjyv",
                        "impressionValue": "tastebuilder_impression=/m/01rrjyv"
                    },
                    "Leo Dan": {
                        "selectionValue": "tastebuilder_selection=/m/01mvc66",
                        "impressionValue": "tastebuilder_impression=/m/01mvc66"
                    },
                    "Pesado": {
                        "selectionValue": "tastebuilder_selection=/m/01m6w81",
                        "impressionValue": "tastebuilder_impression=/m/01m6w81"
                    },
                    "Edwin Luna ": {
                        "selectionValue": "tastebuilder_selection=/g/11cnkfxr93",
                        "impressionValue": "tastebuilder_impression=/g/11cnkfxr93"
                    },
                    "Sergio Vega": {
                        "selectionValue": "tastebuilder_selection=/m/04gmh_3",
                        "impressionValue": "tastebuilder_impression=/m/04gmh_3"
                    },
                    "Los 2 de la S": {
                        "selectionValue": "tastebuilder_selection=/g/11g22y_6xv",
                        "impressionValue": "tastebuilder_impression=/g/11g22y_6xv"
                    },
                    "La Factoria": {
                        "selectionValue": "tastebuilder_selection=/m/0417xfq",
                        "impressionValue": "tastebuilder_impression=/m/0417xfq"
                    },
                    "Chiquis": {
                        "selectionValue": "tastebuilder_selection=/m/0n9m1_4",
                        "impressionValue": "tastebuilder_impression=/m/0n9m1_4"
                    },
                    "Charlie Adam": {
                        "selectionValue": "tastebuilder_selection=/g/11tjhrqy82",
                        "impressionValue": "tastebuilder_impression=/g/11tjhrqy82"
                    },
                    "Peder B. Helland": {
                        "selectionValue": "tastebuilder_selection=/g/11b7_v75hv",
                        "impressionValue": "tastebuilder_impression=/g/11b7_v75hv"
                    },
                    "Alan Olav Walker": {
                        "selectionValue": "tastebuilder_selection=/g/11tk1_gjrp",
                        "impressionValue": "tastebuilder_impression=/g/11tk1_gjrp"
                    },
                    "Joseph Dave Gomez": {
                        "selectionValue": "tastebuilder_selection=/g/11sbwq7sn_",
                        "impressionValue": "tastebuilder_impression=/g/11sbwq7sn_"
                    },
                    "Giani Wlazly Toe": {
                        "selectionValue": "tastebuilder_selection=/g/11scjnl3h1",
                        "impressionValue": "tastebuilder_impression=/g/11scjnl3h1"
                    },
                    "relaxdaily": {
                        "selectionValue": "tastebuilder_selection=/g/11b7_s6hr6",
                        "impressionValue": "tastebuilder_impression=/g/11b7_s6hr6"
                    },
                    "Deuter": {
                        "selectionValue": "tastebuilder_selection=/m/01mbw4p",
                        "impressionValue": "tastebuilder_impression=/m/01mbw4p"
                    }
                }
            }),
        ]

        self.endpoints_explore = [
            (ytmusic.get_mood_categories, {}),
            (ytmusic.get_mood_playlists, {
                "params": "ggMPOg1uX2lRZUZiMnNrQnJW"
            }),
            (ytmusic.get_charts, {
                "country": "US"
            }),
        ]

        self.endpoints_watch = [(ytmusic.get_watch_playlist, {"videoId": "9mWr4c_ig54"})]

        self.endpoints_library = [
            (ytmusic.get_library_playlists, {}), (ytmusic.get_library_songs, {}),
            (ytmusic.get_library_albums, {}), (ytmusic.get_library_artists, {}),
            (ytmusic.get_library_subscriptions, {}), (ytmusic.get_liked_songs, {}),
            (ytmusic.get_history, {}), (ytmusic.rate_song, {
                "videoId": "9mWr4c_ig54"
            }),
            (ytmusic.edit_song_library_status, {
                "feedbackTokens": [
                    "AB9zfpJjt2-TFC3_CCiXs8QOmTl2vx09tyf5BoFTt5h4-Mi3VKI4694pn2fIoTX-IiZ-KvoTJ9WWAKR1hnQ1VyWl7-g1HJucrQ"
                ]
            }), (ytmusic.rate_playlist, {
                "playlistId": "RDAMVM9mWr4c_ig54"
            }), (ytmusic.subscribe_artists, {
                "channelIds": ["UC2Eotb0QaPkaJI4Cw4oHZ6Q"]
            }), (ytmusic.unsubscribe_artists, {
                "channelIds": ["UC2Eotb0QaPkaJI4Cw4oHZ6Q"]
            })
        ]

        self.endpoints_playlists = [(ytmusic.get_playlist, {
            "playlistId": "RDCLAK5uy_mbdO3_xdD4NtU1rWI0OmvRSRZ8NH4uJCM"
        })]

    def _get_quota(self, endpoint, quotas, index):
        quota = 0
        print(f"Testing endpoint data for {endpoint[0].__name__}")
        start_time = time.time()
        while time.time() - start_time <= 3600:
            response = None
            try:
                response = endpoint[0](**endpoint[1])
                if endpoint[0].__name__ == "set_tasteprofile":
                    if response is None:
                        quota += 1
                    else:
                        break
                elif response is None:
                    break
                else:
                    quota += 1

            except Exception as e:
                print(f"Error occured for {endpoint[0].__name__}")
                print(e)
                break

            time.sleep(0.15)

        quotas[index] = quota

    def _print_quotas(self, endpoints, quotas, name):
        print(f"Final quotas for {name} endpoints")
        for endpoint, quota in zip(endpoints, quotas):
            print(f"{endpoint[0].__name__} endpoint has an API quota of {quota}")

    def quota_search(self):
        quotas = [0] * len(self.endpoints_search)
        threads = [None] * len(self.endpoints_search)
        for i, endpoint in enumerate(self.endpoints_search):
            threads[i] = Thread(target=self._get_quota, args=(endpoint, quotas, i))
            threads[i].start()
            time.sleep(3)

        for thread in threads:
            thread.join()

        self._print_quotas(self.endpoints_search, quotas, "search")

    def quota_browse(self):
        quotas = [0] * len(self.endpoints_browse)
        threads = [None] * len(self.endpoints_browse)
        for i, endpoint in enumerate(self.endpoints_browse):
            threads[i] = Thread(target=self._get_quota, args=(endpoint, quotas, i))
            threads[i].start()
            time.sleep(3)

        for thread in threads:
            thread.join()

        self._print_quotas(self.endpoints_browse, quotas, "browse")

    def quota_explore(self):
        quotas = [0] * len(self.endpoints_explore)
        threads = [None] * len(self.endpoints_explore)
        for i, endpoint in enumerate(self.endpoints_explore):
            threads[i] = Thread(target=self._get_quota, args=(endpoint, quotas, i))
            threads[i].start()
            time.sleep(3)

        for thread in threads:
            thread.join()

        self._print_quotas(self.endpoints_explore, quotas, "explore")

    def quota_watch(self):
        quotas = [0] * len(self.endpoints_watch)
        threads = [None] * len(self.endpoints_watch)
        for i, endpoint in enumerate(self.endpoints_watch):
            threads[i] = Thread(target=self._get_quota, args=(endpoint, quotas, i))
            threads[i].start()
            time.sleep(3)

        for thread in threads:
            thread.join()

        self._print_quotas(self.endpoints_watch, quotas, "watch")

    def quota_library(self):
        quotas = [0] * len(self.endpoints_library)
        threads = [None] * len(self.endpoints_library)
        for i, endpoint in enumerate(self.endpoints_library):
            threads[i] = Thread(target=self._get_quota, args=(endpoint, quotas, i))
            threads[i].start()
            time.sleep(3)

        for thread in threads:
            thread.join()

        self._print_quotas(self.endpoints_library, quotas, "library")

    def quota_playlists(self):
        quotas = [0] * (len(self.endpoints_playlists) + 5)
        threads = [None] * 2
        additions = [(ytmusic.create_playlist, {}), (ytmusic.edit_playlist, {}),
                     (ytmusic.add_playlist_items, {}), (ytmusic.remove_playlist_items, {}),
                     (ytmusic.delete_playlist, {})]
        threads[0] = Thread(target=self._get_quota, args=(self.endpoints_playlists[0], quotas, 0))
        threads[1] = Thread(target=self._playlists, args=(quotas, additions))
        for thread in threads:
            thread.start()
            time.sleep(3)

        for thread in threads:
            thread.join()

        self.endpoints_playlists.extend(additions)
        self._print_quotas(self.endpoints_playlists, quotas, "playlists")

    def _playlists(self, quotas, endpoints):
        for endpoint in endpoints:
            print(f"Testing endpoint data for {endpoint[0].__name__}")

        start_time = time.time()
        i = 0
        while time.time() - start_time <= 3600:
            try:
                playlist_id = self.ytmusic.create_playlist(f"oh no{i-1}", f"testing{i-1}")
                if playlist_id is not None:
                    quotas[1] += 1
            except Exception as e:
                print("Error occured for create_playlist")
                print(e)
                time.sleep(0.15)
                break

            try:
                edit_status = self.ytmusic.edit_playlist(playlist_id, f"oh no{i}")
                if edit_status is not None:
                    quotas[2] += 1
            except Exception as e:
                print("Error occured for edit_playlist")
                print(e)

            try:
                add_status = self.ytmusic.add_playlist_items(playlist_id, ["pleeYqFVR4E"])
                if add_status is not None:
                    quotas[3] += 1

                remove_status = self.ytmusic.remove_playlist_items(
                    playlist_id, [{
                        "videoId": "pleeYqFVR4E",
                        "setVideoId": add_status["playlistEditResults"][0]["setVideoId"]
                    }])
                if remove_status is not None:
                    quotas[4] += 1
            except Exception as e:
                print("Error occured for add_playlist_items or remove_playlist_items")
                print(e)

            try:
                delete_status = self.ytmusic.delete_playlist(playlist_id)
                if delete_status is not None:
                    quotas[5] += 1
            except Exception as e:
                print("Error occured for delete_playlist")
                print(e)

            time.sleep(0.15)
            i += 1


def main():
    ytmusic_auth = YTMusic("../oauth.json")
    endpoints = Endpoints(ytmusic_auth)

    endpoints.quota_search()
    endpoints.quota_browse()
    endpoints.quota_explore()
    endpoints.quota_watch()
    endpoints.quota_library()
    endpoints.quota_playlists()


if __name__ == "__main__":
    main()
