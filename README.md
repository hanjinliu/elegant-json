# elegant-json

Deal with JSON files elegantly.

> **Warning**
>
> elegant-json is **Work in Progress**!

### Installation

```
git clone https://github.com/hanjinliu/elegant-json
```

### Motivation

Suppose you have a JSON file in the following format.

```json
{
    "title": "Title",
    "data": {
        "last modified": "2022.06.01",
        "values": [0, 1, 2, 3]
    }
}
```

What would you do?

##### Conventional way

```python
import json

with open("path/to/json") as f:
    js = json.load(f)

# `js` is a nested dictionary
js["title"]
js["data"]["last modified"]
js["data"]["values"][2]
```

This is terrible.

&cross; typing

&cross; missing values

&cross; readability

##### In this module

Copy json and substitute values you want with `Attr` object.

```python
from elegant_json import JsonClass, Attr

# define a class with a json template
class C(JsonClass):
    __json_template__ = {
        "title": Attr(),
        "data": {
            "last modified": Attr(name="last_modified"),
            "values": Attr()
        }
    }

    title: str
    last_modified: str
    values: list[int]

c = C.load("path/to/json")  # or from a dict >>> c = C(js)
c.title
c.last_modified
c.values[2]
```

##### Other helper functions

- `isformatted`

    This function checks if a dictionary is in the given format

    ```python
    from elegant_json import isformatted

    dict0 = {
        "title": "Formatted data",
        "data": {
            "last modified": "yyyy.mm.dd",
            "values": []
        }
    }
    isformatted(dict0, C)  # True

    dict1 = {
        "title": "Wrong data",
        "data": {
            "a": 0,
            "b": 2,
        }
    }
    isformatted(dict1, C)  # False
