#include "mys.hpp"

#include <iomanip>

std::shared_ptr<List<String>> create_args(int argc, const char *argv[])
{
    int i;
    auto args = std::make_shared<List<String>>();

    for (i = 0; i < argc; i++) {
        args->append(argv[i]);
    }

    return args;
}

std::ostream&
operator<<(std::ostream& os, const Exception& e)
{
    os << e.what();

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
    if (obj.m_string) {
        os << "\"";

        for (u64 i = 0; i < obj.m_string->size(); i++) {
            os << PrintChar((*obj.m_string)[i]);
        }

        os << "\"";
    } else {
        os << "None";
    }

    return os;
}

std::ostream& operator<<(std::ostream& os, const PrintString& obj)
{
    if (obj.m_value.m_string) {
        for (u64 i = 0; i < obj.m_value.m_string->size(); i++) {
            os << PrintChar((*obj.m_value.m_string)[i]);
        }
    } else {
        os << "None";
    }

    return os;
}

std::ostream&
operator<<(std::ostream& os, const Bytes& obj)
{
    if (obj.m_bytes) {
        os << "b\"";

        for (auto v : *obj.m_bytes) {
            os << "\\x";
            os << std::hex
               << std::setfill('0')
               << std::setw(2)
               << (unsigned)v
               << std::dec;
        }

        os << "\"";
    } else {
        os << "None";
    }

    return os;
}

#if defined(MYS_TEST)

#define ANSI_COLOR_RED "\x1b[31m"
#define ANSI_COLOR_GREEN "\x1b[32m"
#define ANSI_COLOR_YELLOW "\x1b[33m"
#define ANSI_COLOR_BLUE "\x1b[34m"
#define ANSI_COLOR_MAGENTA "\x1b[35m"
#define ANSI_COLOR_CYAN "\x1b[36m"

#define ANSI_BOLD "\x1b[1m"
#define ANSI_RESET "\x1b[0m"

#define COLOR(color, ...) ANSI_RESET ANSI_COLOR_##color __VA_ARGS__ ANSI_RESET

#define BOLD(...) ANSI_RESET ANSI_BOLD __VA_ARGS__ ANSI_RESET

#define COLOR_BOLD(color, ...)                                          \
    ANSI_RESET ANSI_COLOR_##color ANSI_BOLD __VA_ARGS__ ANSI_RESET

Test *tests_head_p = NULL;
Test *tests_tail_p = NULL;

Test::Test(const char *name_p, test_func_t func)
{
    m_name_p = name_p;
    m_func = func;
    m_next_p = NULL;

    if (tests_head_p == NULL) {
        tests_head_p = this;
    } else {
        tests_tail_p->m_next_p = this;
    }

    tests_tail_p = this;
}

#include <chrono>

using namespace std::chrono;

int main()
{
    Test *test_p;
    int passed = 0;
    int failed = 0;
    int total = 0;
    const char *result_p;

    test_p = tests_head_p;

    while (test_p != NULL) {
        auto begin = steady_clock::now();

        try {
            test_p->m_func();
            result_p = COLOR(GREEN, " ✔");
            passed++;
        } catch (std::exception &e) {
            std::cout << "Message: " << e << std::endl;
            result_p = COLOR(RED, " ✘");
            failed++;
        }

        auto end = steady_clock::now();
        auto duration = duration_cast<milliseconds>(end - begin).count();

        std::cout
            << result_p
            << " " << test_p->m_name_p
            << " (" <<  duration << " ms)"
            << std::endl;

        total++;
        test_p = test_p->m_next_p;
    }

    if (failed == 0) {
        return (0);
    } else {
        return (1);
    }
}

#elif defined(MYS_APPLICATION)

extern void package_main(int argc, const char *argv[]);

int main(int argc, const char *argv[])
{
    int res;

    try {
        package_main(argc, argv);
        res = 0;
    } catch (std::exception &e) {
        std::cerr << e << std::endl;
        res = 1;
    }

    return (res);
}

#endif

std::ostream& operator<<(std::ostream& os, const Bool& obj)
{
    if (obj.m_value) {
        os << "True";
    } else {
        os << "False";
    }

    return os;
}

size_t encode_utf8(char *dst_p, i32 ch)
{
    size_t size;

    if(ch < 0x80) {
        dst_p[0] = ch;
        size = 1;
    } else if(ch < 0x800) {
        dst_p[0] = (ch >> 6) | 0xc0;
        dst_p[1] = (ch & 0x3f) | 0x80;
        size = 2;
    } else if(ch < 0x10000) {
        dst_p[0] = (ch >> 0xc) | 0xe0;
        dst_p[1] = ((ch >> 6) & 0x3f) | 0x80;
        dst_p[2] = (ch & 0x3f) | 0x80;
        size = 3;
    } else if(ch < 0x200000) {
        dst_p[0] = (ch >> 0x12) | 0xf0;
        dst_p[1] = ((ch >> 0xc) & 0x3f) | 0x80;
        dst_p[2] = ((ch >> 6) & 0x3f) | 0x80;
        dst_p[3] = (ch & 0x3f) | 0200;
        size = 4;
    } else {
        size = 0;
    }

    return size;
}

