import pytest
import pycontext_manager as m

def test_context_manager():

    with m.ProxyRAII() as pr:
	assert m.global_instance_counter == 1

    with m.ProxyRAII() as pr:
	assert m.global_instance_counter == 1
