from typing import Any
import elegant_json as ej
from pathlib import Path
import pytest
from copy import deepcopy

root = Path(__file__).parent / "jsons"

template_1 = {
    "key1": ej.Attr("arg1"), 
    "key2": ej.Attr("arg2"),
    "key3": [0, 1, ej.Attr("arg3")]
}

template_2 = {
    "key1": [
        {"a": ej.Attr("arg1")},
        {"b": ej.Attr("arg2")},
        ej.Attr("arg3"),
    ],
}

template_3 = {
    "key1": {
        "key1": ej.Attr("arg1"),
        "key2": {
            "key1": ej.Attr("arg2"),
            "key2": {
                "key1": ej.Attr("arg3"),
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
        __json_template__ = deepcopy(temp)
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
    init = ej.create_constructor(deepcopy(temp), mutable=mutable)
    
    c = init.load(root/f"test{i}.json")  # type: ignore
    _common_part(c, mutable)

@pytest.mark.parametrize(
    ["temp", "i"],
    [(template_1, 1), (template_2, 2), (template_3, 3)]
)
@pytest.mark.parametrize("mutable", [False, True])
def test_loader(temp, i, mutable):
    loader = ej.create_loader(deepcopy(temp), mutable=mutable)
    
    c = loader(root/f"test{i}.json")
    _common_part(c, mutable)

def test_decorator():
    @ej.jsonclass(deepcopy(template_1))
    class A:
        arg1: int
        arg2: str
        arg3: list[int]
        
    c = A.load(root/f"test1.json")
    _common_part(c, False)

def test_override():
    temp = {"load": ej.Attr()}
    class A(ej.JsonClass):
        __json_template__ = deepcopy(temp)
    
    a = A({"load": 0})
    assert a.load == 0
    
    @ej.jsonclass(temp)
    class B:
        pass
    
    a = B({"load": 0})
    assert a.load == 0


@pytest.mark.parametrize("temp", [template_1, template_2, template_3])
def test_create(temp):
    class C(ej.JsonClass):
        __json_template__ = deepcopy(temp)
        arg1: Any
        arg2: Any
        arg3: Any
    
    value = object()
    c = C.create(value=value)
    assert c.arg1 == value
    assert c.arg2 == value
    assert c.arg3 == value
    