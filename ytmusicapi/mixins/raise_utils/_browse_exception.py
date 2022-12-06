def raise_get_song(browseId):
    if not browseId:
        raise Exception("Invalid browseId provided.")    

def raise_get_lyrics(browseId):
    if not browseId:
        raise Exception("Invalid browseId provided. This song might not have lyrics.")    

def raise_match(match):
    if not match:
        raise Exception("Could not identify the URL for base.js player.")

def raise_match_signature(match):
    if match is None:
        raise Exception("Unable to identify the signatureTimestamp.")    