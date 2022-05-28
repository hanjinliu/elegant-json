from __future__ import annotations
import json
from typing import TYPE_CHECKING
from ._objects import JsonDict, EmptyObject

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

def load(path: str) -> JsonDict:
    with open(path, mode="r") as f:
        js = json.load(f)
    return JsonDict(js)

def isempty(obj) -> TypeGuard[EmptyObject]:
    return isinstance(obj, EmptyObject)