std::ostream& operator<<(std::ostream& os, const Char& obj)
{
    char buf[4];
    size_t size;

    size = encode_utf8(&buf[0], obj.m_value);

    os << "'";

    for (size_t i = 0; i < size; i++) {
        os << buf[i];
    }

    os << "'";

    return os;
}

std::ostream& operator<<(std::ostream& os, const PrintChar& obj)
{
    char buf[4];
    size_t size;

    size = encode_utf8(&buf[0], obj.m_value.m_value);

    for (size_t i = 0; i < size; i++) {
        os << buf[i];
    }

    return os;
}

const String& string_not_none(const String& obj)
{
    if (!obj.m_string) {
        throw NoneError("object is None");
    }

    return obj;
}

const Bytes& bytes_not_none(const Bytes& obj)
{
    if (!obj.m_bytes) {
        throw NoneError("object is None");
    }

    return obj;
}

std::ostream& operator<<(std::ostream& os, const Object& obj)
{
    obj.__format__(os);

    return os;
}

String::String(const char *str)
{
    if (str) {
        m_string = std::make_shared<std::vector<Char>>();

        for (size_t i = 0; i < strlen(str); i++) {
            m_string->push_back(str[i]);
        }
    } else {
        m_string = nullptr;
    }
}

String String::operator+(const String& other)
{
    String res("");

    res += *this;
    res += other;

    return res;
}

String String::operator*(int value) const
{
    String res;
    int i;

    for (i = 0; i < value; i++) {
        res += *this;
    }

    return res;
}

Bytes String::to_utf8() const
{
    Bytes res({});
    size_t size;
    char buf[4];

    for (const auto & ch : *m_string) {
        size = encode_utf8(&buf[0], ch.m_value);

        for (size_t i = 0; i < size; i++) {
            res += buf[i];
        }
    }

    return res;
}

void String::upper() const
{
    for (auto& ch : *m_string) {
        ch.m_value = toupper(ch.m_value);
    }
}

void String::lower() const
{
    for (auto& ch : *m_string) {
        ch.m_value = tolower(ch.m_value);
    }
}

Bool String::starts_with(const String& value) const
{
    size_t value_length = value.__len__();

    if (value_length > m_string->size()) {
        return Bool(false);
    }

    for (u64 i = 0; i < value_length; i++) {
        if ((*m_string)[i] != (*value.m_string)[i]) {
            return false;
        }
    }

    return true;
}

int String::__len__() const
{
    return shared_ptr_not_none(m_string)->size();
}

String String::__str__() const
{
    String res("");

    res.m_string->insert(res.m_string->end(),
                         shared_ptr_not_none(m_string)->begin(),
                         shared_ptr_not_none(m_string)->end());

    return res;
}

Char& String::get(i64 index) const
{
    if (index < 0) {
        index = m_string->size() + index;
    }

    if (index < 0 || index >= static_cast<i64>(m_string->size())) {
        throw IndexError("string index out of range");
    }

    return (*m_string)[index];
}

u8& Bytes::operator[](i64 index) const
{
    if (index < 0) {
        index = m_bytes->size() + index;
    }

    if (index < 0 || index >= static_cast<i64>(m_bytes->size())) {
        throw IndexError("bytes index out of range");
    }

    return (*m_bytes)[index];
}

i64 String::__int__() const
{
    char buf[32];

    // ToDo: proper checks and so on
    if (m_string->size() == 0) {
        return 0;
    }

    if (m_string->size() > 31) {
        throw ValueError("too big");
    }

    for (size_t i = 0; i < m_string->size(); i++) {
        buf[i] = (*m_string)[i].m_value;
    }

    buf[m_string->size()] = '\0';

    return atoi(&buf[0]);
}

String input(String prompt)
{
    std::string value;

    std::cout << PrintString(prompt) << std::flush;
    getline(std::cin, value);

    return String(value);
}

String String::join(const std::shared_ptr<List<String>>& list) const
{
    String res("");
    size_t j = 0;

    for (auto i : list->m_list) {
        res += i;
        if (j < list->m_list.size() - 1) {
            res += *this;
        }
        ++j;
    }
    return res;
}

String bytes_str(const Bytes& value)
{
    std::stringstream ss;

    ss << value;

    return String(ss.str().c_str());
}

String string_str(const String& value)
{
    if (value.m_string) {
        String res("");

        res.m_string->insert(res.m_string->end(),
                             value.m_string->begin(),
                             value.m_string->end());

        return res;
    } else {
        return String("None");
    }
}

Exception::Exception(const char *name_p, String message)
{
    m_what = String(name_p);
    m_what += ": ";
    m_what += message;
    m_what_bytes = m_what.to_utf8();
    m_what_bytes += 0; // NULL termination.
}

void Object::__format__(std::ostream& os) const
{
}

String Object::__str__() const
{
    return String("Object()");
}
