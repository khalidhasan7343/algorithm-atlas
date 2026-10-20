// Stable top-down merge sort. Compile with C++17 or C++20.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <string>
#include <system_error>
#include <vector>

namespace algorithm_atlas {
namespace merge_sort_detail {

template <typename T>
void sort_range(std::vector<T>& result, std::vector<T>& buffer,
                std::size_t start, std::size_t end) {
    if (end - start < 2) {
        return;
    }
    const std::size_t middle = start + (end - start) / 2;
    sort_range(result, buffer, start, middle);
    sort_range(result, buffer, middle, end);

    std::size_t left = start;
    std::size_t right = middle;
    for (std::size_t destination = start; destination < end; ++destination) {
        // Equivalence under < chooses the left item, preserving stability.
        if (right == end ||
            (left < middle && !(result[right] < result[left]))) {
            buffer[destination] = result[left++];
        } else {
            buffer[destination] = result[right++];
        }
    }
    for (std::size_t position = start; position < end; ++position) {
        result[position] = buffer[position];
    }
}

}  // namespace merge_sort_detail

template <typename T>
std::vector<T> merge_sort(const std::vector<T>& values) {
    std::vector<T> result = values;
    // Copy initialization also supports records without a default constructor.
    std::vector<T> buffer = result;
    merge_sort_detail::sort_range(result, buffer, 0, result.size());
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        const char* begin = token.data();
        const char* end = begin + token.size();
        if (*begin == '+') {
            ++begin;
        }
        bool decimal = begin != end;
        for (const char* position = begin; position != end; ++position) {
            if (position == begin && *position == '-') {
                continue;
            }
            if (*position < '0' || *position > '9') {
                decimal = false;
            }
        }
        long long value = 0;
        const auto conversion = std::from_chars(begin, end, value, 10);
        if (!decimal || conversion.ec != std::errc{} || conversion.ptr != end ||
            (token.size() > 1 && token[0] == '+' && token[1] == '-')) {
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
    const auto result = algorithm_atlas::merge_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
