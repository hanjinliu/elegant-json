from __future__ import annotations
from typing import Callable, TypeVar, overload
from ._json_class import JsonClassMeta, JsonClass, _JSON_TEMPLATE, _JSON_MUTABLE

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

def create_constructor(template=None, mutable=False):
    cls = jsonclass(object, template=template, mutable=mutable)
    return cls

def create_loader(template=None, mutable=False):
    cls = jsonclass(object, template=template, mutable=mutable)
    return cls.load