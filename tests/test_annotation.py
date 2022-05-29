from elegant_json import JsonClass, Attr

def test_annotation():
    class C(JsonClass):
        __json_template__ = {
            "a": Attr(),
            "b": {
                "name": Attr(),
                "value": Attr(),
            }
        }
        
        a: int
        name: str
        value: list[int]
    
    c = C({"a": "10", "b": {"name": "1", "value": ["1", "3"]}})
    assert C.__json_template__["a"].annotation == int
    assert C.__json_template__["b"]["name"].annotation == str
    assert C.__json_template__["b"]["value"].annotation == list[int]
    assert c.a == 10
    assert c.name == "1"
    assert c.value == [1, 3]
        