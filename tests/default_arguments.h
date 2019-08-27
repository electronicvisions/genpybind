#pragma once

#include "genpybind.h"

template <typename T, int N> struct Tpl {};

struct GENPYBIND(visible) X {};

void GENPYBIND(visible) function_builtin(int x = 5, bool arg = true) {}
void GENPYBIND(visible) function_class(X x = X()) {}

namespace example {

struct GENPYBIND(visible) Z {
	static constexpr int max = 17;
};

struct GENPYBIND(visible) Y {

  static constexpr int N = 42;

  Y(int v = 0) : _m(v) {};

private:
  int _m;
};

void GENPYBIND(visible) function_class_in_namespace(Y y = Y()) {}


void GENPYBIND(visible) function_class_in_namespace_with_parameter(Y y = Y(Z::max)) {}


} // namespace example


void GENPYBIND(visible)
function_class_outside_namespace(example::Y y = example::Y()) {}

void GENPYBIND(visible)
function_class_outside_namespace_with_parameter_namespaced(::example::Y y = ::example::Y(::example::Z::max)) {}

void GENPYBIND(visible)
function_class_outside_namespace_namespaced(::example::Y y = ::example::Y()) {}

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
