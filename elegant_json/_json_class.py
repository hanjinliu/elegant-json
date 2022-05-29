from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Iterable

_JSON_TEMPLATE = "__json_template__"
_JSON_MUTABLE = "__json_mutable__"

def _iter_dict(d: dict[str, Any | None], keys: list[str | int]) -> Iterable[tuple[Any | None, list[str | int]]]:
    for k, v in d.items():
        next_keys = keys + [k]
        if isinstance(v, (list, tuple)):
            yield from  _iter_list(v, next_keys)
        elif isinstance(v, dict):
            yield from  _iter_dict(v, next_keys)
        else:
            yield v, next_keys

def _iter_list(l: Iterable[Any | None], keys: list[str | int]) -> Iterable[tuple[Any | None, list[str | int]]]:
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
                out = out[k]  # type: ignore
        except (KeyError, IndexError):
            out = default
        return out
    
    prop = property(fget)
    
    if mutable:
        def fset(self: JsonClass, value):
            out = self._json
            for k in keys[:-1]:
                out = out[k]  # type: ignore
            out[keys[-1]] = value  # type: ignore
            return None
    
        prop = prop.setter(fset)
    
    return prop

class JsonClassMeta(type):
    __json_template__: dict[str, Any | None] = {}
    __json_mutable__: bool = False

    def __new__(
        cls: type,
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
        
        jcls: JsonClassMeta = type.__new__(cls, name, bases, namespace, **kwds)
        return jcls


class JsonClass(metaclass=JsonClassMeta):
    """The base class of json class."""
    
    def __init__(self, d: dict[str, Any | None], /):
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
    def load(cls, path: str | Path | bytes, encoding: str | None = None):
        """Load a json file and create a json class from it."""
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)
