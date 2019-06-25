#pragma once

#include "genpybind.h"

// TODO: Add tests for opaque typedefs, (non-)alias typedefs

class GENPYBIND(visible) A {};

typedef A typedef_A GENPYBIND(visible);
