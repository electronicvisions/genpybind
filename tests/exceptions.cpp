#include "exceptions.h"

my_exception::my_exception(std::string const& msg) : mMsg(msg) {
}

my_exception::~my_exception() throw() {
}

const char* my_exception::what() const throw() {
	return mMsg.c_str();
}

void my_thrower::my_throw() const {
	throw my_exception("my_exception thrown");
}
