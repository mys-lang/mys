#include "mys.hpp"

List<String> create_args(int argc, const char *argv[])
{
    int i;
    List<String> args({});

    for (i = 0; i < argc; i++) {
        args.push_back(argv[i]);
    }

    return args;
}

std::ostream&
operator<<(std::ostream& os, const Exception& e)
{
    os << e.m_name_p << ": " << e.what();

    return os;
}

std::ostream&
operator<<(std::ostream& os, const std::exception& e)
{
    os << e.what();

    return os;
}

std::ostream&
operator<<(std::ostream& os, const String& obj)
{
    os << *obj.m_string;

    return os;
}
