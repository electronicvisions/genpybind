#pragma once

#include "genpybind.h"

template <typename T, int N> struct Tpl {};

struct GENPYBIND(visible) X {
	static constexpr int max = 17;
};

void GENPYBIND(visible) function_builtin(int x = 5, bool arg = true) {}
void GENPYBIND(visible) function_class(X x = X()) {}

// FIXME: fails if moved to example cf. namespace fixme in cutils.py
static constexpr int min = 13;

namespace example {
struct GENPYBIND(visible) Y {
  static constexpr int N = 42;
  Y(int v = 0) : _m(v) {}
private:
  int _m;
};
void GENPYBIND(visible) function_class_in_namespace(Y y = Y()) {}
void GENPYBIND(visible) function_class_in_namespace_with_parameter(Y y = Y(min), Y y2 = Y(X::max)) {}
} // namespace example

void GENPYBIND(visible)
function_class_outside_namespace(example::Y y = example::Y()) {}

void GENPYBIND(visible)
function_class_outside_namespace_with_parameter(example::Y y = example::Y(min), example::Y y2 = example::Y(X::max)) {}

// TODO: genpybind uses `example::Y::N` as default argument?
/*
void GENPYBIND(visible) function_template_outside_namespace(
    Tpl<example::Y, example::Y::N> y = Tpl<example::Y, example::Y::N>()) {}
*/

// TODO: genpybind fails to expand `Y::N` to fully qualified expression
/*
namespace example {
void GENPYBIND(visible)
    function_template_in_namespace(Tpl<Y, Y::N> y = Tpl<Y, Y::N>()) {}
} // namespace example
*/

// TODO: braced initialization not supported in default argument
// Not sure if pybind11 supports this at all...
/*
void GENPYBIND(visible) function_braced(X x = {}) {}
namespace example {
void GENPYBIND(visible) function_braced_in_namespace(Y y = {}) {}
} // namespace example
void GENPYBIND(visible) function_braced_outside_namespace(example::Y y = {})
*/
