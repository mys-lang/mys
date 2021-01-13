#pragma once

#define PCRE2_CODE_UNIT_WIDTH 32
#include <pcre2.h>

#include "string.hpp"

#include "../errors/index.hpp"

class RegexMatch final
{
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

    std::tuple<int, int> get_start_end(int index) const
    {
        PCRE2_SIZE *ovector = pcre2_get_ovector_pointer(m_match_data.get());
        uint32_t num_match = get_num_matches();

        if (index >= num_match) {
            std::make_shared<IndexError>("no such group")->__throw();
        }

        return std::make_tuple(ovector[index * 2], ovector[index * 2 + 1]);
    }

    String group(const String& name) const
    {
        PCRE2_UCHAR *buffer;
        PCRE2_SIZE length;
        String res("");
        int error;
        std::vector<PCRE2_UCHAR> name_sptr;

        name_sptr.resize(name.m_string->size() + 1);
        std::copy(name.m_string->begin(), name.m_string->end(), name_sptr.begin());
        name_sptr[name.m_string->size()] = 0;

        error = pcre2_substring_get_byname(m_match_data.get(), name_sptr.data(), &buffer, &length);
        if (error == PCRE2_ERROR_NOSUBSTRING) {
            std::make_shared<IndexError>("no such group")->__throw();
        }
        else if (error != 0) {
            std::make_shared<IndexError>("xxx1")->__throw();
        }

        for (size_t i = 0; i < length; i++) {
            res.m_string->push_back(buffer[i]);
        }

        pcre2_substring_free(buffer);

        return res;
    }

    String group(int index) const
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
            std::make_shared<IndexError>("xxx2")->__throw();
        }

        for (size_t i = 0; i < length; i++) {
            res.m_string->push_back(buffer[i]);
        }

        pcre2_substring_free(buffer);

        return res;
    }
};

class Regex final
{
public:
    std::shared_ptr<pcre2_code> m_compiled;

    Regex(const String& regex, const String& flags)
    {
        int pcreError;
        PCRE2_SIZE pcreErrorOffset;
        PCRE2_SPTR regex_sptr = reinterpret_cast<PCRE2_SPTR>(regex.m_string->data());
        uint32_t options = PCRE2_UTF;
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

    RegexMatch match(const String& string) const
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
            std::make_shared<IndexError>("xxx3")->__throw();
        }

        return RegexMatch(match_data, m_compiled, string);
    }

    String replace(const String& subject, const String& replacement, int flags = 0) const
    {
        PCRE2_SPTR subject_sptr = reinterpret_cast<PCRE2_SPTR>(subject.m_string->data());
        PCRE2_SPTR replacement_sptr = reinterpret_cast<PCRE2_SPTR>(replacement.m_string->data());
        auto pcre_output = std::vector<PCRE2_UCHAR>();
        PCRE2_SIZE out_length = 8;
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
            std::make_shared<IndexError>("xxx4")->__throw();
        }

        String res("");
        for (int i = 0; i < out_length; ++i) {
            res.m_string->push_back(pcre_output[i]);
        }

        return res;
    }
};

std::ostream& operator<<(std::ostream& os, const RegexMatch& obj);

const Regex& regex_not_none(const Regex& obj);
const RegexMatch& regexmatch_not_none(const RegexMatch& obj);
String regexmatch_str(const RegexMatch& value);
