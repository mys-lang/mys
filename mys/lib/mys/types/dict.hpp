#pragma once

#include "../common.hpp"
#include "../utils.hpp"
#include "../errors/key.hpp"
#include "string.hpp"
#include "tuple.hpp"
#include "list.hpp"

// Dicts.
template<typename TK, typename TV>
class Dict final
{
public:
    robin_hood::unordered_map<TK, TV> m_map;

    Dict() : m_map(robin_hood::unordered_map<TK, TV>())
    {
    }

    Dict(std::initializer_list<robin_hood::pair<TK, TV>> il) :
        m_map(robin_hood::unordered_map<TK, TV>(il))
    {
    }

    void __setitem__(const TK& key, const TV& value)
    {
        m_map[key] = value;
    }

    const TV& get(const TK& key, const TV& default_value)
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            return default_value;
        }
    }

    const TV& get(const TK& key) const
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            std::make_shared<KeyError>("key does not exist")->__throw();
        }
    }

    TV& get(const TK& key)
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            std::make_shared<KeyError>("key does not exist")->__throw();
        }
    }

    std::shared_ptr<List<TK>> keys() const
    {
        std::vector<TK> keys;
        for (const auto& kv : m_map) {
            keys.push_back(kv.first);
        }
        return std::make_shared<List<TK>>(keys);
    }

    std::shared_ptr<List<TV>> values() const
    {
        std::vector<TV> values;
        for (const auto& kv : m_map) {
            values.push_back(kv.second);
        }
        return std::make_shared<List<TV>>(values);
    }

    TV pop(const TK& key, const TV& def)
    {
        const auto& i = m_map.find(key);
        TV value;
        if (i == m_map.end()) {
            value = def;
        }
        else {
            value = i->second;
            m_map.erase(i);
        }
        return value;
    }

    void clear()
    {
        m_map.clear();
    }

    void update(const std::shared_ptr<Dict<TK, TV>>& other)
    {
        for (const auto& i : other->m_map) {
            m_map[i.first] = i.second;
        }
    }

    int __len__() const
    {
        return m_map.size();
    }

    bool __contains__(const TK& key) const
    {
        return m_map.contains(key);
    }

    String __str__()
    {
        std::stringstream ss;
        ss << *this;
        return String(ss.str().c_str());
    }
};

template<class TK, class TV> std::ostream&
operator<<(std::ostream& os, const Dict<TK, TV>& dict)
{
    const char *delim_p;

    os << "{";
    delim_p = "";

    for (auto item = dict.m_map.begin();
         item != dict.m_map.end();
         item++, delim_p = ", ") {
        os << delim_p << item->first << ": " << item->second;
    }

    os << "}";

    return os;
}

template<typename TK, typename TV> bool
operator==(const std::shared_ptr<Dict<TK, TV>>& a,
           const std::shared_ptr<Dict<TK, TV>>& b)
{
    if (!a && !b) {
        return true;
    } else {
        return shared_ptr_not_none(a)->m_map == shared_ptr_not_none(b)->m_map;
    }
}

template<typename TK, typename TV> bool
operator!=(const std::shared_ptr<Dict<TK, TV>>& a,
           const std::shared_ptr<Dict<TK, TV>>& b)
{
    return !(a == b);
}

template<typename TK, typename TV>
std::shared_ptr<List<std::shared_ptr<Tuple<TK, TV>>>>
create_list_from_dict(const std::shared_ptr<Dict<TK, TV>>& dict)
{
    auto list = std::make_shared<List<std::shared_ptr<Tuple<TK, TV>>>>();

    for (auto const& [key, value] : shared_ptr_not_none(dict)->m_map) {
        list->append(std::make_shared<Tuple<TK, TV>>(key, value));
    }

    return list;
}

template <typename TK, typename TV>
using SharedDict = std::shared_ptr<Dict<TK, TV>>;
