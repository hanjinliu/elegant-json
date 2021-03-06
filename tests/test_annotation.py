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

def test_json_annotation():
    class D(JsonClass):
        __json_template__ = {
            "id": Attr(),
            "name": Attr(),
        }
        id: int
        name: str
        
    class C(JsonClass):
        __json_template__ = {
            "a": Attr(),
            "list": Attr(),
        }
        
        a: int
        list: list[D]
    
    c = C({"a": "10", "list": [
        {"id": "101", "name": "name1"},
        {"id": "102", "name": "name2"},
    ]})
    
    assert c.a == 10
    assert c.list[0].id == 101
    assert c.list[0].name == "name1"
    assert c.list[1].id == 102
    assert c.list[1].name == "name2"
    
def test_annotation_with_forwardref():
    class C(JsonClass):
        __json_template__ = {
            "a": Attr(),
            "b": {
                "name": Attr(),
                "value": Attr(),
            }
        }
        
        a: "int"
        name: "str"
        value: "list[int]"
    
    c = C({"a": "10", "b": {"name": "1", "value": ["1", "3"]}})
    assert c.a == 10
    assert c.name == "1"
    assert c.value == [1, 3]
