#include "example.h"

#ifdef RUN_TEST

#define BOOST_TEST_MODULE example_tests
#include <boost/test/included/unit_test.hpp>

BOOST_AUTO_TEST_CASE( add )
{
	auto res = add_numbers(1.0, 2.0);
	BOOST_TEST(res == 3.0);
}

BOOST_AUTO_TEST_CASE( subtract )
{
	auto res = subtract_numbers(1.0, 2.0);
	BOOST_TEST(res == -1.0);
}

BOOST_AUTO_TEST_CASE( snprintf_function )
{
	auto res = multiply_numbers(-7.0, 2.0);
	std::string tpl = "_%d_";
	int quantity = std::snprintf(NULL, 0, tpl.c_str(), 14);
	BOOST_TEST(quantity == 4);
}

#endif
