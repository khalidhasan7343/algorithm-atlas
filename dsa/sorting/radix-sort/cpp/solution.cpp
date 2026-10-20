// Stable base-256 LSD radix sort for signed 64-bit long long values.
#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <string>
#include <system_error>
#include <vector>

static_assert(std::numeric_limits<long long>::digits == 63 &&
                  std::numeric_limits<long long>::min() ==
                      (-9223372036854775807LL - 1),
              "This lesson requires the full signed 64-bit long long range");

namespace algorithm_atlas {

std::vector<long long> radix_sort(const std::vector<long long>& values) {
    std::vector<long long> result(values);
    if (result.size() < 2) {
        return result;
    }
    std::vector<long long> buffer(result.size());
    constexpr std::uint64_t sign_bit = std::uint64_t{1} << 63;
    for (unsigned shift = 0; shift < 64; shift += 8) {
        std::array<std::size_t, 256> counts{};
        for (const long long value : result) {
            // Conversion is defined modulo 2^64, including LLONG_MIN.
            const auto key = static_cast<std::uint64_t>(value) ^ sign_bit;
            ++counts[(key >> shift) & 255];
        }
        std::size_t position = 0;
        for (auto& count : counts) {
            const auto frequency = count;
            count = position;
            position += frequency;
        }
        for (const long long value : result) {
            const auto key = static_cast<std::uint64_t>(value) ^ sign_bit;
            const auto digit = (key >> shift) & 255;
            buffer[counts[digit]++] = value;
        }
        result.swap(buffer);
    }
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
namespace {
bool parse_integer(const std::string& token, long long& value) {
    std::size_t first_digit = 0;
    if (!token.empty() && (token[0] == '+' || token[0] == '-')) {
        first_digit = 1;
    }
    if (first_digit == token.size()) {
        return false;
    }
    for (std::size_t index = first_digit; index < token.size(); ++index) {
        if (token[index] < '0' || token[index] > '9') {
            return false;
        }
    }
    const char* begin = token.data() + (token[0] == '+' ? 1 : 0);
    const char* end = token.data() + token.size();
    const auto parsed = std::from_chars(begin, end, value);
    return parsed.ec == std::errc{} && parsed.ptr == end;
}
}  // namespace

int main() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        long long value = 0;
        if (!parse_integer(token, value)) {
            std::cerr << "error: expected signed decimal integers in the long long range\n";
            return 1;
        }
        values.push_back(value);
    }
    if (std::cin.bad()) {
        std::cerr << "error: could not read input\n";
        return 1;
    }
    const auto result = algorithm_atlas::radix_sort(values);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
