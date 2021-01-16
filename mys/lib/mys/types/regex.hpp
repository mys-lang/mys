#pragma once

#define PCRE2_CODE_UNIT_WIDTH 32
#include <pcre2.h>

#include "string.hpp"

#include "../errors/index.hpp"

class Regex;

class RegexMatch final
{
private:
    int group_index(const String& name) const;

public:
    std::shared_ptr<pcre2_match_data> m_match_data;
    std::shared_ptr<pcre2_code> m_code;
    String m_string;

    // Must keep references to string and compiled regexp
    // as match_data use them internally
    RegexMatch(std::shared_ptr<pcre2_match_data> match_data,
               std::shared_ptr<pcre2_code> code,
               const String& string)
        : m_match_data(match_data),
          m_code(code),
          m_string(string)
    {
    }

    RegexMatch(void *)
        : m_match_data(nullptr)
    {}

    RegexMatch()
        : m_match_data(nullptr)
    {}

    uint32_t get_num_matches() const
    {
        return pcre2_get_ovector_count(m_match_data.get());
    }

    SharedTuple<i64, i64> span(int index) const;
    SharedTuple<i64, i64> span(const String& name) const
    {
        return span(group_index(name));
    }

    int start(int index) const
    {
        auto [start, end] = span(index)->m_tuple;
        return start;
    }

    int start(const String& name) const
    {
        return start(group_index(name));
    }

    int end(int index) const
    {
        auto [start, end] = span(index)->m_tuple;
        return end;
    }

    int end(const String& name) const
    {
        return end(group_index(name));
    }

    String group(int index) const;
    String group(const String& name) const
    {
        return group(group_index(name));
    }

    SharedDict<String, String> group_dict() const;
    SharedList<String> groups() const;
};

class Regex final
{
public:
    std::shared_ptr<pcre2_code> m_compiled;

    static String get_error(int error);
    Regex(const String& regex, const String& flags);
    RegexMatch match(const String& string) const;
    String replace(const String& subject, const String& replacement, int flags = 0) const;
    std::shared_ptr<List<String>> split(const String& string) const;

};

std::ostream& operator<<(std::ostream& os, const RegexMatch& obj);

const Regex& regex_not_none(const Regex& obj);
const RegexMatch& regexmatch_not_none(const RegexMatch& obj);
String regexmatch_str(const RegexMatch& value);
