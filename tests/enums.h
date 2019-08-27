#pragma once

#include <string>

#include "genpybind.h"

enum GENPYBIND(visible) State { YES = 0, NO, MAYBE };

enum GENPYBIND(arithmetic) Access { Read = 4, Write = 2, Execute = 1 };

enum class GENPYBIND(visible) Color { red = 2, green, blue };

std::string test_enum(State state) GENPYBIND(visible);
std::string test_enum(Color color) GENPYBIND(visible);
