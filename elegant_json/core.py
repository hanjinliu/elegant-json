import json
from ._objects import JsonDict

def load(path) -> JsonDict:
    with open(path, mode="r") as f:
        js = json.load(f)
    return JsonDict(js)