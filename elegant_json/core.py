from __future__ import annotations
import json
from pathlib import Path
from typing import Callable, Literal, TypeVar, overload, Any
from ._json_class import JsonClass, _JSON_TEMPLATE, _JSON_MUTABLE
from ._json_attribute import JsonProperty

_C = TypeVar("_C")

@overload
def jsonclass(template_or_class: type[_C], template: dict[str, Any | None], mutable: bool = False) -> type[_C | JsonClass]:
    ...

@overload
def jsonclass(template_or_class: Literal[None], template: dict[str, Any | None], mutable: bool = False) -> Callable[[type[_C]], type[_C | JsonClass]]:
    ...
    
@overload
def jsonclass(template_or_class: dict[str, Any | None], template: Literal[None] = None, mutable: bool = False) -> Callable[[type[_C]], type[_C | JsonClass]]:
    ...

    
def jsonclass(template_or_class=None, template=None, mutable=False):
    """

    Parameters
    ----------
    cls_or_template : _type_, optional
        _description_, by default None
    template : _type_, optional
        _description_, by default None
    mutable : bool, optional
        If true, properties are mutable.

    Returns
    -------
    subclass of JsonClass
        An class that inherits the input class and ``JsonClass``.
    
    Excamples
    ---------
    >>> template = {..., {..., "xxx": "a"}}
    >>> @jsonclass(template)
    >>> class C:
    >>>     a: int
    >>> c = C()
    >>> c.a  # get some value
    """
    if isinstance(template_or_class, type):
        cls = template_or_class
    elif isinstance(template_or_class, dict):
        cls = None
        template = template_or_class
    elif template_or_class is None:
        cls = None
    else:
        raise TypeError
    
    if not isinstance(template, dict):
        raise TypeError("`template` must be given as a dict.")
    
    def _func(cls_):
        ns = {_JSON_TEMPLATE: template, _JSON_MUTABLE: mutable}
        return type(cls_.__name__, (cls_, JsonClass), ns)
    
    return _func if cls is None else _func(cls)

class _dummy:
    """Dummy class for json class creation."""

def create_constructor(template: dict[str, Any | None], mutable: bool = False, name=None):
    cls = jsonclass(_dummy, template=template, mutable=mutable)
    return cls

def create_loader(template: dict[str, Any | None], mutable: bool = False, name=None):
    cls = jsonclass(_dummy, template=template, mutable=mutable)
    # NOTE: simply this function can return `cls.load` but will not work if
    # new class has `load` property by chance.
    def load(path: str | Path | bytes, encoding: str | None = None):
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)  # type: ignore
    return load


def isformatted(obj, json_class: type[JsonClass]) -> bool:
    if not isinstance(obj, dict):
        return False
    for name in json_class._json_properties:
        prop: JsonProperty = getattr(json_class, name)
        try:
            out: Any = obj
            for k in prop.keys():
                out = out[k]
        except (KeyError, IndexError):
            return False
    return True