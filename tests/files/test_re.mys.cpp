#include <iostream>
#include <string>
#include <regex>

int main()
{
    std::string sub("subject4");
    std::regex re("(sub)(.*)(\\d)");
    std::smatch groups;

    if (std::regex_match(sub, groups, re)) {
        std::cout << "Groups: (";

        for (unsigned i = 1; i < groups.size(); i++) {
            std::cout << (i == 1 ? "'" : ", '") << groups[i] << "'";
        }

        std::cout << ")" << std::endl;
    } else {
        std::cout << "No match." << std::endl;
    }

    return 0;
}
