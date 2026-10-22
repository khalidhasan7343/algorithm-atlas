#include "../../common.hpp"

namespace atlas_dp {
Integer knapsack(const std::vector<Integer>& weights, const std::vector<Integer>& values,
                 Integer capacity) {
    work_limit(weights.size(), capacity);
    require(weights.size() == values.size(), "weight/value length mismatch");
    for (auto weight : weights) bounded(weight, 0, 1000000000);
    for (auto value : values) bounded(value, -1000000000, 1000000000);
    std::vector<Integer> best(static_cast<std::size_t>(capacity + 1), 0);
    for (std::size_t i = 0; i < weights.size(); ++i) {
        // Signed loop counter also handles weight zero without underflow.
        for (Integer room = capacity; room >= weights[i]; --room) {
            auto& cell = best[static_cast<std::size_t>(room)];
            cell = std::max(cell, best[static_cast<std::size_t>(room - weights[i])] + values[i]);
        }
    }
    return best.back();  // Sum of positive item values is at most 10^12.
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto capacity = atlas_dp::read_integer();
        const auto count = atlas_dp::read_integer();
        atlas_dp::bounded(count, 0, 1000);
        std::vector<atlas_dp::Integer> weights, values;
        for (atlas_dp::Integer i = 0; i < count; ++i) {
            weights.push_back(atlas_dp::read_integer());
            values.push_back(atlas_dp::read_integer());
        }
        atlas_dp::end_input();
        std::cout << atlas_dp::knapsack(weights, values, capacity);
    });
}
#endif
