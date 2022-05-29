from __future__ import annotations
import json
from pathlib import Path
from types import GenericAlias
from typing import Any, Iterable, TYPE_CHECKING, TypeVar, get_args, get_origin


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

def _define_converter(annotation):
    if annotation is None:
        converter = lambda x: x
    elif isinstance(annotation, GenericAlias):
        origin = get_origin(annotation)
        args = get_args(annotation)
        if origin is list:
            arg = args[0]
            if isinstance(arg, type):
                converter = lambda x: list(_define_converter(arg)(a) for a in x)
            else:
                raise ValueError
        elif origin is dict:
            if args[0] is not str:
                raise TypeError("Only dict[str, ...] is supported.")
            val = args[1]
            if isinstance(val, type):
                converter = lambda x: {k: _define_converter(val)(v) for k, v in x.items()}
            else:
                raise ValueError
        elif origin is tuple:
            converter = lambda x: tuple(_define_converter(arg)(a) for arg, a in zip(args, x))
        else:
            raise ValueError
    else:
        converter = lambda x: annotation(x)
    return converter

class Attr:
    def __init__(
        self,
        name: str | None = None, 
        annotation: type | None = None,
        *,
        default = None,
        mutable: bool | None = None,
    ):
        self.name = name
        self.default = default
        self.mutable = mutable or False
        self.mutability_given = mutable is not None
        self.converter = _define_converter(annotation)
        
    @property
    def name(self) -> str | None:
        return self._name
    
    @name.setter
    def name(self, value: str | None):
        if value is not None and not value.isidentifier():
            raise ValueError(f"{value!r} is not an identifier.")
        self._name = value
    
    def to_property(self, keys: list[str | int]) -> property:
        def fget(jself: JsonClass):
            out = jself._json
            try:
                for k in keys:
                    out = out[k]  # type: ignore
            except (KeyError, IndexError):
                out = self.default
            return self.converter(out)
        
        prop = property(fget)
        
        if self.mutable:
            def fset(jself: JsonClass, value):
                out = jself._json
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
        ns = set()
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
            if attr.name in ns:
                raise ValueError(f"Name collision in attributes: {attr.name!r}.")
            ns.add(attr.name)
            prop = attr.to_property(keys)
            namespace[attr.name] = prop
        
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
