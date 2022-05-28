from __future__ import annotations
import json
from typing import Any, Iterable

def _iter_dict(d: dict[str, Any], keys: list[str | int]) -> Iterable[tuple[Any, list[str | int]]]:
    for k, v in d.items():
        next_keys = keys + [k]
        if isinstance(v, (list, tuple)):
            yield from  _iter_list(v, next_keys)
        elif isinstance(v, dict):
            yield from  _iter_dict(v, next_keys)
        else:
            yield v, next_keys

def _iter_list(l: list[Any], keys: list[str | int]) -> Iterable[tuple[Any, list[str | int]]]:
    for k, v in enumerate(l):
        next_keys = keys + [k]
        if isinstance(v, (list, tuple)):
            yield from  _iter_list(v, next_keys)
        elif isinstance(v, dict):
            yield from  _iter_dict(v, next_keys)
        else:
            yield v, next_keys

def _define_property(
    name: str,
    keys: list[str | int],
    mutable: bool = False,
    default: Any | None = None,
) -> property:
    if not name.isidentifier():
        raise ValueError(f"{name!r} is not an identifier.")
    def fget(self: JsonClass):
        out = self._json
        try:
            for k in keys:
                out = out[k]
        except (KeyError, IndexError):
            out = default
        return out
        
    if mutable:
        def fset(self: JsonClass, value):
            out = self._json
            for k in keys[:-1]:
                out = out[k]
            out[keys[-1]] = value
            return None
    else:
        fset = None
    
    return property(fget, fset)


_JSON_TEMPLATE = "__json_template__"
_JSON_MUTABLE = "__json_mutable__"

class JsonClassMeta(type):
    __json_template__ = {}
    __json_mutable__ = False
    def __new__(
        fcls: type,
        name: str,
        bases: tuple,
        namespace: dict,
        **kwds,
    ) -> JsonClassMeta:
        
        js_temp = namespace.get(_JSON_TEMPLATE, {})
        mutable = namespace.get(_JSON_MUTABLE, False)
        
        for property_name, keys in _iter_dict(js_temp, []):
            if not isinstance(property_name, str):
                continue
            prop = _define_property(property_name, keys, mutable)
            namespace[property_name] = prop
        
        cls: JsonClassMeta = type.__new__(fcls, name, bases, namespace, **kwds)
        return cls

class JsonClass(metaclass=JsonClassMeta):
    """The base class of json class."""
    
    def __init__(self, d: dict[str, Any], /):
        if not isinstance(d, dict):
            raise TypeError(
                f"Input of {self.__class__.__name__} must be a dict, got {type(d)}"
            )
        self._json = d
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"
    
    @property
    def json(self) -> dict[str, Any]:
        """Return the original json dictionary."""
        return self._json
    
    @classmethod
    def load(cls, path: str, encoding: str | None = None):
        """Load a json file and create a json class from it."""
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)


"""
d = {"a": [None, "arg1"],
     "b": "arg2",
     "c": {
         "x": "arg3"
     }}

class C(JsonClass):
    __json_template__ = d
    a: int
C().a

@make(d)
class C:
    a: int
C().a

constructor = make_constructor(d)
ins = constructor(js)
ins.a

loader = make_loader(d)
ins = loader(path)
ins.a
"""