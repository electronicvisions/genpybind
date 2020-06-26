import pyexceptions as m

def test_can_raise():
    raise m.my_exception("foo")

def test_can_throw():
    mt = m.my_thrower()
    try:
        mt.my_throw()
    except RuntimeError as e:
        assert(str(e) == "my_exception was thrown")
