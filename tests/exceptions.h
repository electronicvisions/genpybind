#pragma once

#include <exception>
#include <string>

#include "genpybind.h"

class GENPYBIND(visible) my_exception : std::exception
{
public:
	my_exception(std::string const& msg);
	virtual ~my_exception() throw();

	virtual const char* what() const throw();

private:
	std::string mMsg;
};

class GENPYBIND(visible) my_thrower
{
public:
	void my_throw() const;
};
