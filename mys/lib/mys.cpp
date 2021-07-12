#include <iomanip>
#include <alloca.h>
#include "mys.hpp"

#include "unicodectype.cpp"
#include "fiber.cpp"
#include "memory.cpp"
#include "whereami.c"

extern void __application_init(void);
extern void __application_exit(void);
extern void package_main(int argc, const char *argv[]);

#if defined(MYS_TEST)
#    include <chrono>
#endif

namespace mys {

TracebackEntry *traceback_bottom_p;
TracebackEntry *traceback_top_p;
TracebackEntry traceback_entry;

static void ignore_sigpipe()
{
    sigset_t sigpipe_mask;
    sigset_t saved_mask;

    sigemptyset(&sigpipe_mask);
    sigaddset(&sigpipe_mask, SIGPIPE);

    if (pthread_sigmask(SIG_BLOCK, &sigpipe_mask, &saved_mask) == -1) {
        perror("pthread_sigmask");
        exit(1);
    }
}

#if defined(MYS_TRACEBACK)

void print_traceback(void)
{
    std::cerr << "Traceback (most recent call last):" << std::endl;

    TracebackEntry *item_p;
    TracebackEntryInfo *entry_info_p;

    item_p = traceback_bottom_p->next_p;

    while (true) {
        entry_info_p = &item_p->info_p->entries_info_p[item_p->index];
        std::cerr
            << "  File: \"" << item_p->info_p->path_p << "\","
            << " line " << entry_info_p->line_number
            << " in " << entry_info_p->name_p << "\n"
            << "    " << entry_info_p->code_p << "\n";

        if (item_p == traceback_top_p) {
            break;
        }

        item_p = item_p->next_p;
    }
}

void print_error_traceback(const mys::shared_ptr<Error>& error,
                           std::ostream& os)
{
    os << "Traceback (most recent call last):" << std::endl;

    TracebackEntryInfo *entry_info_p;

    for (auto item : error->m_traceback) {
        entry_info_p = &item.info_p->entries_info_p[item.index];
        os
            << "  File: \"" << item.info_p->path_p << "\","
            << " line " << entry_info_p->line_number
            << " in " << entry_info_p->name_p << "\n"
            << "    " << entry_info_p->code_p << "\n";
    }

    os << "\n";
}

#else

void print_traceback(void)
{
}

void print_error_traceback(const mys::shared_ptr<Error>& error,
                           std::ostream& os)
{
}

#endif

mys::shared_ptr<List<String>> create_args(int argc, const char *argv[])
{
    int i;
    auto args = mys::make_shared<List<String>>();

    for (i = 0; i < argc; i++) {
        args->append(argv[i]);
    }

    return args;
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

#if defined(MYS_COVERAGE)
std::ofstream mys_coverage_file;
#endif

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

using namespace std::chrono;

static bool is_test_match(Test *test_p, const char *test_pattern_p)
{
    const char *full_test_name_p;
    size_t full_test_name_length;
    size_t pattern_length;
    size_t offset;
    bool match_beginning;
    bool match_end;
    char *pattern_p;

    if (test_pattern_p == NULL) {
        return true;
    }

    pattern_length = strlen(test_pattern_p);

    if (pattern_length == 0) {
        return (true);
    }

    match_beginning = (test_pattern_p[0] == '^');
    match_end = (test_pattern_p[pattern_length - 1] == '$');
    pattern_p = (char *)alloca(pattern_length + 1);
    strcpy(pattern_p, test_pattern_p);

    if (match_beginning) {
        pattern_p++;
        pattern_length--;
    }

    if (match_end) {
        pattern_length--;
    }

    full_test_name_p = test_p->m_name_p;
    full_test_name_length = strlen(full_test_name_p);

    if (pattern_length > full_test_name_length) {
        return false;
    }

    if (match_beginning || match_end) {
        if ((pattern_length == 0) && match_beginning && match_end) {
            return false;
        }

        if (match_beginning) {
            if (strncmp(full_test_name_p, pattern_p, pattern_length) != 0) {
                return false;
            }
        }

        if (match_end) {
            offset = (full_test_name_length - pattern_length);

            if (strncmp(&full_test_name_p[offset],
                        pattern_p,
                        pattern_length) != 0) {
                return false;
            }
        }
    } else if (strstr(full_test_name_p, pattern_p) == NULL) {
        return false;
    }

    return true;
}

int main(int argc, const char *argv[])
{
    Test *test_p;
    int failed = 0;
    const char *result_p;
    const char *test_pattern_p;

    if (argc == 2) {
        test_pattern_p = argv[1];
    } else {
        test_pattern_p = NULL;
    }

    ignore_sigpipe();

    __MYS_TRACEBACK_INIT();
    init();

    try {
        __application_init();
    } catch (const __Error &e) {
        __MYS_TRACEBACK_RESTORE();
        print_error_traceback(e.m_error, std::cout);
        std::cout << PrintString(e.m_error->__str__()) << std::endl;
        __MYS_TRACEBACK_EXIT_MAIN();

        return 1;
    }

    test_p = tests_head_p;

    while (test_p != NULL) {
        if (is_test_match(test_p, test_pattern_p)) {
            auto begin = steady_clock::now();

            try {
                test_p->m_func();
                result_p = COLOR(GREEN, " ✔");
            } catch (const __Error &e) {
                __MYS_TRACEBACK_RESTORE();
                print_error_traceback(e.m_error, std::cout);
                std::cout << PrintString(e.m_error->__str__()) << std::endl;
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
        }

        test_p = test_p->m_next_p;
    }

    try {
        __application_exit();
    } catch (const __Error &e) {
        __MYS_TRACEBACK_RESTORE();
        print_error_traceback(e.m_error, std::cout);
        std::cout << PrintString(e.m_error->__str__()) << std::endl;
        __MYS_TRACEBACK_EXIT_MAIN();

        return 1;
    }

    __MYS_TRACEBACK_EXIT_MAIN();

    if (failed == 0) {
        return 0;
    } else {
        return 1;
    }
}

#elif defined(MYS_APPLICATION)

int main(int argc, const char *argv[])
{
    int res = 1;

    ignore_sigpipe();

    __MYS_TRACEBACK_INIT();
    init();

    try {
        __application_init();
        package_main(argc, argv);
        res = 0;
    } catch (const __SystemExitError &e) {
        __MYS_TRACEBACK_RESTORE();

        // This exception should probably contain the exit code.
        auto error = static_cast<mys::shared_ptr<SystemExitError>>(e.m_error);

        if (error->m_message.m_string) {
            std::cerr << e.m_error << std::endl;
        } else {
            res = 0;
        }
    } catch (const __Error &e) {
        __MYS_TRACEBACK_RESTORE();
        print_error_traceback(e.m_error, std::cerr);
        std::cerr << e.m_error << std::endl;
    }

    __application_exit();
    __MYS_TRACEBACK_EXIT_MAIN();

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

    if (ch < 0x80) {
        dst_p[0] = ch;
        size = 1;
    } else if (ch < 0x800) {
        dst_p[0] = (ch >> 6) | 0xc0;
        dst_p[1] = (ch & 0x3f) | 0x80;
        size = 2;
    } else if (ch < 0x10000) {
        dst_p[0] = (ch >> 0xc) | 0xe0;
        dst_p[1] = ((ch >> 6) & 0x3f) | 0x80;
        dst_p[2] = (ch & 0x3f) | 0x80;
        size = 3;
    } else if (ch < 0x200000) {
        dst_p[0] = (ch >> 0x12) | 0xf0;
        dst_p[1] = ((ch >> 0xc) & 0x3f) | 0x80;
        dst_p[2] = ((ch >> 6) & 0x3f) | 0x80;
        dst_p[3] = (ch & 0x3f) | 0x80;
        size = 4;
    } else {
        size = 0;
    }

    return size;
}

size_t decode_utf8(char *src_p, size_t size, i32 *ch)
{
    if ((src_p[0] & 0x80) == 0) {
        *ch = src_p[0];
        size = 1;
    } else if ((src_p[0] & 0xe0) == 0xc0) {
        *ch = (src_p[0] & 0x1f) << 6;
        *ch += src_p[1] & 0x3f;
        size = 2;
    } else if ((src_p[0] & 0xf0) == 0xe0) {
        *ch = (src_p[0] & 0x0f) << 12;
        *ch += (src_p[1] & 0x3f) << 6;
        *ch += (src_p[2] & 0x3f);
        size = 3;
    } else if ((src_p[0] & 0xf8) == 0xf0) {
        *ch = (src_p[0] & 0x07) << 18;
        *ch += (src_p[1] & 0x3f) << 12;
        *ch += (src_p[2] & 0x3f) << 6;
        *ch += (src_p[3] & 0x3f);
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

#if !defined(MYS_UNSAFE)
void abort_is_none()
{
    print_traceback();
    std::cerr << "\nPanic(message=\"Object is None.\")\n";
    abort();
}

const String& string_not_none(const String& obj)
{
    if (!obj.m_string) {
        abort_is_none();
    }

    return obj;
}

String& string_not_none(String& obj)
{
    if (!obj.m_string) {
        abort_is_none();
    }

    return obj;
}

const Regex& regex_not_none(const Regex& obj)
{
    if (!obj.m_compiled) {
        abort_is_none();
    }

    return obj;
}

const RegexMatch& regexmatch_not_none(const RegexMatch& obj)
{
    if (!obj.m_match_data) {
        abort_is_none();
    }

    return obj;
}

const Bytes& bytes_not_none(const Bytes& obj)
{
    if (!obj.m_bytes) {
        abort_is_none();
    }

    return obj;
}
#endif

std::ostream& operator<<(std::ostream& os, Object& obj)
{
    os << PrintString(obj.__str__());

    return os;
}

String::String(const char *str)
{
    if (str) {
        m_string = mys::make_shared<CharVector>();
        for (size_t i = 0; i < strlen(str); i++) {
            append(Char(str[i]));
        }
    } else {
        m_string = nullptr;
    }
}

String::String(const Bytes& bytes)
{
    size_t size;
    i32 ch;
    size_t pos;

    if (bytes.m_bytes) {
        m_string = mys::make_shared<CharVector>();
        pos = 0;

        while (pos < bytes.m_bytes->size()) {
            size = decode_utf8((char *)&bytes.m_bytes->data()[pos],
                               bytes.m_bytes->size() - pos,
                               &ch);

            if (size == 0) {
                mys::make_shared<ValueError>("invalid UTF-8")->__throw();
            }

            m_string->push_back(Char(ch));
            pos += size;
        }
    } else {
        m_string = nullptr;
    }
}

String::String(const Bytes& bytes, i64 start, i64 end)
{
    size_t size;
    i32 ch;

    if (bytes.m_bytes) {
        if (start > bytes.m_bytes->size()) {
            start = bytes.m_bytes->size();
        }

        if (end > bytes.m_bytes->size()) {
            end = bytes.m_bytes->size();
        }

        m_string = mys::make_shared<CharVector>();

        while (start < end) {
            size = decode_utf8((char *)&bytes.m_bytes->data()[start],
                               end - start,
                               &ch);

            if (size == 0) {
                mys::make_shared<ValueError>("invalid UTF-8")->__throw();
            }

            m_string->push_back(Char(ch));
            start += size;
        }
    } else {
        m_string = nullptr;
    }
}

#if 0
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
#endif

String String::operator+(const String& other)
{
    String res("");

    res.append(*this);
    res.append(other);

    return res;
}

void String::operator*=(int value)
{
    String copy("");
    copy.append(*this);

    m_string = mys::make_shared<CharVector>();
    for (int i = 0; i < value; i++) {
        append(copy);
    }
}

String String::operator*(int value) const
{
    String res("");
    int i;

    for (i = 0; i < value; i++) {
        res.append(*this);
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

void String::from_unsigned(std::stringstream& ss, u64 value, char radix)
{
    int msb = 0;

    m_string = mys::make_shared<CharVector>();

    switch (radix) {

    case 'b':
        for (int i = 0; i < 64; i++) {
            if (value & (1ull << i)) {
                msb = i;
            }
        }

        for (int i = msb; i >= 0; i--) {
            ss << (value & (1ull << i) ? '1' : '0');
        }

        break;

    case 'o':
        ss << std::oct << value << std::dec;
        break;

    case 'd':
        ss << value;
        break;

    case 'x':
        ss << std::hex << value << std::dec;
        break;
    }

    for (auto ch : ss.str()) {
        append(Char(ch));
    }
}

String::String(i64 value, char radix)
{
    std::stringstream ss;
    int msb = 0;

    if (value < 0) {
        ss << '-';
        value *= -1;
    }

    from_unsigned(ss, value, radix);
}

String::String(u64 value, char radix)
{
    std::stringstream ss;

    from_unsigned(ss, value, radix);
}

#define GREEK_CAPTIAL_LETTER_SIGMA 0x3a3
#define GREEK_SMALL_LETTER_FINAL_SIGMA 0x3c2
#define GREEK_SMALL_LETTER_SIGMA 0x3c3

String String::set_case(CaseMode mode) const
{
    String res;
    res.m_string = mys::make_shared<CharVector>(*m_string.get());

    auto i = res.m_string->begin();
    int index = 0;
    while (i != res.m_string->end()) {
        Py_UCS4 mapped[3];
        int n;

        if (mode == CaseMode::CAPITALIZE && index == 0) {
            n = _PyUnicode_ToTitleFull(*i, mapped);
        }
        else if ((mode == CaseMode::LOWER || mode == CaseMode::CAPITALIZE)
                 && i->m_value == GREEK_CAPTIAL_LETTER_SIGMA) {
            uint32_t c;
            int j;

            // Lower case sigma at the end of a word is different than
            // in other positions, use the following regexp to detect this situation:
            // \p{cased}\p{case-ignorable}*U+03A3!(\p{case-ignorable}*\p{cased})

            for (j = index - 1; j >= 0; j--) {
                c = res.m_string->at(j).m_value;
                if (!_PyUnicode_IsCaseIgnorable(c)) {
                    break;
                }
            }
            bool final_sigma = j >= 0 && _PyUnicode_IsCased(c);
            if (final_sigma) {
                for (j = index + 1; j < res.m_string->size(); j++) {
                    c = res.m_string->at(j).m_value;
                    if (!_PyUnicode_IsCaseIgnorable(c))
                        break;
                }
                final_sigma = j == res.m_string->size() || !_PyUnicode_IsCased(c);
            }
            mapped[0] = final_sigma ? GREEK_SMALL_LETTER_FINAL_SIGMA : GREEK_SMALL_LETTER_SIGMA;
            n = 1;
        }
        else {
            switch (mode) {
              case CaseMode::LOWER:
              case CaseMode::CAPITALIZE:
                  n = _PyUnicode_ToLowerFull(*i, mapped);
                  break;
              case CaseMode::UPPER:
                  n = _PyUnicode_ToUpperFull(*i, mapped);
                  break;
              case CaseMode::FOLD:
                  n = _PyUnicode_ToFoldedFull(*i, mapped);
                  break;
            }
        }

        if (n == 1) {
            *i = mapped[0];
            ++i;
            index += 1;
        }
        else {
            CharVector vmapped;
            vmapped.resize(n);
            for (int j = 0; j < n; ++j)  {
                vmapped[j] = mapped[j];
            }

            i = res.m_string->erase(i);
            auto j = res.m_string->insert(i, vmapped.begin(), vmapped.end());
            i = j + vmapped.size();
            index += vmapped.size();
        }
    }

    return res;
}

String String::upper() const
{
    return set_case(CaseMode::UPPER);
}

String String::capitalize() const
{
    return set_case(CaseMode::CAPITALIZE);
}

String String::lower() const
{
    return set_case(CaseMode::LOWER);
}

String String::casefold() const
{
    return set_case(CaseMode::FOLD);
}

Bool String::starts_with(const String& value) const
{
    int value_length = value.__len__();

    if (value_length > m_string->size()) {
        return false;
    }

    for (u64 i = 0; i < value_length; i++) {
        if ((*m_string)[i] != (*value.m_string)[i]) {
            return false;
        }
    }

    return true;
}

Bool String::ends_with(const String& value) const
{
    int value_length = value.__len__();
    int start = m_string->size() - value_length;

    if (start < 0) {
        return false;
    }

    for (u64 i = 0; i < value_length; i++) {
        if ((*m_string)[start + i] != (*value.m_string)[i]) {
            return false;
        }
    }

    return true;
}

int String::__len__() const
{
    return shared_ptr_not_none(m_string)->size();
}

String String::__str__()
{
    String res("");

    res.m_string->insert(res.m_string->end(),
                         shared_ptr_not_none(m_string)->begin(),
                         shared_ptr_not_none(m_string)->end());

    return res;
}

String String::get(std::optional<i64> _start, std::optional<i64> _end,
                   i64 step) const
{
    int size = m_string->size();
    int start;
    int end;

    if (step > 0) {
        start = _start.value_or(0);
        end = _end.value_or(size);
    }
    else {
        start = _start.value_or(size - 1);
        end = _end.value_or(-size - 1);
    }

    if (start < 0) {
        start = m_string->size() + start;
        if (start < 0) {
            start = (step < 0) ? -1 : 0;
        }
    }
    else if (start >= size) {
        start = (step < 0) ? size - 1 : size;
    }

    if (end < 0) {
        end = m_string->size() + end;
        if (end < 0) {
            end = (step < 0) ? -1 : 0;
        }
    }
    else if (end >= size) {
        end = (step < 0) ? size - 1 : size;
    }

    String res("");
    int i = start;

    if (step == 1) {
        res.m_string->resize(end - start);
        std::copy(m_string->begin() + start,
                  m_string->begin() + end,
                  res.m_string->begin());
    } else if (step > 0) {
        while (i < end) {
            res.append((*m_string)[i]);
            i += step;
        }
    } else {
        while (i > end) {
            res.append((*m_string)[i]);
            i += step;
        }
    }

    return res;
}

#if !defined(MYS_UNSAFE)

Char& String::get(i64 index) const
{
    if (index < 0) {
        index = m_string->size() + index;
    }

    if (index < 0 || index >= static_cast<i64>(m_string->size())) {
        print_traceback();
        std::cerr
            << "\nPanic(message=\"String index "
            << index
            << " is out of range.\")\n";
        abort();
    }

    return (*m_string)[index];
}

#endif

u8& Bytes::operator[](i64 index) const
{
    if (index < 0) {
        index = m_bytes->size() + index;
    }

#if !defined(MYS_UNSAFE)
    if (index < 0 || index >= static_cast<i64>(m_bytes->size())) {
        print_traceback();
        std::cerr
            << "\nPanic(message=\"Bytes index "
            << index
            << " is out of range.\")\n";
        abort();
    }
#endif

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
        mys::make_shared<ValueError>("too big")->__throw();
    }

    for (size_t i = 0; i < m_string->size(); i++) {
        buf[i] = (*m_string)[i].m_value;
    }

    buf[m_string->size()] = '\0';

    return atoi(&buf[0]);
}

f64 String::__float__() const
{
    f64 value = 0.0;
    bool negative = false;
    i32 exponent = 0;
    i32 ch;
    auto it = m_string->begin();
    auto it_end = m_string->end();

    if (it == it_end) {
        mys::make_shared<ValueError>("invalid literal for float")->__throw();
    }

    if (*it == Char('-')) {
        negative = true;
        it++;
    }

    if (it == it_end) {
        mys::make_shared<ValueError>("invalid literal for float")->__throw();
    }

    while (it != it_end) {
        ch = *it++;

        if (!isdigit(ch)) {
            break;
        }

        value = value * 10.0 + (ch - '0');
    }

    if (ch == '.') {
        while (it != it_end) {
            ch = *it++;

            if (!isdigit(ch)) {
                break;
            }

            value = value * 10.0 + (ch - '0');
            exponent--;
        }
    }

    if (ch == 'e' || ch == 'E') {
        int sign = 1;
        int i = 0;

        if (it == it_end) {
            mys::make_shared<ValueError>("invalid literal for float")->__throw();
        }

        ch = *it++;

        if (ch == '+') {
            if (it == it_end) {
                mys::make_shared<ValueError>("invalid literal for float")->__throw();
            }

            ch = *it++;
        } else if (ch == '-') {
            if (it == it_end) {
                mys::make_shared<ValueError>("invalid literal for float")->__throw();
            }

            ch = *it++;
            sign = -1;
        }

        while (isdigit(ch)) {
            i = i * 10 + (ch - '0');

            if (it == it_end) {
                break;
            }

            ch = *it++;
        }

        exponent += i * sign;
    }

    if ((it != it_end) || ((ch != '.') && !isdigit(ch))) {
        mys::make_shared<ValueError>("invalid literal for float")->__throw();
    }

    while (exponent > 0) {
        value *= 10.0;
        exponent--;
    }

    while (exponent < 0) {
        value *= 0.1;
        exponent++;
    }

    if (negative) {
        value *= -1.0;
    }

    return value;
}

String input(String prompt)
{
    std::string value;

    std::cout << PrintString(prompt) << std::flush;
    getline(std::cin, value);

    return String(value);
}

String String::join(const mys::shared_ptr<List<String>>& list) const
{
    String res("");
    size_t j = 0;

    for (const auto &i : list->m_list) {
        res.append(i);
        if (j < list->m_list.size() - 1) {
            res.append(*this);
        }
        ++j;
    }

    return res;
}

i64 String::find(const Char& sub, std::optional<i64> _start, std::optional<i64> _end) const
{
    return find(String(sub), _start, _end, false);
}

i64 String::find(const String& sub, std::optional<i64> _start, std::optional<i64> _end) const
{
    return find(sub, _start, _end, false);
}

i64 String::find_reverse(const Char& sub, std::optional<i64> _start, std::optional<i64> _end) const
{
    return find(String(sub), _start, _end, true);
}

i64 String::find_reverse(const String& sub, std::optional<i64> _start, std::optional<i64> _end) const
{
    return find(sub, _start, _end, true);
}

i64 String::find(const String& sub, std::optional<i64> _start, std::optional<i64> _end,
                 bool reverse) const
{
    i64 res = -1;
    int size = m_string->size();
    i64 start = _start.value_or(0);
    i64 end = _end.value_or(size);

    if (start < 0) {
        start += m_string->size();
        if (start < 0) {
            start = 0;
        }
    }
    else if (start >= size) {
        return -1;
    }

    if (end < 0) {
        end += size;
        if (end < 0) {
            end = size;
        }
    }
    else if (end > size) {
        end = size;
    }

    if (end - start <= 0) {
        return -1;
    }

    if (reverse) {
        auto i_rbegin = m_string->rbegin() + size - end;
        auto i_rend = m_string->rbegin() + size - start;

        auto s = std::search(
            i_rbegin,
            i_rend,
            sub.m_string->begin(), sub.m_string->end());
        if (s == i_rend) {
            return -1;
        }
        return s - i_rbegin + end - 1;
    }
    else {
        auto i_begin = m_string->begin() + start;
        auto i_end = m_string->begin() + end;

        auto s = std::search(
            i_begin,
            i_end,
            sub.m_string->begin(), sub.m_string->end());
        if (s == i_end) {
            return -1;
        }
        return s - i_begin + start;
    }
}

mys::shared_ptr<List<String>> String::split(const String& separator) const
{
    auto list = mys::make_shared<List<String>>();

    if (separator.m_string) {
        if (separator.m_string->size() == 0) {
            mys::make_shared<ValueError>("empty separator")->__throw();
        }

        auto it = m_string->begin();

        while (it != m_string->end()) {
            auto it_sep = std::search(it,
                                      m_string->end(),
                                      separator.m_string->begin(),
                                      separator.m_string->end());

            String part("");
            part.m_string->resize(it_sep - it);
            std::copy(it, it_sep, part.m_string->begin());
            it = it_sep + separator.m_string->size();
            list->append(part);

            if (it_sep == m_string->end()) {
                break;
            }
        }

        if (it == m_string->end()) {
            list->append(String(""));
        }
    } else {
        list->append(*this);
    }

    return list;
}

String String::strip_left_right(std::optional<const String> chars, bool left, bool right) const
{
    String res;
    res.m_string = mys::make_shared<CharVector>(*m_string.get());

    // Characters to strip not given or given as None.
    bool whitespace = !chars.has_value() || !chars->m_string;

    // Return the same string if strip("").
    if (!whitespace && (chars->m_string->size() == 0)) {
        return *this;
    }

    if (left) {
        auto begin = res.m_string->begin();
        for (; begin != res.m_string->end(); ++begin) {
            if (whitespace) {
                if (!_PyUnicode_IsWhitespace(*begin)) {
                    break;
                }
            }
            else {
                auto i = std::find(chars->m_string->begin(), chars->m_string->end(), *begin);
                if (i == chars->m_string->end()) {
                    break;
                }
            }
        }
        res.m_string->erase(res.m_string->begin(), begin);
    }

    if (right) {
        auto end = res.m_string->rbegin();
        for (; end != res.m_string->rend(); ++end) {
            if (whitespace) {
                if (!_PyUnicode_IsWhitespace(*end)) {
                    break;
                }
            }
            else {
                auto i = std::find(chars->m_string->begin(), chars->m_string->end(), *end);
                if (i == chars->m_string->end()) {
                    break;
                }
            }
        }
        res.m_string->erase(end.base(), res.m_string->end());
    }
    return res;
}

String String::strip(std::optional<const String> chars) const
{
    return strip_left_right(chars, true, true);
}

String String::strip_left(std::optional<const String> chars) const
{
    return strip_left_right(chars, true, false);
}

String String::strip_right(std::optional<const String> chars) const
{
    return strip_left_right(chars, false, true);
}

SharedTuple<String, String, String> String::partition(const Char& chr) const
{
    auto i = std::find(m_string->begin(), m_string->end(), chr);
    if (i == m_string->end()) {
        return mys::make_shared<Tuple<String, String, String>>(*this, "", "");
    }

    String a("");
    a.m_string->insert(a.m_string->end(), m_string->begin(), i);
    String b("");
    b.append(chr);
    String c("");
    c.m_string->insert(c.m_string->end(), i + 1, m_string->end());

    return mys::make_shared<Tuple<String, String, String>>(a, b, c);
}

SharedTuple<String, String, String> String::partition(const String& str) const
{
    if (!str.m_string) {
        mys::make_shared<ValueError>("separator is None")->__throw();
    }

    auto i = std::search(m_string->begin(), m_string->end(),
                         str.m_string->begin(), str.m_string->end());
    if (i == m_string->end()) {
        return mys::make_shared<Tuple<String, String, String>>(*this, "", "");
    }

    String a("");
    a.m_string->insert(a.m_string->end(), m_string->begin(), i);
    String b("");
    b.m_string->insert(b.m_string->end(), i + str.__len__(), m_string->end());

    return mys::make_shared<Tuple<String, String, String>>(a, str, b);
}

String String::replace(const Char& old, const Char& _new) const
{
    String res;
    res.m_string = mys::make_shared<CharVector>(*m_string.get());

    for (auto& ch : *res.m_string) {
        if (ch.m_value == old.m_value) {
            ch.m_value = _new.m_value;
        }
    }

    return res;
}

String String::replace(const String& old, const String& _new) const
{
    String res;
    res.m_string = mys::make_shared<CharVector>(*m_string.get());

    auto i = res.m_string->begin();
    while (i != res.m_string->end()) {
        auto s = std::search(i, res.m_string->end(),
                             old.m_string->begin(), old.m_string->end());
        if (s == res.m_string->end()) {
            break;
        }
        i = res.m_string->erase(s, s + old.m_string->size());
        i = res.m_string->insert(i, _new.m_string->begin(), _new.m_string->end());
        i += _new.m_string->size();
    }

    return res;
}

String String::replace(const Regex& regex, const String& replacement, int flags) const
{
    return regex.replace(*this, replacement, flags);
}

Bool String::is_alpha() const
{
    if (m_string->size() == 0) {
        return false;
    }

    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsAlpha(c.m_value);
                       });
}

Bool String::is_digit() const
{
    if (m_string->size() == 0) {
        return false;
    }

    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsDigit(c.m_value);
                       });
}

Bool String::is_numeric() const
{
    if (m_string->size() == 0) {
        return false;
    }

    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsNumeric(c.m_value);
                       });
}

