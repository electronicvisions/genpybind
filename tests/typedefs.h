#pragma once

#include "genpybind.h"

// a "read-only" class that we cannot modify
struct X {
	X(int i = 0) : m_i(i) {}

	int get_value() const { return m_i; }

	bool operator== (X const& other) const {
		return m_i == other.m_i;
	}

	bool operator< (X const& other) const {
		return m_i < other.m_i;
	}

private:
	int m_i;
};

// let's add some functionality for it
typedef X X_t GENPYBIND(expose_as("X_t"), opaque(true));

GENPYBIND_MANUAL({
	auto my_X = parent.attr("X_t");
	auto ism = parent->py::is_method(my_X);
	my_X.attr("__hash__") = parent->py:: cpp_function([](X const& self) { return self.get_value(); }, ism);
	my_X.attr("__str__") = parent->py:: cpp_function([parent](X const& self) { return parent->std:: to_string(self.get_value()); }, ism);
})

// TODO: Add tests for opaque typedefs, (non-)alias typedefs
