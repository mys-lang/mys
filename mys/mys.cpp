#include "mys.hpp"

shared_vector<shared_string> create_args(int argc, const char *argv[])
{
    int i;
    shared_vector<shared_string> args = {};

    for (i = 1; i < argc; i++) {
        args->push_back(make_shared_string(argv[i]));
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
