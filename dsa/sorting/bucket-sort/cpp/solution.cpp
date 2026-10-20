// Stable bucket sort on finite double values in [0, 1], including both endpoints.
#include <algorithm>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace algorithm_atlas {

std::vector<double> bucket_sort(const std::vector<double>& values,
                                std::size_t bucket_count = 0) {
    std::vector<double> result(values);
    if (bucket_count == 0) {
        bucket_count = std::max<std::size_t>(1, result.size());
    }
    for (const double value : result) {
        if (!std::isfinite(value) || value < 0.0 || value > 1.0) {
            throw std::invalid_argument("bucket_sort requires finite values in [0, 1]");
        }
    }
    if (result.size() < 2) {
        return result;
    }

    std::vector<std::vector<double>> buckets(bucket_count);
    for (const double value : result) {
        const double scaled = value * static_cast<double>(bucket_count);
        std::size_t index = bucket_count - 1;
        // Clamp 1.0 and rounded endpoints before any potentially unsafe cast.
        if (scaled < static_cast<double>(bucket_count) &&
            scaled < static_cast<double>(std::numeric_limits<std::size_t>::max())) {
            index = std::min(bucket_count - 1, static_cast<std::size_t>(scaled));
        }
        buckets[index].push_back(value);
    }

    result.clear();
    for (auto& bucket : buckets) {
        for (std::size_t index = 1; index < bucket.size(); ++index) {
            const double value = bucket[index];
            std::size_t position = index;
            while (position > 0 && value < bucket[position - 1]) {
                bucket[position] = bucket[position - 1];
                --position;
            }
            bucket[position] = value;
        }
        result.insert(result.end(), bucket.begin(), bucket.end());
    }
    return result;
}

}  // namespace algorithm_atlas

#ifndef ALGORITHM_ATLAS_NO_MAIN
namespace {
bool is_digit(char value) {
    return value >= '0' && value <= '9';
}

bool parse_decimal(const std::string& token, double& value) {
    std::size_t position = 0;
    if (!token.empty() && (token[0] == '+' || token[0] == '-')) {
        ++position;
    }
    std::size_t digits = 0;
    while (position < token.size() && is_digit(token[position])) {
        ++digits;
        ++position;
    }
    if (position < token.size() && token[position] == '.') {
        ++position;
        while (position < token.size() && is_digit(token[position])) {
            ++digits;
            ++position;
        }
    }
    if (digits == 0) {
        return false;
    }
    if (position < token.size() && (token[position] == 'e' || token[position] == 'E')) {
        ++position;
        if (position < token.size() && (token[position] == '+' || token[position] == '-')) {
            ++position;
        }
        const auto exponent_begin = position;
        while (position < token.size() && is_digit(token[position])) {
            ++position;
        }
        if (position == exponent_begin) {
            return false;
        }
    }
    if (position != token.size()) {
        return false;
    }
    char* end = nullptr;
    value = std::strtod(token.c_str(), &end);
    return end == token.c_str() + token.size() && std::isfinite(value) &&
           value >= 0.0 && value <= 1.0;
}
}  // namespace

int main() {
    std::vector<double> values;
    std::string token;
    while (std::cin >> token) {
        double value = 0.0;
        if (!parse_decimal(token, value)) {
            std::cerr << "error: expected finite decimal real values in [0, 1]\n";
            return 1;
        }
        values.push_back(value);
    }
    if (std::cin.bad()) {
        std::cerr << "error: could not read input\n";
        return 1;
    }
    const auto result = algorithm_atlas::bucket_sort(values);
    std::cout << std::setprecision(17);
    for (std::size_t index = 0; index < result.size(); ++index) {
        if (index != 0) {
            std::cout << ' ';
        }
        std::cout << result[index];
    }
    std::cout << '\n';
}
#endif
