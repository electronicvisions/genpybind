#pragma once

#include <optional>

// clang-format off
#ifdef __GENPYBIND__
#pragma genpybind include<pybind11/stl.h>
#endif // __GENPYBIND__
// clang-format on
#include "genpybind.h"

std::optional<int> example(std::optional<int> value = std::nullopt)
    GENPYBIND(visible);
