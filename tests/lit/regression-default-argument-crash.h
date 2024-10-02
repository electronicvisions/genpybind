// SPDX-FileCopyrightText: 2024 Johann Klähn <johann@jklaehn.de>
//
// SPDX-License-Identifier: MIT
//
// RUN: genpybind-tool %s -- 2>&1

#pragma once

#include "genpybind.h"

template <typename T> class value {
public:
  template <typename U = T> constexpr value(const U v = U()) {}
};
template class value<unsigned long>;
