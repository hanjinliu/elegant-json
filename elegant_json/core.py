from __future__ import annotations
import json
from typing import Callable, TypeVar, overload
from ._json_class import JsonClass, _JSON_TEMPLATE, _JSON_MUTABLE

_C = TypeVar("_C", bound=type)

@overload
def jsonclass(cls: type[_C], template: dict | None = None, mutable: bool = False) -> type[_C | JsonClass]:
    ...


@overload
def jsonclass(template: dict | None = None, mutable: bool = False) -> Callable[[type[_C]], type[_C | JsonClass]]:
    ...

    
def jsonclass(cls_or_template = None, template=None, mutable=False):
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
    if isinstance(cls_or_template, type):
        cls = cls_or_template
    elif isinstance(cls_or_template, dict):
        cls = None
        template = cls_or_template
    elif cls_or_template is None:
        cls = None
    else:
        raise TypeError
    ns = {_JSON_TEMPLATE: template, _JSON_MUTABLE: mutable}
    new_cls = type(cls.__name__, (cls, JsonClass), ns)
    return new_cls

class _dummy:
    pass

def create_constructor(template=None, mutable=False):
    cls = jsonclass(_dummy, template=template, mutable=mutable)
    return cls

def create_loader(template=None, mutable=False):
    cls = jsonclass(_dummy, template=template, mutable=mutable)
    # NOTE: simply this function can return `cls.load` but will not work if
    # new class has `load` property by chance.
    def load(path: str, encoding: str | None = None):
        with open(path, mode="r", encoding=encoding) as f:
            js = json.load(f)
        return cls(js)
    return load