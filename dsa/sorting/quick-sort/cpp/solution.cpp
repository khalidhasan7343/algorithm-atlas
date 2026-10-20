// Three-way quicksort. Define ALGORITHM_ATLAS_NO_MAIN for reusable templates.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace algorithm_atlas {
namespace quick_sort_detail {

template <typename T>
void sort_range(std::vector<T>& result, std::size_t start, std::size_t end) {
    while (end - start > 1) {
        // Copy the pivot so moving its original element cannot change it.
        const T pivot = result[start + (end - start) / 2];
        std::size_t lower = start;
        std::size_t current = start;
        std::size_t upper = end;
        while (current < upper) {
            if (result[current] < pivot) {
                std::swap(result[lower++], result[current++]);
            } else if (pivot < result[current]) {
                std::swap(result[current], result[--upper]);
            } else {
                ++current;
            }
        }
        if (lower - start < end - upper) {
            sort_range(result, start, lower);
            start = upper;
        } else {
            sort_range(result, upper, end);
            end = lower;
        }
    }
}

}  // namespace quick_sort_detail

template <typename T>
std::vector<T> quick_sort(const std::vector<T>& values) {
    std::vector<T> result = values;
    quick_sort_detail::sort_range(result, 0, result.size());
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        const std::size_t offset = (token[0] == '+' || token[0] == '-') ? 1 : 0;
        bool decimal = offset < token.size();
        for (std::size_t index = offset; index < token.size(); ++index) {
            decimal = decimal && token[index] >= '0' && token[index] <= '9';
        }
        const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
        const char* end = token.data() + token.size();
        long long value = 0;
        const auto parsed = std::from_chars(begin, end, value);
        if (!decimal || parsed.ec != std::errc{} || parsed.ptr != end) {
            std::cerr << "error: expected signed decimal integers in long long range\n";
            return 1;
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) {
        std::cerr << "error: could not read standard input\n";
        return 1;
    }
    const auto result = algorithm_atlas::quick_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
