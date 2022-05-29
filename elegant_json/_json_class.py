from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Iterable

from ._json_attribute import Attr

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


class JsonClassMeta(type):
    __json_template__: dict[str, Any | None] = {}
    __json_mutable__: bool = False
    _json_properties: frozenset[str]

    def __new__(
        cls: type,
        name: str,
        bases: tuple,
        namespace: dict,
        **kwds,
    ) -> JsonClassMeta:
        
        js_temp = namespace.get(_JSON_TEMPLATE, {})
        mutable = namespace.get(_JSON_MUTABLE, False)
        props = set()
        for value, keys in _iter_dict(js_temp, []):
            if isinstance(value, str):
                attr = Attr(value, mutable=mutable)
            elif isinstance(value, Attr):
                attr = value
                if attr.name is None:
                    attr_name = keys[-1]
                    if not isinstance(attr_name, str):
                        raise ValueError
                    attr.name = attr_name
                if not attr.mutability_given:
                    attr.mutable = mutable
            else:
                continue
            if attr.name in props:
                raise ValueError(f"Name collision in attributes: {attr.name!r}.")
            props.add(attr.name)
            prop = attr.to_property(keys)
            namespace[attr.name] = prop
        
        jcls: JsonClassMeta = type.__new__(cls, name, bases, namespace, **kwds)
        jcls._json_properties = frozenset(props)
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
        return f"<{self.__class__.__name__} object>"
    
    @property
    def json(self) -> dict[str, Any | None]:
        """Return the original json dictionary."""
        return self._json
    
    @classmethod
    def load(cls, path: str | Path | bytes, encoding: str | None = None):
        """Load a json file and create a json class from it."""
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)
