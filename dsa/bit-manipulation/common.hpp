#ifndef ATLAS_BIT_COMMON_HPP
#define ATLAS_BIT_COMMON_HPP
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <system_error>
#include <unordered_map>
#include <utility>
#include <vector>

namespace atlas_bit
{
    using Value = std::int64_t;
    using Word = std::uint32_t;
    static_assert(std::numeric_limits<Word>::digits == 32, "32-bit unsigned words required");
    constexpr Value MIN_VALUE = -2147483648LL, MAX_VALUE = 2147483647LL;

    inline void require(bool condition, const char *message)
    {
        if (!condition)
            throw std::invalid_argument(message);
    }
    inline void integer(Value value)
    {
        require(value >= MIN_VALUE && value <= MAX_VALUE, "expected signed 32-bit integer");
    }
    inline void sequence(const std::vector<Value> &values, std::size_t limit = 10000)
    {
        require(values.size() <= limit, "too many values");
        for (Value value : values)
            integer(value);
    }
    inline Value signed_value(Word word)
    {
        const Value wide = static_cast<Value>(word);
        return wide <= MAX_VALUE ? wide : wide - 4294967296LL;
    }
    inline void paired(const std::vector<Value> &values, std::size_t singletons)
    {
        sequence(values);
        require(values.size() >= singletons && values.size() % 2 == singletons % 2,
                "invalid size for singleton/pair contract");
        std::unordered_map<Value, int> frequency;
        for (Value value : values)
            ++frequency[value];
        std::size_t found = 0;
        for (const auto &item : frequency)
        {
            require(item.second == 1 || item.second == 2, "unsupported multiplicity");
            found += item.second == 1;
        }
        require(found == singletons, "incorrect singleton count");
    }
    inline std::vector<Value> read_values(std::size_t limit = 10000)
    {
        std::vector<Value> values;
        std::string token;
        while (std::cin >> token)
        {
            require(values.size() < limit && token.size() <= 11, "input size limit");
            std::size_t first = (token[0] == '+' || token[0] == '-') ? 1 : 0;
            require(first < token.size(), "missing digits");
            for (std::size_t i = first; i < token.size(); ++i)
                require(token[i] >= '0' && token[i] <= '9', "expected decimal integer");
            Value value = 0;
            const bool negative = token[0] == '-';
            for (std::size_t i = first; i < token.size(); ++i)
                value = value * 10 + static_cast<Value>(token[i] - '0');
            if (negative)
                value = -value;
            integer(value);
            values.push_back(value);
        }
        return values;
    }
    inline void emit(Value value) { std::cout << value; }
    template <class T>
    void emit(const std::vector<T> &values)
    {
        std::cout << '[';
        for (std::size_t i = 0; i < values.size(); ++i)
        {
            if (i)
                std::cout << ',';
            emit(values[i]);
        }
        std::cout << ']';
    }
}
#endif
