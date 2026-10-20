// Bottom-up max-heap construction with iterative sift-down; C++17/C++20.
#include <charconv>
#include <cstddef>
#include <iostream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace algorithm_atlas {
namespace heap_sort_detail {

template <typename T>
void sift_down(std::vector<T>& values, std::size_t root, std::size_t count) {
    // This condition both finds internal nodes and keeps child arithmetic safe.
    while (root < count / 2) {
        std::size_t child = 2 * root + 1;
        if (child + 1 < count && values[child] < values[child + 1]) {
            ++child;
        }
        if (!(values[root] < values[child])) {
            return;
        }
        std::swap(values[root], values[child]);
        root = child;
    }
}

}  // namespace heap_sort_detail

template <typename T>
std::vector<T> heap_sort(const std::vector<T>& values) {
    std::vector<T> result = values;
    for (std::size_t parent = result.size() / 2; parent > 0; --parent) {
        heap_sort_detail::sift_down(result, parent - 1, result.size());
    }
    for (std::size_t count = result.size(); count > 1; --count) {
        std::swap(result[0], result[count - 1]);
        heap_sort_detail::sift_down(result, 0, count - 1);
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
    const auto result = algorithm_atlas::heap_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
