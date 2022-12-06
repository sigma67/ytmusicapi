import os

supported_filetypes = ["mp3", "m4a", "wma", "flac", "ogg"]

def support_exception(filepath):
    if os.path.splitext(filepath)[1][1:] not in supported_filetypes:
        raise Exception(
            "The provided file type is not supported by YouTube Music. Supported file types are "
            + ', '.join(supported_filetypes))    

def check_path(filepath):
    if not os.path.isfile(filepath):
        raise Exception("The provided file does not exist.")    