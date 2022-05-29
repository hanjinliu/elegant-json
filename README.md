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

js = C.load("path/to/json")
js.title
js.last_modified
js.values[2]
```