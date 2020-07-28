#pragma once


#include <genpybind.h>

struct A;

template <typename T>
struct Base
{
	int value;
};

typedef Base<A> Base_A GENPYBIND(opaque(false));

struct GENPYBIND(visible) A : public Base<A>
{
};
