from elegant_json import JsonClass, Attr

def test_generic():
    class C(JsonClass):
        __json_template__ = {
            "a": Attr(annotation=list[str]),
            "b": Attr(annotation=tuple[int, str]),
            "c": Attr(annotation=dict[str, float])
        }
        __json_mutable__ = True
        a: list[str]
        b: tuple[int, str]
        c: dict[str, float]
    
    test_data = {
        "a": [1, "a"],
        "b": ["1", "a"],
        "c": {"x": 1.0, "y": "2.3"}
    }
    
    c = C(test_data)
    assert c.a == ["1", "a"]
    assert c.b == (1, "a")
    assert c.c == {"x": 1.0, "y": 2.3}
    
        
def test_nested_json_class():
    class D(JsonClass):
        __json_template__ = {
            "a": Attr(),
            "b": Attr(),
            "c": Attr(),
        }
        __json_mutable__ = True
        a: int
        b: list[int]
        c: None

    class C(JsonClass):
        __json_template__ = {
            "a": Attr("arg", D),
            "irrelevant": ...,
            }
        __json_mutable__ = True
        arg: D

    test_data = {
        "a": {"a": 10, "b": [1,2,3], "c": None},
        "b": 22,
        "c": {"x": 33}
    }

    c = C(test_data)
    assert type(c.arg) is D
    assert c.arg.a == 10
    assert c.arg.b == [1, 2, 3]
    assert c.arg.c is None
    
    c.arg.a = 0
    c.arg.b = []
    
    assert c.arg.a == 0
    assert c.arg.b == []
