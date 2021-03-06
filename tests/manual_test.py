import os
import pymanual as m

def test_function_pointer():
    obj = m.Something()
    assert obj.something() is True

def test_lambda():
    obj = m.Something()
    assert obj[42] == 42 + obj.offset

def test_template():
    obj = m.Something()
    assert str(obj) == "uiae"

def test_preamble():
    assert os.environ.get("genpybind") == "preamble"

def test_postamble():
    assert os.environ.get("genpybind") == "preamble"
    assert os.environ.get("genpybind_post") == "postamble"
