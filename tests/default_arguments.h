#pragma once

#include "genpybind.h"

template <typename T, int N> struct Tpl {};

struct GENPYBIND(visible) X {};

inline void GENPYBIND(visible) function_builtin(int x = 5, bool arg = true) {}
inline void GENPYBIND(visible) function_class(X x = X()) {}

namespace example {
struct GENPYBIND(visible) Y {
  static constexpr int N = 42;
};
inline void GENPYBIND(visible) function_class_in_namespace(Y y = Y()) {}
} // namespace example

inline void GENPYBIND(visible)
    function_class_outside_namespace(example::Y y = example::Y()) {}

template<typename T>
class Klass {
public:
	T echo(T t, int i=1) {return t;}
};

template class Klass<int>;
GENPYBIND(opaque) typedef Klass<int> Klass_int;

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
/*
void GENPYBIND(visible) function_braced(X x = {}) {}
namespace example {
void GENPYBIND(visible) function_braced_in_namespace(Y y = {}) {}
} // namespace example
void GENPYBIND(visible) function_braced_outside_namespace(example::Y y = {})
*/
