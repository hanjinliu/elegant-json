from __future__ import annotations
from types import GenericAlias
from typing import Any, Iterable, TYPE_CHECKING, TypeVar, get_args, get_origin

if TYPE_CHECKING:
    from ._json_class import JsonClass


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

class JsonProperty(property):
    def keys(self) -> list[str | int]:
        return self._keys
    
    def set_keys(self, keys):
        self._keys = keys
    
    def setter(self, fset) -> JsonProperty:
        return self.__class__(self.fget, fset)

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
    
    def to_property(self, keys: list[str | int]) -> JsonProperty:
        def fget(jself: JsonClass):
            out: Any = jself._json
            try:
                for k in keys:
                    out = out[k]
            except (KeyError, IndexError):
                out = self.default
            return self.converter(out)
        
        prop = JsonProperty(fget)
        
        if self.mutable:
            def fset(jself: JsonClass, value):
                out: Any = jself._json
                for k in keys[:-1]:
                    out = out[k]
                out[keys[-1]] = value
                return None
        
            prop = prop.setter(fset)
        
        prop.set_keys(keys)
        return prop
