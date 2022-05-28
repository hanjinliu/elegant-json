from __future__ import annotations
import json
from typing import Mapping, Sequence, Union

JsonObject = Union[int, float, str, list["JsonObject"], None, bool]

class JsonDict(Mapping[str, JsonObject]):
    def __init__(self, d, hist: list = []):
        self._dict = d
        self._hist = hist.copy()
    
    def __getitem__(self, key):
        try:
            out = self._dict[key]
            out = _convert(out, self._hist + [key])
        except KeyError:
            out = EmptyObject(self._hist + [key])
        return out
    
    __getattr__ = __getitem__
    
    def __iter__(self):
        return iter(self._dict)
    
    def __len__(self) -> int:
        return len(self._dict)
    
    def __repr__(self) -> str:
        return json.dumps(self._dict, indent=2)

    def __eq__(self, other) -> bool:
        return self._dict == other

class MutableJsonDict(JsonDict):
    def __setitem__(self, key, value) -> None:
        ...
    
    def __delitem__(self, key) -> None:
        try:
            del self._dict[key]
        except KeyError:
            pass
    
class JsonList(Sequence):
    def __init__(self, l, hist: list = []) -> None:
        self._list = l
        self._hist = hist.copy()
    
    def __iter__(self):
        return iter(self._list)
    
    def __getitem__(self, key):
        try:
            out = self._list[key]
            out = _convert(out, self._hist + [key])
        except IndexError:
            out = EmptyObject(self._hist + [key])
        return out
    
    def __len__(self) -> int:
        return len(self._list)
    
    def __repr__(self) -> str:
        return json.dumps(self._list, indent=2)
    
    def __eq__(self, other) -> bool:
        return self._list == other

def _convert(out, hist):
    if isinstance(out, list):
        out = JsonList(out, hist)
    elif isinstance(out, dict):
        out = JsonDict(out, hist)
    return out

class EmptyObject:
    def __init__(self, hist: list):
        self._hist = hist.copy()
    
    def __getitem__(self, key) -> EmptyObject:
        return self.__class__(self._hist)

    __getattr__ = __getitem__
    
    def __repr__(self) -> str:
        return "Empty"
