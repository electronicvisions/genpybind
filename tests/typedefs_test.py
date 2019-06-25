import pytest
import pytypedefs as m

def test_alias():
    assert hasattr(m, 'typedef_A')
    assert isinstance(m.typedef_A(), m.A)
