__version__ = "0.0.1"

from .core import (
    jsonclass,
    create_loader,
    create_constructor,
    isformatted,
)

from ._json_class import JsonClass, Attr

__all__ = [
    "Attr",
    "JsonClass",
    "jsonclass",
    "create_loader",
    "create_constructor",
    "isformatted",
]