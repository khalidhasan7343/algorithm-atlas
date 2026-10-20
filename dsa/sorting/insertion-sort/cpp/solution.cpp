// Stable insertion sort. Define ALGORITHM_ATLAS_NO_MAIN to include the API.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <string>
#include <system_error>
#include <vector>

namespace algorithm_atlas {

template <typename T>
std::vector<T> insertion_sort(const std::vector<T>& values) {
    std::vector<T> result = values;
    for (std::size_t index = 1; index < result.size(); ++index) {
        const T item = result[index];
        std::size_t position = index;
        // Strict comparison preserves the original order of equivalent items.
        while (position > 0 && item < result[position - 1]) {
            result[position] = result[position - 1];
            --position;
        }
        result[position] = item;
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
    const auto result = algorithm_atlas::insertion_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
