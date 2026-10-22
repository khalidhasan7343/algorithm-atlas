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
// Positive and negative totals are separate exact two-word magnitudes.
// With <= SIZE_MAX 64-bit values and a 64-bit target, each fits 128 bits.
// Unsigned carry arithmetic avoids signed overflow and nonstandard __int128.
static_assert(std::numeric_limits<std::size_t>::digits <= 64);
static_assert(std::numeric_limits<long long>::digits == 63);
struct Magnitude { std::uint64_t high = 0, low = 0; };
Magnitude add(Magnitude value, std::uint64_t amount) {
    const auto before = value.low;
    value.low += amount;
    if (value.low < before) { ++value.high; }
    return value;
}
bool equal(Magnitude a, Magnitude b) { return a.high == b.high && a.low == b.low; }
std::uint64_t magnitude(long long value) {
    const auto raw = static_cast<std::uint64_t>(value);
    return value < 0 ? std::uint64_t{0} - raw : raw;
}
std::optional<std::vector<std::size_t>> subset_sum_backtracking(
    const std::vector<long long>& values, long long target) {
    std::vector<std::size_t> path;
    std::optional<std::vector<std::size_t>> answer;
    const auto visit = [&](auto&& self, std::size_t index,
                           Magnitude positive, Magnitude negative) -> bool {
        const bool match = target >= 0
            ? equal(positive, add(negative, magnitude(target)))
            : equal(add(positive, magnitude(target)), negative);
        if (match) { answer = path; return true; }
        if (index == values.size()) { return false; }
        auto next_positive = positive, next_negative = negative;
        if (values[index] >= 0) { next_positive = add(positive, magnitude(values[index])); }
        else { next_negative = add(negative, magnitude(values[index])); }
        path.push_back(index);
        const bool found = self(self, index + 1, next_positive, next_negative);
        path.pop_back();
        if (found) { return true; }
        return self(self, index + 1, positive, negative);
    };
    visit(visit, 0, Magnitude{}, Magnitude{});
    return answer;
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
        if (numbers.empty()) { throw std::invalid_argument("target required"); }
        const std::vector<long long> values(numbers.begin() + 1, numbers.end());
        write_json(algorithm_atlas::subset_sum_backtracking(values, numbers[0]));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
