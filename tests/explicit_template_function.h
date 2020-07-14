#pragma once

#include "genpybind.h"

struct GENPYBIND(visible) Something {
  Something() = default;
  template <typename T> Something(T val);
  int value = 0;
};

struct GENPYBIND(visible) Klass {
  template <typename T> T increase(const T &val) GENPYBIND(visible);
}; // Klass

template <typename T> T frobnicate(const T &val) GENPYBIND(visible);

template <typename T> T echo_with_default_argument(T val = 3) GENPYBIND(visible);

constexpr int f() { return 23; }
template <typename T> T echo_with_default_argument_2(T val = f()) GENPYBIND(visible);

extern template Something::Something(int);
extern template int Klass::increase(const int &);
extern template int frobnicate<int>(const int &);
extern template double frobnicate<double>(const double &);
extern template int echo_with_default_argument<int>(int);
extern template int echo_with_default_argument_2<int>(int);
