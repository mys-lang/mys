static void run(void)
{
    auto value = 0;

    for (auto i = 0; i < 2000000; i++) {
        value += 1;
    }
}

int main()
{
    run();

    return (0);
}
