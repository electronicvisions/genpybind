// RUN: genpybind-tool %s -- -std=c++17 -xc++ -D__GENPYBIND__ 2>&1
#include "genpybind.h"

template <typename T> class value {
public:
  template <typename U = T> constexpr value(const U v = U()) {}
};
template class value<unsigned long>;
