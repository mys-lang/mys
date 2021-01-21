#include <iomanip>
#include "mys.hpp"

#include "unicodectype.cpp"
#include "fiber.cpp"

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

extern void __application_init(void);

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

    core_fiber::init();

    try {
        __application_init();
    } catch (const __Error &e) {
        std::cout << PrintString(e.m_error->__str__()) << std::endl;
        return 1;
    }

    test_p = tests_head_p;

    while (test_p != NULL) {
        auto begin = steady_clock::now();

        try {
            test_p->m_func();
            result_p = COLOR(GREEN, " ✔");
            passed++;
        } catch (const __Error &e) {
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
    int res = 1;

    try {
        __application_init();
        package_main(argc, argv);
        res = 0;
    } catch (const __SystemExitError &e) {
        // This exception should probably contain the exit code.
        auto error = std::dynamic_pointer_cast<SystemExitError>(e.m_error);

        if (error->m_message.m_string) {
            std::cerr << e.m_error << std::endl;
        } else {
            res = 0;
        }
    } catch (const __Error &e) {
        std::cerr << e.m_error << std::endl;
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
        std::make_shared<NoneError>("object is None")->__throw();
    }

    return obj;
}

const Regex& regex_not_none(const Regex& obj)
{
    if (!obj.m_compiled) {
        std::make_shared<NoneError>("object is None")->__throw();
    }

    return obj;
}

const RegexMatch& regexmatch_not_none(const RegexMatch& obj)
{
    if (!obj.m_match_data) {
        std::make_shared<NoneError>("object is None")->__throw();
    }

    return obj;
}

const Bytes& bytes_not_none(const Bytes& obj)
{
    if (!obj.m_bytes) {
        std::make_shared<NoneError>("object is None")->__throw();
    }

    return obj;
}

std::ostream& operator<<(std::ostream& os, Object& obj)
{
    os << PrintString(obj.__str__());

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
    String res("");
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
    set_case(CaseMode::UPPER);
}

String String::to_upper() const
{
    String res("");
    res.m_string = std::make_shared<std::vector<Char>>(*m_string);
    res.upper();
    return res;
}

void String::capitalize() const
{
    set_case(CaseMode::CAPITALIZE);
}

String String::to_capitalize() const
{
    String res("");
    res.m_string = std::make_shared<std::vector<Char>>(*m_string);
    res.capitalize();
    return res;
}

#define GREEK_CAPTIAL_LETTER_SIGMA 0x3a3
#define GREEK_SMALL_LETTER_FINAL_SIGMA 0x3c2
#define GREEK_SMALL_LETTER_SIGMA 0x3c3

void String::set_case(CaseMode mode) const
{
    auto i = m_string->begin();
    int index = 0;
    while (i != m_string->end()) {
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
            // in other positions, the following code implements the following
            // regexp to detect this situation:
            // \p{cased}\p{case-ignorable}*U+03A3!(\p{case-ignorable}*\p{cased})

            for (j = index - 1; j >= 0; j--) {
                c = m_string->at(j).m_value;
                if (!_PyUnicode_IsCaseIgnorable(c)) {
                    break;
                }
            }
            bool final_sigma = j >= 0 && _PyUnicode_IsCased(c);
            if (final_sigma) {
                for (j = index + 1; j < m_string->size(); j++) {
                    c = m_string->at(j).m_value;
                    if (!_PyUnicode_IsCaseIgnorable(c))
                        break;
                }
                final_sigma = j == m_string->size() || !_PyUnicode_IsCased(c);
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
            std::vector<Char> vmapped;
            vmapped.resize(n);
            for (int j = 0; j < n; ++j)  {
                vmapped[j] = mapped[j];
            }

            i = m_string->erase(i);
            auto j = m_string->insert(i, vmapped.begin(), vmapped.end());
            i = j + vmapped.size();
            index += vmapped.size();
        }
    }
}

void String::lower() const
{
    set_case(CaseMode::LOWER);
}

String String::to_lower() const
{
    String res("");
    res.m_string = std::make_shared<std::vector<Char>>(*m_string);
    res.lower();
    return res;
}

void String::casefold() const
{
    set_case(CaseMode::FOLD);
}

String String::to_casefold() const
{
    String res("");
    res.m_string = std::make_shared<std::vector<Char>>(*m_string);
    res.casefold();
    return res;
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
    while (step > 0 ? i < end : i > end) {
        res.m_string->push_back(m_string->at(i));
        i += step;
    }
    return res;
}

Char& String::get(i64 index) const
{
    if (index < 0) {
        index = m_string->size() + index;
    }

    if (index < 0 || index >= static_cast<i64>(m_string->size())) {
        std::make_shared<IndexError>("string index out of range")->__throw();
    }

    return (*m_string)[index];
}

u8& Bytes::operator[](i64 index) const
{
    if (index < 0) {
        index = m_bytes->size() + index;
    }

    if (index < 0 || index >= static_cast<i64>(m_bytes->size())) {
        std::make_shared<IndexError>("bytes index out of range")->__throw();
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
        std::make_shared<ValueError>("too big")->__throw();
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

std::shared_ptr<List<String>> String::split(const String& separator) const
{
    auto res = std::make_shared<List<String>>();
    auto i = m_string->begin();
    while (i != m_string->end()) {
        auto s = std::search(i, m_string->end(),
                             separator.m_string->begin(), separator.m_string->end());
        String r("");
        r.m_string->resize(separator.m_string->size());
        std::copy(i, s, r.m_string->begin());
        i = s + separator.m_string->size();
        res->append(r);
        if (s == m_string->end()) {
            break;
        }
    }
    return res;
}

void String::strip_left_right(std::optional<const String> chars, bool left, bool right) const
{
    bool whitespace = !chars.has_value();

    if (left) {
        auto start = m_string->begin();
        for (; start != m_string->end(); ++start) {
            if (whitespace) {
                if (!_PyUnicode_IsWhitespace(*start)) {
                    break;
                }
            }
            else {
                auto i = std::find(chars->m_string->begin(), chars->m_string->end(), *start);
                if (i == chars->m_string->end()) {
                    break;
                }
            }
        }
        m_string->erase(m_string->begin(), start);
    }

    if (right) {
        auto end = m_string->rbegin();
        for (; end != m_string->rend(); ++end) {
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
        m_string->erase(end.base(), m_string->end());
    }
}

void String::strip(std::optional<const String> chars) const
{
    strip_left_right(chars, true, true);
}

void String::strip_left(std::optional<const String> chars) const
{
    strip_left_right(chars, true, false);
}

void String::strip_right(std::optional<const String> chars) const
{
    strip_left_right(chars, false, true);
}

String String::cut(const Char& chr) const
{
    auto i = std::find(m_string->begin(), m_string->end(), chr);
    if (i == m_string->end()) {
        return nullptr;
    }

    String res = String("");
    res.m_string->resize(i - m_string->begin());
    std::copy(m_string->begin(), i, res.m_string->begin());

    m_string->erase(m_string->begin(), i + 1);

    return res;
}

void String::replace(const Char& old, const Char& _new) const
{
    for (auto& ch : *m_string) {
        if (ch.m_value == old.m_value) {
            ch.m_value = _new.m_value;
        }
    }
}

void String::replace(const String& old, const String& _new) const
{
    auto i = m_string->begin();
    while (i != m_string->end()) {
        auto s = std::search(i, m_string->end(),
                             old.m_string->begin(), old.m_string->end());
        if (s == m_string->end()) {
            break;
        }
        i = m_string->erase(s, s + old.m_string->size());
        i = m_string->insert(i, _new.m_string->begin(), _new.m_string->end());
        i += _new.m_string->size();
    }
}

void String::replace(const Regex& regex, const String& replacement, int flags) const
{
    String res = regex.replace(*this, replacement, flags);

    m_string->resize(res.m_string->size());
    std::copy(res.m_string->begin(), res.m_string->end(), m_string->begin());
}

Bool String::is_alpha() const
{
    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsAlpha(c.m_value);
                       });
}

Bool String::is_digit() const
{
    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsDigit(c.m_value);
                       });
}

