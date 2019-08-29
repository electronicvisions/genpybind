import pytest
import pytypedefs as m

def test_typedefs_expose():
    assert hasattr(m, 'X_t')
    assert not hasattr(m, 'X')

def test_typedefs_hashable():
    assert hasattr(m.X_t, '__hash__')
    assert hasattr(m.X_t, '__eq__')
    assert hasattr(m.X_t, '__lt__')

    a = m.X_t(1)
    b = m.X_t(2)
    c = m.X_t(2)

    assert b == c
    assert not b < c
    assert not b > c
    assert a < b
    assert b > a
    assert a == a
    assert b == b

    x = m.X_t(100)
    y = m.X_t(100)

    data = {}
    data[x] = '123'

    assert data[x] == '123'
    assert data.get(x, False) == '123'

    assert data[y] == '123'
    assert data.get(y, False) == '123'

    z = m.X_t(100)
    assert data[z] == '123'
    assert data.get(z, False) == '123'

    assert str(x) == str(x.get_value())

test_typedefs_expose()
test_typedefs_hashable()
