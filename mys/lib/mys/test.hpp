#pragma once

class Test;

extern Test *tests_head_p;
extern Test *tests_tail_p;

typedef void (*test_func_t)(void);

class Test {

public:
    const char *m_name_p;
    test_func_t m_func;
    Test *m_next_p;

    Test(const char *name_p, test_func_t func);
};
