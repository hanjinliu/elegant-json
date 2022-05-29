from elegant_json import JsonClass, Attr

def test_inheritance():
    class C(JsonClass):
        __json_template__ = {
            "a": Attr(),
            "b": {
                "x": Attr(),
                "y": Attr(),
            }
        }
    
        a: str
        x: int
        y: int
        
        def get_values(self):
            return self.a, self.x, self.y
    
    class B(C):
        def get_values_as_list(self):
            return list(self.get_values())
    
    b = B({"a": "A", "b": {"x": 0, "y": 1}})
    assert b.get_values() == ("A", 0, 1)
    assert b.get_values_as_list() == ["A", 0, 1]
