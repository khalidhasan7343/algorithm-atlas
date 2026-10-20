// Counting sort with negative-key offsets and an explicit range limit.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <system_error>
#include <type_traits>
#include <vector>

namespace algorithm_atlas {

std::vector<long long> counting_sort(
    const std::vector<long long>& values, std::size_t max_range = 1000000) {
    if (max_range == 0) {
        throw std::invalid_argument("max_range must be positive");
    }
    if (values.empty()) {
        return {};
    }
    long long minimum = values.front();
    long long maximum = values.front();
    for (const long long value : values) {
        if (value < minimum) { minimum = value; }
        if (value > maximum) { maximum = value; }
    }

    using Unsigned = std::make_unsigned_t<long long>;
    // Unsigned subtraction gives the exact nonnegative mathematical distance
    // even across zero, without ever evaluating an overflowing signed sum.
    const Unsigned difference =
        static_cast<Unsigned>(maximum) - static_cast<Unsigned>(minimum);
    if (difference == std::numeric_limits<Unsigned>::max() ||
        difference >= max_range) {
        throw std::length_error("key range exceeds max_range");
    }
    const std::size_t key_range = static_cast<std::size_t>(difference) + 1;
    std::vector<std::size_t> counts(key_range, 0);
    for (const long long value : values) {
        const auto offset = static_cast<std::size_t>(
            static_cast<Unsigned>(value) - static_cast<Unsigned>(minimum));
        ++counts[offset];
    }
    for (std::size_t index = 1; index < key_range; ++index) {
        counts[index] += counts[index - 1];
    }

    std::vector<long long> result(values.size());
    for (std::size_t index = values.size(); index > 0; --index) {
        const long long value = values[index - 1];
        const auto offset = static_cast<std::size_t>(
            static_cast<Unsigned>(value) - static_cast<Unsigned>(minimum));
        result[--counts[offset]] = value;
    }
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        const std::size_t digits_start =
            (!token.empty() && (token[0] == '+' || token[0] == '-')) ? 1 : 0;
        bool valid = digits_start < token.size();
        for (std::size_t index = digits_start; index < token.size(); ++index) {
            valid = valid && token[index] >= '0' && token[index] <= '9';
        }
        if (!valid) {
            std::cerr << "error: expected signed decimal integers in long long range\n";
            return 1;
        }
        const char* first = token.data() + (token[0] == '+' ? 1 : 0);
        const char* last = token.data() + token.size();
        long long value = 0;
        const auto parsed = std::from_chars(first, last, value, 10);
        if (parsed.ec != std::errc{} || parsed.ptr != last) {
            std::cerr << "error: expected signed decimal integers in long long range\n";
            return 1;
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) {
        std::cerr << "error: failed to read standard input\n";
        return 1;
    }
    try {
        const auto result = algorithm_atlas::counting_sort(values);
        for (std::size_t index = 0; index < result.size(); ++index) {
            if (index != 0) { std::cout << ' '; }
            std::cout << result[index];
        }
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
