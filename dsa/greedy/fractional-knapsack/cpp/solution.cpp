#include "../../common.hpp"

namespace atlas_greedy {
struct Rational {
    Integer numerator, denominator;
    Rational(Integer n = 0, Integer d = 1) {
        require(n >= 0 && d > 0, "invalid nonnegative rational");
        const auto common = std::gcd(n, d);
        numerator = n/common;
        denominator = d/common;
    }
};
struct KnapsackResult { Rational value; std::vector<Rational> fractions; };
KnapsackResult fractional_knapsack(const std::vector<Integer>& weights,
                                   const std::vector<Integer>& values, Integer capacity) {
    bounded(capacity, 0, 1000000000);
    require(weights.size() == values.size() && weights.size() <= 10000, "invalid item count");
    for (auto w : weights) bounded(w, 1, 1000000);
    for (auto v : values) bounded(v, 0, 1000000);
    std::vector<std::size_t> ordered(weights.size());
    std::iota(ordered.begin(), ordered.end(), 0);
    std::sort(ordered.begin(), ordered.end(), [&](auto a, auto b) {
        const auto left = values[a]*weights[b], right = values[b]*weights[a];
        return left != right ? left > right : a < b;
    });
    KnapsackResult result{Rational(), std::vector<Rational>(weights.size())};
    Integer whole_value = 0, remaining = capacity;
    for (auto index : ordered) {
        if (remaining == 0 || values[index] == 0) break;
        if (weights[index] <= remaining) {
            result.fractions[index] = Rational(1);
            whole_value += values[index];
            remaining -= weights[index];
            result.value = Rational(whole_value);
        } else {
            result.fractions[index] = Rational(remaining, weights[index]);
            // whole_value <= 10^10, weight <= 10^6, product <= 10^16.
            result.value = Rational(whole_value*weights[index]+values[index]*remaining, weights[index]);
            break;
        }
    }
    return result;
}
inline void print_ratio(const Rational& value) {
    std::cout << '[' << value.numerator << ',' << value.denominator << ']';
}
inline void print_knapsack(const KnapsackResult& result) {
    std::cout << "{\"value\":"; print_ratio(result.value); std::cout << ",\"fractions\":[";
    for (std::size_t i = 0; i < result.fractions.size(); ++i) {
        if (i) std::cout << ',';
        print_ratio(result.fractions[i]);
    }
    std::cout << "]}";
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_greedy::cli([] {
        const auto capacity = atlas_greedy::read_integer();
        const auto count = atlas_greedy::read_integer();
        atlas_greedy::bounded(count, 0, 10000);
        std::vector<atlas_greedy::Integer> weights, values;
        for (atlas_greedy::Integer i = 0; i < count; ++i) {
            weights.push_back(atlas_greedy::read_integer());
            values.push_back(atlas_greedy::read_integer());
        }
        atlas_greedy::end_input();
        atlas_greedy::print_knapsack(atlas_greedy::fractional_knapsack(weights, values, capacity));
    });
}
#endif