Bool String::is_space() const
{
    if (m_string->size() == 0) {
        return false;
    }

    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsWhitespace(c.m_value);
                       });
}

Bool Char::is_digit() const
{
    return _PyUnicode_IsDigit(m_value);
}

Bool Char::is_numeric() const
{
    return _PyUnicode_IsNumeric(m_value);
}

Bool Char::is_alpha() const
{
    return _PyUnicode_IsAlpha(m_value);
}

Bool Char::is_space() const
{
    return _PyUnicode_IsWhitespace(m_value);
}

RegexMatch String::match(const Regex& regex) const
{
    return regex.match(*this);
}

mys::shared_ptr<List<String>> String::split() const
{
    return Regex("\\s+", "").split(*this);
}

mys::shared_ptr<List<String>> String::split(const Regex& regex) const
{
    return regex.split(*this);
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

String string_with_quotes(const String& value)
{
    if (value.m_string) {
        String res("\"");

        res.m_string->insert(res.m_string->end(),
                             value.m_string->begin(),
                             value.m_string->end());
        res += "\"";

        return res;
    } else {
        return String("None");
    }
}

String regexmatch_str(const RegexMatch& value)
{
    if (value.m_match_data) {
      return String("xxx");
    } else {
      return String("None");
    }
}

String regex_str(const Regex& value)
{
    if (value.m_compiled) {
      return String("xxx");
    } else {
      return String("None");
    }
}

std::ostream& operator<<(std::ostream& os, const RegexMatch& obj)
{
    if (obj.m_match_data) {
        os << "RegexMatch(span=" << obj.span(0) << ", "
           << "match=" << obj.group(0) << ")";
    }
    else {
        os << "None";
    }

    return os;
}

void Object::__format__(std::ostream& os) const
{
}

String Object::__str__()
{
    return String("Object()");
}

void AssertionError::__throw()
{
    throw __AssertionError(mys::shared_ptr<AssertionError>(this));
}

String AssertionError::__str__()
{
    std::stringstream ss;
    ss << "AssertionError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void IndexError::__throw()
{
    throw __IndexError(mys::shared_ptr<IndexError>(this));
}

String IndexError::__str__()
{
    std::stringstream ss;
    ss << "IndexError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void InterruptError::__throw()
{
    throw __InterruptError(mys::shared_ptr<InterruptError>(this));
}

String InterruptError::__str__()
{
    return String("InterruptError()");
}

void KeyError::__throw()
{
    throw __KeyError(mys::shared_ptr<KeyError>(this));
}

String KeyError::__str__()
{
    std::stringstream ss;
    ss << "KeyError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void NotImplementedError::__throw()
{
    throw __NotImplementedError(mys::shared_ptr<NotImplementedError>(this));
}

String NotImplementedError::__str__()
{
    std::stringstream ss;
    ss << "NotImplementedError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void SystemExitError::__throw()
{
    throw __SystemExitError(mys::shared_ptr<SystemExitError>(this));
}

String SystemExitError::__str__()
{
    std::stringstream ss;
    ss << "SystemExitError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void UnreachableError::__throw()
{
    throw __UnreachableError(mys::shared_ptr<UnreachableError>(this));
}

String UnreachableError::__str__()
{
    std::stringstream ss;
    ss << "UnreachableError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void ValueError::__throw()
{
    throw __ValueError(mys::shared_ptr<ValueError>(this));
}

String ValueError::__str__()
{
    std::stringstream ss;
    ss << "ValueError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

int RegexMatch::group_index(const String& name) const
{
    std::vector<PCRE2_UCHAR> name_sptr;
    int index;

    name_sptr.resize(name.m_string->size() + 1);
    std::copy(name.m_string->begin(), name.m_string->end(), name_sptr.begin());
    name_sptr[name.m_string->size()] = 0;

    index = pcre2_substring_number_from_name(m_code.get(), name_sptr.data());
    if (index == PCRE2_ERROR_NOSUBSTRING) {
        mys::make_shared<IndexError>("no such group")->__throw();
    }
    else if (index < 0) {
        mys::make_shared<IndexError>(Regex::get_error(index))->__throw();
    }

    return index;
}

String RegexMatch::group(int index) const
{
    PCRE2_UCHAR *buffer;
    PCRE2_SIZE length;
    int error;

    error = pcre2_substring_get_bynumber(m_match_data.get(), index, &buffer, &length);
    if (error == PCRE2_ERROR_NOSUBSTRING) {
        print_traceback();
        std::cerr << "\nPanic(message=\"No such regex group.\")\n";
        abort();
    }
    else if (error == PCRE2_ERROR_UNSET) {
        return String(nullptr);
    }
    else if (error != 0) {
        mys::make_shared<IndexError>(Regex::get_error(error))->__throw();
    }

    String res("");
    res.m_string->resize(length);
    std::copy(buffer, buffer + length, res.m_string->begin());

    pcre2_substring_free(buffer);

    return res;
}

SharedDict<String, String> RegexMatch::group_dict() const
{
    auto res = mys::make_shared<Dict<String, String>>();
    int num = get_num_matches();
    uint32_t name_count;
    PCRE2_SPTR name_table;
    PCRE2_SPTR ptr;
    uint32_t name_entry_size;
    uint32_t i;

    pcre2_pattern_info(m_code.get(), PCRE2_INFO_NAMECOUNT,
                       &name_count);
    pcre2_pattern_info(m_code.get(), PCRE2_INFO_NAMETABLE,
                       &name_table);
    pcre2_pattern_info(m_code.get(), PCRE2_INFO_NAMEENTRYSIZE,
                       &name_entry_size);

    for (ptr = name_table, i = 0; i < name_count; ++i, ptr += name_entry_size) {
        int index = ptr[0];
        String name("");
        name.m_string->reserve(name_entry_size - 1);
        for (int c = 0; c < name_entry_size; ++c) {
            if (ptr[1 + c] == 0) {
                break;
            }
            name.append(Char(ptr[1 + c]));
        }
        res->m_map[name] = group(index);
    }

    return res;
}

SharedList<String> RegexMatch::groups() const
{
    auto res = mys::make_shared<List<String>>();
    int num = get_num_matches();

    res->m_list.reserve(num - 1);
    for (int i = 1; i < num; ++i) {
        res->m_list.push_back(group(i));
    }

    return res;
}

SharedTuple<i64, i64> RegexMatch::span(int index) const
{
    PCRE2_SIZE *ovector = pcre2_get_ovector_pointer(m_match_data.get());
    uint32_t num_match = get_num_matches();

    if (index >= num_match) {
        mys::make_shared<IndexError>("no such group")->__throw();
    }

    return mys::make_shared<Tuple<i64, i64>>(
        ovector[index * 2], ovector[index * 2 + 1]);
}

String Regex::get_error(int error)
{
    String res("");
    std::vector<PCRE2_UCHAR> buffer;
    int length;

    buffer.resize(1024);

    length = pcre2_get_error_message(error, buffer.data(), buffer.size());
    if (length > 0) {
        res.m_string->resize(length);
        std::copy(buffer.begin(), buffer.begin() + length, res.m_string->begin());
    }
    return res;
}

Regex::Regex(const String& regex, const String& flags)
{
    int pcreError;
    PCRE2_SIZE pcreErrorOffset;
    PCRE2_SPTR regex_sptr = reinterpret_cast<PCRE2_SPTR>(regex.m_string->data());
    PCRE2_SIZE length = regex.m_string->size();
    uint32_t options = PCRE2_UTF | PCRE2_UCP;
    PCRE2_UCHAR empty[] = { 0 };

    for (auto i : *flags.m_string) {
        switch (i.m_value) {
          case 'i':
              options |= PCRE2_CASELESS;
              break;
          case 'm':
              options |= PCRE2_MULTILINE;
              break;
          case 'x':
              options |= PCRE2_EXTENDED;
              break;
          case 's':
              options |= PCRE2_DOTALL;
              break;
          default:
              break;
        }
    }

    if (length == 0) {
        regex_sptr = empty;
    }

    pcre2_code *compiled_p = pcre2_compile(regex_sptr,
                                           length,
                                           options,
                                           &pcreError,
                                           &pcreErrorOffset,
                                           NULL);

    if (compiled_p == NULL) {
        PCRE2_UCHAR buffer[128];
        int l = pcre2_get_error_message(pcreError, buffer, sizeof(buffer));
        String message("");
        for (int i = 0; i < l; i++) {
            message += Char((char)buffer[i]);
        }
        message += " at offset ";
        message += String((u64)pcreErrorOffset);
        mys::make_shared<ValueError>(message)->__throw();
    }

    m_compiled.reset(compiled_p,
                     [](pcre2_code *code) {
                         pcre2_code_free(code);
                     });
}

RegexMatch Regex::match(const String& string) const
{
    std::shared_ptr<pcre2_match_data> match_data;
    PCRE2_SPTR string_sptr = reinterpret_cast<PCRE2_SPTR>(string.m_string->data());
    PCRE2_SIZE length = string.m_string->size();
    PCRE2_UCHAR empty[] = { 0 };
    int error;

    if (length == 0) {
        string_sptr = empty;
    }

    match_data.reset(pcre2_match_data_create_from_pattern(m_compiled.get(), NULL),
                     [](pcre2_match_data *data) {
                         pcre2_match_data_free(data);
                     });

    error = pcre2_match(m_compiled.get(), string_sptr, length, 0, 0,
                        match_data.get(), NULL);
    if (error == PCRE2_ERROR_NOMATCH) {
        return RegexMatch();
    }
    else if (error < 0) {
        mys::make_shared<IndexError>(get_error(error))->__throw();
    }

    return RegexMatch(match_data, m_compiled, string);
}

String Regex::replace(const String& subject, const String& replacement, int flags) const
{
    PCRE2_SPTR subject_sptr = reinterpret_cast<PCRE2_SPTR>(subject.m_string->data());
    PCRE2_SIZE subject_length = subject.m_string->size();
    PCRE2_SPTR replacement_sptr = reinterpret_cast<PCRE2_SPTR>(replacement.m_string->data());
    PCRE2_SIZE replacement_length = replacement.m_string->size();
    auto pcre_output = std::vector<PCRE2_UCHAR>();
    PCRE2_SIZE out_length = 1024;
    int error;
    uint32_t options = PCRE2_SUBSTITUTE_OVERFLOW_LENGTH;
    int retry = 2;
    PCRE2_UCHAR empty[] = { 0 };

    if (subject_length == 0) {
        subject_sptr = empty;
    }

    if (replacement_length == 0) {
        replacement_sptr = empty;
    }

    if (flags == 0) {
        options |= PCRE2_SUBSTITUTE_GLOBAL;
    }

    while (retry--) {
        pcre_output.resize(out_length);
        error = pcre2_substitute(m_compiled.get(),
                                 subject_sptr, subject_length,
                                 0, options, NULL, NULL,
                                 replacement_sptr, replacement_length,
                                 pcre_output.data(), &out_length);
        if (error != PCRE2_ERROR_NOMEMORY) {
            break;
        }
    }

    if (error < 0) {
        mys::make_shared<IndexError>(get_error(error))->__throw();
    }

    String res("");
    for (int i = 0; i < out_length; ++i) {
        res.append(Char(pcre_output[i]));
    }

    return res;
}

mys::shared_ptr<List<String>> Regex::split(const String& string) const
{
    String split(string);
    List<String> res;
    while (true) {
        RegexMatch m = match(split);
        if (m.m_match_data && m.get_num_matches() > 0) {
            auto [start, end] = m.span(0)->m_tuple;
            res.append(split.get(0, start, 1));
            split = split.get(end, split.__len__(), 1);
        }
        else {
            res.append(split);
            break;
        }
    }
    return mys::make_shared<List<String>>(res);
}

Bytes::Bytes(u64 size)
{
    m_bytes = mys::make_shared<std::vector<u8>>();
    m_bytes->resize(size);
}

String Bytes::to_hex() const
{
    String hex("");
    char buf[3];

    for (auto v : *m_bytes) {
        sprintf(buf, "%02x", v);
        hex.m_string->push_back(buf[0]);
        hex.m_string->push_back(buf[1]);
    }

    return hex;
}

i64 Bytes::find(const Bytes& needle,
                std::optional<i64> _start,
                std::optional<i64> _end) const
{
    i64 res = -1;
    int size = m_bytes->size();
    i64 start = _start.value_or(0);
    i64 end = _end.value_or(size);

    if (start < 0) {
        start += m_bytes->size();

        if (start < 0) {
            start = 0;
        }
    } else if (start >= size) {
        return -1;
    }

    if (end < 0) {
        end += size;

        if (end < 0) {
            end = size;
        }
    } else if (end > size) {
        end = size;
    }

    if (end - start <= 0) {
        return -1;
    }

    auto i_begin = m_bytes->begin() + start;
    auto i_end = m_bytes->begin() + end;

    auto s = std::search(i_begin,
                         i_end,
                         needle.m_bytes->begin(),
                         needle.m_bytes->end());

    if (s == i_end) {
        return -1;
    }

    return s - i_begin + start;
}

Error::Error()
{
#if defined(MYS_TRACEBACK)
    TracebackEntry *item_p;
    TracebackEntryInfo *entry_info_p;

    item_p = traceback_bottom_p->next_p;

    while (true) {
        m_traceback.push_back(*item_p);

        if (item_p == traceback_top_p) {
            break;
        }

        item_p = item_p->next_p;
    }
#endif
}

String executable()
{
    static String path("");

    if (path.m_string->size() == 0) {
        int length = wai_getExecutablePath(NULL, 0, NULL);
        char *path_p = (char *)malloc(length + 1);
        wai_getExecutablePath(path_p, length, NULL);
        path_p[length] = '\0';
        path += path_p;
        path += "-assets/";
        free(path_p);
    }

    return path;
}

String assets(const char *package_p)
{
    return executable() + package_p;
}

}

#if defined(MYS_APPLICATION) || defined(MYS_TEST)

int main(int argc, const char *argv[])
{
    return mys::main(argc, argv);
}

#endif
