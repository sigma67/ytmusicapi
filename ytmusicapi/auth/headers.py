import json
import os
from typing import Dict


def load_headers_file(auth: str) -> Dict:
    if os.path.isfile(auth):
        with open(auth) as json_file:
            input_json = json.load(json_file)
    else:
        input_json = json.loads(auth)
    return input_json
