#pragma once

#include "../common.hpp"
#include "../errors/value.hpp"

/* slice(), enumerate() and range() used in for loops. */

namespace mys {

struct Slice {
    i64 m_begin;
    i64 m_end;
    i64 m_step;

    Slice(i64 begin, i64 end, i64 step, i64 length) {
        if (step == 0) {
            mys::make_shared<ValueError>("slice step can't be zero")->__throw();
        }

        if (begin < 0) {
            begin += length;

            if (begin < 0) {
                begin = 0;
            }
        }

        if (end < 0) {
            end += length;

            if (end < 0) {
                end = 0;
            }
        }

        if (((begin < end) && (step < 0))
            || ((begin > end) && (step > 0))
            || (begin == end)) {
            begin = 0;
            end = 0;
            step = 1;
        }

        m_begin = begin;
        m_end = end;
        m_step = step;
    }

    i64 length() {
        if (m_begin <= m_end) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

class OpenSlice {

public:
    i64 m_begin;

    OpenSlice(i64 begin) {
        if (begin < 0) {
            begin = 0;
        }

        m_begin = begin;
    }
};

template <typename T>
class Range {

public:
    T m_begin;
    T m_end;
    T m_step;
    T m_next;

    Range(T end) : m_begin(0), m_end(end), m_step(1) {
    }

    Range(T begin, T end) : m_begin(begin), m_end(end), m_step(1) {
    }

    Range(T begin, T end, T step) : m_begin(begin), m_end(end), m_step(step) {
    }

    void iter() {
        m_next = m_begin;
    }

    T next() {
        T next = m_next;
        m_next += m_step;
        return next;
    }

    void slice(Slice& slice) {
        T begin = (m_begin + slice.m_begin * m_step);

        if (begin > m_end) {
            begin = m_end;
        }

        m_begin = begin;
        T end = m_begin + slice.length() * slice.m_step;

        if (end > m_end) {
            end = m_end;
        }

        m_end = end;
        m_step *= slice.m_step;
    }

    void slice(OpenSlice& slice) {
        m_begin += (slice.m_begin * m_step);
    }

    void reversed() {
        T begin;
        T l;

        begin = m_begin;
        l = length();
        m_begin = begin + (l - 1) * m_step;
        m_end = m_begin - (l - 1) * m_step;

        if (m_step > 0) {
            m_end--;
        } else {
            m_end++;
        }

        m_step *= -1;
    }

    i64 length() {
        if (m_step > 0) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

template <typename T>
class Enumerate {

public:
    T m_begin;
    T m_end;
    T m_step;
    T m_next;

    Enumerate(T begin, T end) {
        m_begin = begin;
        m_end = begin + end;
        m_step = 1;
    }

    void iter() {
        m_next = m_begin;
    }

    T next() {
        T next = m_next;
        m_next += m_step;
        return next;
    }

    void slice(Slice& slice) {
        T begin = (m_begin + slice.m_begin * m_step);

        if (begin > m_end) {
            begin = m_end;
        }

        m_begin = begin;
        T end = m_begin + slice.length() * slice.m_step;

        if (end > m_end) {
            end = m_end;
        }

        m_end = end;
        m_step *= slice.m_step;
    }

    void slice(OpenSlice& slice) {
        m_begin += slice.m_begin;
    }

    void reversed() {
        T begin;
        T l;

        begin = m_begin;
        l = length();
        m_begin = begin + (l - 1) * m_step;
        m_end = m_begin - (l - 1) * m_step;

        if (m_step > 0) {
            m_end--;
        } else {
            m_end++;
        }

        m_step *= -1;
    }

    i64 length() {
        if (m_step > 0) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

template <typename T>
class Data {

public:
    T m_begin;
    T m_end;
    T m_step;
    T m_next;

    Data(T end) : m_begin(0), m_end(end), m_step(1) {
    }

    void iter() {
        m_next = m_begin;
    }

    T next() {
        T next = m_next;
        m_next += m_step;
        return next;
    }

    void slice(Slice& slice) {
        T begin = (m_begin + slice.m_begin * m_step);

        if (begin > m_end) {
            begin = m_end;
        }

        m_begin = begin;
        T end = m_begin + slice.length() * slice.m_step;

        if (end > m_end) {
            end = m_end;
        }

        m_end = end;
        m_step *= slice.m_step;
    }

    void slice(OpenSlice& slice) {
        m_begin += slice.m_begin;
    }

    void reversed() {
        T begin;
        T l;

        begin = m_begin;
        l = length();
        m_begin = begin + (l - 1) * m_step;
        m_end = m_begin - (l - 1) * m_step;

        if (m_step > 0) {
            m_end--;
        } else {
            m_end++;
        }

        m_step *= -1;
    }

    i64 length() {
        if (m_step > 0) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

}
