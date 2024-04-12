#include <iostream>

#include <boost/algorithm/string.hpp>
#include <boost/date_time/gregorian/gregorian.hpp>
#include <boost/date_time/gregorian/parsers.hpp>

#ifndef RUN_TEST

int main()
{
	{
		std::string s("2018-12-01");
		boost::gregorian::date d(boost::gregorian::from_simple_string(s));
		std::cout << boost::gregorian::to_simple_string(d) << std::endl;
	}
}

#endif
