#include <regex>
#include "mys.hpp"

int main()
{
    std::string sub("subject4");
    std::regex re("(sub)(.*)(\\d)");
    std::smatch groups;
    const char *delim_p;
    unsigned i;
        
    if (std::regex_match(sub, groups, re)) {
        std::cout << "Groups: (";

        for (i = 1, delim_p = "'"; i < groups.size(); i++, delim_p = ", '") {
            std::cout << delim_p << groups[i] << "'";
        }

        std::cout << ")" << std::endl;
    } else {
        std::cout << "No match." << std::endl;
    }

    return 0;
}
