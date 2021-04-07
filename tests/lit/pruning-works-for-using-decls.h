// RUN: genpybind-tool --dump-graph=pruned %s -- -std=c++17 -xc++ -D__GENPYBIND__ 2>&1 | FileCheck %s --strict-whitespace
#pragma once

#include "genpybind.h"

namespace outer {
namespace detail {
struct something {};
} // namespace detail
using detail::something;
} // namespace outer

// CHECK: Declaration context graph after pruning:
// CHECK-NEXT: <no children>
