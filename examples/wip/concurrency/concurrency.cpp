#include <iostream>
#include "fiber.hpp"

class Sleeper : public fiber::Fiber {
public:
    int m_delay;
    const char *m_message_p;

    Sleeper(int delay, const char *message_p)
    {
        m_delay = delay;
        m_message_p = message_p;
    }

    void run()
    {
        while (true) {
            fiber::sleep(m_delay);
            std::cout << "Sleeper awake! " << m_message_p << "\n";
            fiber::yield();
        }
    }
};

void package_main()
{
    std::cout << "Package main!\n";

    fiber::spawn(new Sleeper(1000, "1000"));
    fiber::spawn(new Sleeper(2000, "2000"));
    fiber::spawn(new Sleeper(3000, "3000"));
    fiber::sleep(10000);

    std::cout << "Package main done!\n";
}

int main()
{
    fiber::init();
    package_main();

    return 0;
}
