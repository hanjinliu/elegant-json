import elegant_json as ej

def test_isformatted():
    class C(ej.JsonClass):
        __json_template__ = {
            "a": ej.Attr(),
            "b": {
                "x": ej.Attr(),
                "y": ej.Attr(),
            }
        }
    
    assert ej.isformatted({
        "a": 0,
        "b": {
            "x": 0,
            "y": 0,
        }
    }, C)
    
    assert ej.isformatted({
        "a": 0,
        "b": {
            "x": 0,
            "y": 0,
            "z": {},
        }
    }, C)
    
    assert not ej.isformatted({
        "A": 0,
        "b": {
            "x": 0,
            "y": 0,
        }
    }, C)
    
    assert not ej.isformatted({
        "a": 0,
        "b": {
            "x": 0,
            "z": 0,
        }
    }, C)