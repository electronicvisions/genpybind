#pragma once

#include "genpybind.h"

template <typename T>
class Klass
{
public:
	T echo(T t) {
		return t;
	}
};

template class Klass<int>;
GENPYBIND(opaque) typedef Klass<int> Klass_int;
