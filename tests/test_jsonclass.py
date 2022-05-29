from typing import Any
import elegant_json as ej
from pathlib import Path
import pytest

from elegant_json.core import jsonclass

root = Path(__file__).parent / "jsons"

template_1 = {
    "key1": "arg1", 
    "key2": "arg2",
    "key3": [0, 1, "arg3"]
}

template_2 = {
    "key1": [
        {"a": "arg1"},
        {"b": "arg2"},
        "arg3",
    ],
}

template_3 = {
    "key1": {
        "key1": "arg1",
        "key2": {
            "key1": "arg2",
            "key2": {
                "key1": "arg3",
                "key2": [],
            }
        }
    }
}

def _common_part(c, mutable):
    assert c.arg1 == 1
    assert c.arg2 == "a"
    assert c.arg3 == [1, 2, 3]

    if mutable:
        c.arg1 = 2
        c.arg2 = "t"
        c.arg3 = [0]
        
        assert c.arg1 == 2
        assert c.arg2 == "t"
        assert c.arg3 == [0]

@pytest.mark.parametrize(
    ["temp", "i"],
    [(template_1, 1), (template_2, 2), (template_3, 3)]
)
@pytest.mark.parametrize("mutable", [False, True])
def test_json_class(temp, i, mutable):
    class C(ej.JsonClass):
        __json_template__ = temp
        __json_mutable__ = mutable
        arg1: int
        arg2: str
        arg3: list[int]
    
    c = C.load(root/f"test{i}.json")
    _common_part(c, mutable)

@pytest.mark.parametrize(
    ["temp", "i"],
    [(template_1, 1), (template_2, 2), (template_3, 3)]
)
@pytest.mark.parametrize("mutable", [False, True])
def test_constructor(temp, i, mutable):
    init = ej.create_constructor(temp, mutable=mutable)
    
    c = init.load(root/f"test{i}.json")  # type: ignore
    _common_part(c, mutable)

@pytest.mark.parametrize(
    ["temp", "i"],
    [(template_1, 1), (template_2, 2), (template_3, 3)]
)
@pytest.mark.parametrize("mutable", [False, True])
def test_loader(temp, i, mutable):
    loader = ej.create_loader(temp, mutable=mutable)
    
    c = loader(root/f"test{i}.json")
    _common_part(c, mutable)

def test_decorator():
    @jsonclass(template_1)
    class A:
        arg1: int
        arg2: str
        arg3: list[int]
        
    c = A.load(root/f"test1.json")
    _common_part(c, False)
    
    
    
    