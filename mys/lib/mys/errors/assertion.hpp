#pragma once

#include "base.hpp"

class AssertionError
    : public Error, public std::enable_shared_from_this<AssertionError> {
public:
    String m_message;
    AssertionError()
    {
    }
    AssertionError(const String& message) : m_message(message)
    {
    }
    virtual ~AssertionError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __AssertionError final : public __Error {
public:
    __AssertionError(const std::shared_ptr<AssertionError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};

#define ASSERT(cond)                                            \
    if (!(cond)) {                                              \
        std::make_shared<AssertionError>(#cond)->__throw();     \
    }

#define assert_eq(v1, v2)                                               \
    if (!((v1) == (v2))) {                                              \
        std::cout << "Assert: " << (v1) << " != " << (v2) << std::endl; \
                                                                        \
        std::make_shared<AssertionError>("assert_eq failed")->__throw(); \
    }
