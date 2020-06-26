import pyexplicit_template_class as m

def test_klass():
    k = m.Klass_int()
    assert 3 == k.echo(3)
