#pragma once

#include <memory>
#include "genpybind.h"

extern int global_instance_counter GENPYBIND(visible);

class GENPYBIND(visible) RAII
{
public:
	RAII() { global_instance_counter++; }
	~RAII() { global_instance_counter--; }
};

class GENPYBIND(visible) ProxyRAII
{
public:
	ProxyRAII() = default;

	void __enter__() {
		m_raii_inst.reset();
	}

	void __exit__() {
		m_raii_inst.release();
	}

private:
	std::unique_ptr<RAII> m_raii_inst;
};
