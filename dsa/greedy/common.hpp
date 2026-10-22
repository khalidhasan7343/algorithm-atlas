#ifndef ALGORITHM_ATLAS_GREEDY_COMMON_HPP
#define ALGORITHM_ATLAS_GREEDY_COMMON_HPP

#include <algorithm>
#include <charconv>
#include <cstddef>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <optional>
#include <stdexcept>
#include <string>
#include <vector>

namespace atlas_greedy {
using Integer = long long;
static_assert(std::numeric_limits<Integer>::digits == 63, "64-bit signed integers required");
inline void require(bool condition, const char* message) {
    if (!condition) throw std::invalid_argument(message);
}
inline void bounded(Integer value, Integer lower, Integer upper) {
    require(value >= lower && value <= upper, "integer outside supported domain");
}
inline Integer parse_integer(const std::string& token) {
    require(!token.empty(), "missing integer");
    const std::size_t digit = (token[0] == '+' || token[0] == '-') ? 1 : 0;
    require(digit < token.size(), "missing decimal digits");
    for (std::size_t i = digit; i < token.size(); ++i)
        require(token[i] >= '0' && token[i] <= '9', "expected ASCII decimal integer");
    const char* first = token.data() + (token[0] == '+' ? 1 : 0);
    Integer result = 0;
    const auto parsed = std::from_chars(first, token.data()+token.size(), result);
    require(parsed.ec == std::errc{} && parsed.ptr == token.data()+token.size(), "integer outside signed-64");
    return result;
}
inline Integer read_integer() {
    std::string token;
    require(static_cast<bool>(std::cin >> token), "missing integer");
    return parse_integer(token);
}
inline void end_input() {
    std::string token;
    require(!(std::cin >> token), "extra input");
}
template <typename T> void print_vector(const std::vector<T>& values) {
    std::cout << '[';
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << values[i];
    }
    std::cout << ']';
}
template <typename Action> int cli(Action action) {
    try { action(); std::cout << '\n'; return 0; }
    catch (const std::exception& error) { std::cerr << "error: " << error.what() << '\n'; return 2; }
}
}  // namespace atlas_greedy
#endif
