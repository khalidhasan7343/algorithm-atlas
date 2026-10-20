// Shell sort with Knuth's 3h+1 gaps; C++17 and C++20.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <string>
#include <system_error>
#include <vector>

namespace algorithm_atlas {

template <typename T>
std::vector<T> shell_sort(const std::vector<T>& values) {
    std::vector<T> result = values;
    std::size_t gap = 1;
    // gap < size/3 ensures 3*gap+1 is representable, even for huge sizes.
    while (gap < result.size() / 3) {
        gap = 3 * gap + 1;
    }
    while (gap >= 1) {
        for (std::size_t index = gap; index < result.size(); ++index) {
            T item = result[index];
            std::size_t position = index;
            // Check before subtracting to avoid unsigned index underflow.
            while (position >= gap && item < result[position - gap]) {
                result[position] = result[position - gap];
                position -= gap;
            }
            result[position] = item;
        }
        gap /= 3;
    }
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        std::size_t digit = (token[0] == '+' || token[0] == '-') ? 1 : 0;
        bool decimal = digit < token.size();
        for (; digit < token.size(); ++digit) {
            if (token[digit] < '0' || token[digit] > '9') {
                decimal = false;
            }
        }
        const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
        const char* end = token.data() + token.size();
        long long value = 0;
        const auto conversion = std::from_chars(begin, end, value, 10);
        if (!decimal || conversion.ec != std::errc{} || conversion.ptr != end) {
            std::cerr << "Invalid input: expected signed decimal integers "
                         "in the long long range\n";
            return 1;
        }
        values.push_back(value);
    }
    if (std::cin.bad()) {
        std::cerr << "Input read failed\n";
        return 1;
    }
    const auto result = algorithm_atlas::shell_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
