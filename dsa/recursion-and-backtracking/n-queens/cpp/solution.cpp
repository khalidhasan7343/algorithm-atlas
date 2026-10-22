// Direct recursive backtracking. Define ALGORITHM_ATLAS_NO_MAIN for API use.
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <system_error>
#include <type_traits>
#include <vector>

namespace algorithm_atlas {
std::vector<std::vector<std::size_t>> n_queens(long long board_size) {
    if (board_size < 0) { throw std::invalid_argument("n must be nonnegative"); }
    const auto raw = static_cast<unsigned long long>(board_size);
    const auto maximum = std::numeric_limits<std::size_t>::max();
    if (raw > maximum / 2) { throw std::invalid_argument("n exceeds safe index range"); }
    const auto n = static_cast<std::size_t>(raw);
    std::vector<std::vector<std::size_t>> result;
    std::vector<std::size_t> path;
    std::vector<unsigned char> columns(n, 0), diagonal(n ? 2*n-1 : 0, 0),
                               anti(n ? 2*n-1 : 0, 0);
    const auto visit = [&](auto&& self, std::size_t row) -> void {
        if (row == n) { result.push_back(path); return; }
        for (std::size_t col = 0; col < n; ++col) {
            const auto d = row + col, a = row + (n - 1 - col);
            if (!columns[col] && !diagonal[d] && !anti[a]) {
                columns[col] = diagonal[d] = anti[a] = 1;
                path.push_back(col);
                self(self, row + 1);
                path.pop_back();
                columns[col] = diagonal[d] = anti[a] = 0;
            }
        }
    };
    visit(visit, 0);
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
namespace {
bool read_numbers(std::vector<long long>& numbers) {
    std::string token;
    while (std::cin >> token) {
        std::size_t first = (token[0] == '+' || token[0] == '-') ? 1 : 0;
        if (first == token.size()) { return false; }
        for (std::size_t i = first; i < token.size(); ++i) {
            if (token[i] < '0' || token[i] > '9') { return false; }
        }
        const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
        const char* end = token.data() + token.size();
        long long value = 0;
        const auto parsed = std::from_chars(begin, end, value, 10);
        if (parsed.ec != std::errc{} || parsed.ptr != end) { return false; }
        numbers.push_back(value);
    }
    return std::cin.eof();
}
template <typename T> void write_json(const std::vector<T>& value);
template <typename T> void write_json(const std::optional<T>& value);
template <typename T, std::enable_if_t<std::is_integral_v<T>, int> = 0>
void write_json(T value) { std::cout << value; }
[[maybe_unused]] void write_json(const std::string& value) { std::cout << std::quoted(value); }
template <typename T> void write_json(const std::vector<T>& value) {
    std::cout << '[';
    for (std::size_t i = 0; i < value.size(); ++i) {
        if (i) { std::cout << ','; }
        write_json(value[i]);
    }
    std::cout << ']';
}
template <typename T> void write_json(const std::optional<T>& value) {
    if (value) { write_json(*value); }
    else { std::cout << "null"; }
}
}  // namespace

int main() {
    std::vector<long long> numbers;
    if (!read_numbers(numbers)) {
        std::cerr << "error: expected signed decimal long long tokens\n";
        return 1;
    }
    try {
        if (numbers.size() != 1) { throw std::invalid_argument("exactly one n required"); }
        write_json(algorithm_atlas::n_queens(numbers[0]));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
