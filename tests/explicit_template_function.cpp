#include "explicit_template_function.h"

template <typename T> Something::Something(T val) : value(val) {}

template <typename T> T Klass::increase(const T &val) { return val + 1; }

template <typename T> T frobnicate(const T &val) { return 42 - val; }

template <typename T> T echo_with_default_argument(T val) {return val;}
template <typename T> T echo_with_default_argument_2(T val) {return val;}

template Something::Something(int);
template int Klass::increase(const int &);
template int frobnicate<int>(const int &);
template double frobnicate<double>(const double &);
template int echo_with_default_argument<int>(int);
template int echo_with_default_argument_2<int>(int);