Bool String::is_numeric() const
{
    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsNumeric(c.m_value);
                       });
}

Bool String::is_space() const
{
    return std::all_of(m_string->begin(), m_string->end(),
                       [](Char& c) {
                           return _PyUnicode_IsWhitespace(c.m_value);
                       });
}

RegexMatch String::match(const Regex& regex) const
{
    return regex.match(*this);
}

std::shared_ptr<List<String>> String::split(const Regex& regex) const
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
    throw __AssertionError(shared_from_this());
}

String AssertionError::__str__()
{
    std::stringstream ss;
    ss << "AssertionError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void IndexError::__throw()
{
    throw __IndexError(shared_from_this());
}

String IndexError::__str__()
{
    std::stringstream ss;
    ss << "IndexError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void KeyError::__throw()
{
    throw __KeyError(shared_from_this());
}

String KeyError::__str__()
{
    std::stringstream ss;
    ss << "KeyError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void NoneError::__throw()
{
    throw __NoneError(shared_from_this());
}

String NoneError::__str__()
{
    std::stringstream ss;
    ss << "NoneError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void NotImplementedError::__throw()
{
    throw __NotImplementedError(shared_from_this());
}

String NotImplementedError::__str__()
{
    std::stringstream ss;
    ss << "NotImplementedError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void SystemExitError::__throw()
{
    throw __SystemExitError(shared_from_this());
}

String SystemExitError::__str__()
{
    std::stringstream ss;
    ss << "SystemExitError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void UnreachableError::__throw()
{
    throw __UnreachableError(shared_from_this());
}

String UnreachableError::__str__()
{
    std::stringstream ss;
    ss << "UnreachableError(message=" << m_message << ")";
    return String(ss.str().c_str());
}

void ValueError::__throw()
{
    throw __ValueError(shared_from_this());
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
        std::make_shared<IndexError>("no such group")->__throw();
    }
    else if (index < 0) {
        std::make_shared<IndexError>(Regex::get_error(index))->__throw();
    }

    return index;
}

String RegexMatch::group(int index) const
{
    PCRE2_UCHAR *buffer;
    PCRE2_SIZE length;
    String res("");
    int error;

    error = pcre2_substring_get_bynumber(m_match_data.get(), index, &buffer, &length);
    if (error == PCRE2_ERROR_NOSUBSTRING) {
        std::make_shared<IndexError>("no such group")->__throw();
    }
    else if (error != 0) {
        std::make_shared<IndexError>(Regex::get_error(error))->__throw();
    }

    res.m_string->resize(length);
    std::copy(buffer, buffer + length, res.m_string->begin());

    pcre2_substring_free(buffer);

    return res;
}

SharedDict<String, String> RegexMatch::group_dict() const
{
    auto res = std::make_shared<Dict<String, String>>();
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
            name.m_string->push_back(ptr[1 + c]);
        }
        res->m_map[name] = group(index);
    }

    return res;
}

SharedList<String> RegexMatch::groups() const
{
    auto res = std::make_shared<List<String>>();
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
        std::make_shared<IndexError>("no such group")->__throw();
    }

    return std::make_shared<Tuple<i64, i64>>(
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
        std::copy(buffer.begin(), buffer.end(), res.m_string->begin());
    }
    return res;
}

Regex::Regex(const String& regex, const String& flags)
{
    int pcreError;
    PCRE2_SIZE pcreErrorOffset;
    PCRE2_SPTR regex_sptr = reinterpret_cast<PCRE2_SPTR>(regex.m_string->data());
    uint32_t options = PCRE2_UTF | PCRE2_UCP;
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

    m_compiled.reset(pcre2_compile(regex_sptr, regex.m_string->size(), options,
                                   &pcreError, &pcreErrorOffset, NULL),
                     [](pcre2_code *code) {
                         pcre2_code_free(code);
                     });
}

RegexMatch Regex::match(const String& string) const
{
    std::shared_ptr<pcre2_match_data> match_data;
    PCRE2_SPTR string_sptr = reinterpret_cast<PCRE2_SPTR>(string.m_string->data());
    int error;

    match_data.reset(pcre2_match_data_create_from_pattern(m_compiled.get(), NULL),
                     [](pcre2_match_data *data) {
                         pcre2_match_data_free(data);
                     });
    error = pcre2_match(m_compiled.get(), string_sptr, string.m_string->size(),
                        0, 0, match_data.get(), NULL);
    if (error == PCRE2_ERROR_NOMATCH) {
        return RegexMatch();
    }
    else if (error < 0) {
        std::make_shared<IndexError>(get_error(error))->__throw();
    }

    return RegexMatch(match_data, m_compiled, string);
}

String Regex::replace(const String& subject, const String& replacement, int flags) const
{
    PCRE2_SPTR subject_sptr = reinterpret_cast<PCRE2_SPTR>(subject.m_string->data());
    PCRE2_SPTR replacement_sptr = reinterpret_cast<PCRE2_SPTR>(replacement.m_string->data());
    auto pcre_output = std::vector<PCRE2_UCHAR>();
    PCRE2_SIZE out_length = 1024;
    int error;
    uint32_t options = PCRE2_SUBSTITUTE_OVERFLOW_LENGTH;
    int retry = 2;

    if (flags == 1) {
        options |= PCRE2_SUBSTITUTE_GLOBAL;
    }

    while (retry--) {
        pcre_output.resize(out_length);
        error = pcre2_substitute(m_compiled.get(), subject_sptr, subject.m_string->size(),
                                 0, options, NULL, NULL, replacement_sptr, replacement.m_string->size(),
                                 pcre_output.data(), &out_length);
        if (error != PCRE2_ERROR_NOMEMORY) {
            break;
        }
    }

    if (error < 0) {
        std::make_shared<IndexError>(get_error(error))->__throw();
    }

    String res("");
    for (int i = 0; i < out_length; ++i) {
        res.m_string->push_back(pcre_output[i]);
    }

    return res;
}

std::shared_ptr<List<String>> Regex::split(const String& string) const
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
    return std::make_shared<List<String>>(res);
}
