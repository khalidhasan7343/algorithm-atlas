#ifndef ALGORITHM_ATLAS_DP_COMMON_HPP
#define ALGORITHM_ATLAS_DP_COMMON_HPP

#include <algorithm>
#include <charconv>
#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace atlas_dp {
using Integer = long long;
static_assert(std::numeric_limits<Integer>::digits == 63, "64-bit integers required");

inline void require(bool condition, const char* message) {
    if (!condition) throw std::invalid_argument(message);
}
inline void bounded(Integer value, Integer low, Integer high) {
    require(value >= low && value <= high, "integer outside supported domain");
}
inline void work_limit(std::size_t count, Integer width) {
    bounded(width, 0, 10000);
    require(count <= 1000 && count * (static_cast<std::size_t>(width) + 1) <= 2000000,
            "DP work limit exceeded");
}
inline Integer checked_count_add(Integer a, Integer b) {
    if (b > std::numeric_limits<Integer>::max() - a)
        throw std::overflow_error("combination count exceeds signed 64-bit");
    return a + b;
}
inline Integer parse_integer(const std::string& token) {
    require(!token.empty(), "missing integer");
    const char* first = token.data();
    const char* last = first + token.size();
    if (*first == '+') ++first;
    require(first != last && !(*first == '-' && first != token.data()), "invalid integer");
    Integer value = 0;
    const auto result = std::from_chars(first, last, value);
    require(result.ec == std::errc{} && result.ptr == last, "invalid integer");
    return value;
}
inline Integer read_integer() {
    std::string token;
    require(static_cast<bool>(std::cin >> token), "missing integer");
    return parse_integer(token);
}
inline std::vector<Integer> read_vector(Integer limit = 1000) {
    const Integer count = read_integer();
    bounded(count, 0, limit);
    std::vector<Integer> values;
    values.reserve(static_cast<std::size_t>(count));
    for (Integer i = 0; i < count; ++i) values.push_back(read_integer());
    return values;
}
inline void end_input() {
    std::string extra;
    require(!(std::cin >> extra), "extra input");
}
inline void emit(const std::optional<Integer>& value) {
    if (value) std::cout << *value;
    else std::cout << "null";
}

// Strict UTF-8 decoding: reject overlong forms, surrogates, and > U+10FFFF.
inline std::u32string codepoints(const std::string& text) {
    require(text.size() <= 4000, "UTF-8 byte limit exceeded");
    std::u32string result;
    for (std::size_t i = 0; i < text.size();) {
        const auto first = static_cast<unsigned char>(text[i++]);
        std::uint32_t value;
        unsigned trailing;
        std::uint32_t minimum;
        if (first < 0x80) { value = first; trailing = 0; minimum = 0; }
        else if (first >= 0xc2 && first <= 0xdf) { value = first & 31; trailing = 1; minimum = 0x80; }
        else if (first >= 0xe0 && first <= 0xef) { value = first & 15; trailing = 2; minimum = 0x800; }
        else if (first >= 0xf0 && first <= 0xf4) { value = first & 7; trailing = 3; minimum = 0x10000; }
        else throw std::invalid_argument("invalid UTF-8 lead");
        require(i + trailing <= text.size(), "truncated UTF-8");
        for (unsigned j = 0; j < trailing; ++j) {
            const auto next = static_cast<unsigned char>(text[i++]);
            require((next & 0xc0) == 0x80, "invalid UTF-8 continuation");
            value = (value << 6) | (next & 63);
        }
        require(value >= minimum && value <= 0x10ffff && !(value >= 0xd800 && value <= 0xdfff),
                "invalid Unicode scalar value");
        result.push_back(static_cast<char32_t>(value));
    }
    require(result.size() <= 1000, "code point limit exceeded");
    return result;
}
inline std::string read_line() {
    std::string line;
    require(static_cast<bool>(std::getline(std::cin, line)), "missing text line");
    if (!line.empty() && line.back() == '\r') line.pop_back();
    return line;
}
inline void end_lines() {
    require(std::cin.peek() == std::char_traits<char>::eof(), "extra text line");
}
template <typename Action> int cli(Action action) {
    try { action(); std::cout << '\n'; return 0; }
    catch (const std::exception& error) { std::cerr << "error: " << error.what() << '\n'; return 2; }
}
}  // namespace atlas_dp
#endif
