#include <algorithm>
#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace algorithm_atlas {
// Exact signed magnitude for sums of <= SIZE_MAX signed 64-bit values.
static_assert(std::numeric_limits<long long>::digits == 63);
static_assert(std::numeric_limits<std::size_t>::digits <= 64);
struct Wide { bool negative = false; std::uint64_t high = 0, low = 0; };
int compare_magnitude(Wide a, Wide b) {
    if (a.high != b.high) { return a.high < b.high ? -1 : 1; }
    return a.low == b.low ? 0 : (a.low < b.low ? -1 : 1);
}
Wide from_integer(long long value) {
    const auto raw = static_cast<std::uint64_t>(value);
    return {value < 0, 0, value < 0 ? std::uint64_t{0} - raw : raw};
}
Wide add(Wide a, Wide b) {
    Wide result;
    if (a.negative == b.negative) {
        result.low = a.low + b.low;
        result.high = a.high + b.high + (result.low < a.low ? 1 : 0);
        result.negative = a.negative;
    } else {
        if (compare_magnitude(a, b) < 0) { std::swap(a, b); }
        result.low = a.low - b.low;
        result.high = a.high - b.high - (a.low < b.low ? 1 : 0);
        result.negative = a.negative;
    }
    if (!result.high && !result.low) { result.negative = false; }
    return result;
}
int compare(Wide a, Wide b) {
    if (a.negative != b.negative) { return a.negative ? -1 : 1; }
    const int order = compare_magnitude(a, b);
    return a.negative ? -order : order;
}
std::string decimal(Wide value) {
    if (!value.high && !value.low) { return "0"; }
    const bool negative = value.negative;
    std::string result;
    while (value.high || value.low) {
        Wide quotient;
        unsigned remainder = 0;
        for (int bit = 127; bit >= 0; --bit) {
            const auto digit = bit >= 64 ? (value.high >> (bit-64)) & 1U
                                        : (value.low >> bit) & 1U;
            remainder = remainder*2 + static_cast<unsigned>(digit);
            if (remainder >= 10) {
                remainder -= 10;
                if (bit >= 64) { quotient.high |= std::uint64_t{1} << (bit-64); }
                else { quotient.low |= std::uint64_t{1} << bit; }
            }
        }
        result.push_back(static_cast<char>('0' + remainder));
        value = quotient;
    }
    if (negative) { result.push_back('-'); }
    std::reverse(result.begin(), result.end());
    return result;
}
struct Subarray { Wide sum; std::size_t start, end; };
Subarray better(Subarray a, Subarray b) {
    const int order = compare(a.sum, b.sum);
    if (order != 0) { return order > 0 ? a : b; }
    return std::tie(a.start, a.end) < std::tie(b.start, b.end) ? a : b;
}
std::optional<Subarray> maximum_subarray(const std::vector<long long>& values) {
    if (values.empty()) { return std::nullopt; }
    const auto solve = [&](auto&& self, std::size_t lo, std::size_t hi) -> Subarray {
        if (hi-lo == 1) { return {from_integer(values[lo]), lo, hi}; }
        const auto mid = lo + (hi-lo)/2;
        const auto left = self(self, lo, mid), right = self(self, mid, hi);
        Wide total;
        Subarray suffix{from_integer(values[mid-1]), mid-1, mid};
        for (auto index = mid; index > lo;) {
            --index; total = add(total, from_integer(values[index]));
            suffix = better(suffix, {total, index, mid});
        }
        total = {};
        Subarray prefix{from_integer(values[mid]), mid, mid+1};
        for (auto index = mid; index < hi; ++index) {
            total = add(total, from_integer(values[index]));
            prefix = better(prefix, {total, mid, index+1});
        }
        return better(better(left, right), {add(suffix.sum, prefix.sum), suffix.start, prefix.end});
    };
    return solve(solve, 0, values.size());
}
void print_result(const std::optional<Subarray>& result) {
    if (!result) { std::cout << "null"; }
    else { std::cout << "[\"" << decimal(result->sum) << "\"," << result->start << ',' << result->end << ']'; }
}
bool decimal_token(const std::string& token) {
    if (token.empty()) { return false; }
    std::size_t i = (token[0] == '+' || token[0] == '-') ? 1 : 0;
    if (i == token.size()) { return false; }
    for (; i < token.size(); ++i) { if (token[i] < '0' || token[i] > '9') { return false; } }
    return true;
}
std::vector<long long> read_integers() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        if (!decimal_token(token)) { throw std::invalid_argument("expected decimal integers"); }
        const char* first = token.data() + (token[0] == '+' ? 1 : 0);
        long long value = 0;
        const auto result = std::from_chars(first, token.data() + token.size(), value);
        if (result.ec != std::errc{} || result.ptr != token.data() + token.size()) {
            throw std::invalid_argument("integer outside long long range");
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) { throw std::invalid_argument("input failure"); }
    return values;
}

}  // namespace algorithm_atlas
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        const auto values = algorithm_atlas::read_integers();
        algorithm_atlas::print_result(algorithm_atlas::maximum_subarray(values));
        std::cout << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
