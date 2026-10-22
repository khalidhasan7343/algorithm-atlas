#include "../../common.hpp"

namespace atlas_dp {
Integer matrix_chain_cost(const std::vector<Integer>& dimensions) {
    require(dimensions.size() != 1 && dimensions.size() <= 101, "use zero or 2..101 dimensions");
    for (auto d : dimensions) bounded(d, 1, 100000);
    if (dimensions.size() <= 2) return 0;
    const auto n = dimensions.size() - 1;
    std::vector<std::vector<Integer>> cost(n, std::vector<Integer>(n, 0));
    for (std::size_t length = 2; length <= n; ++length) {
        for (std::size_t left = 0; left + length <= n; ++left) {
            const auto right = left + length - 1;
            auto best = std::numeric_limits<Integer>::max();
            for (std::size_t split = left; split < right; ++split) {
                // <=99 products, each <=10^15, so every candidate fits signed 64-bit.
                const auto candidate = cost[left][split] + cost[split+1][right]
                    + dimensions[left] * dimensions[split+1] * dimensions[right+1];
                best = std::min(best, candidate);
            }
            cost[left][right] = best;
        }
    }
    return cost[0][n-1];
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto dimensions = atlas_dp::read_vector(101);
        atlas_dp::end_input();
        std::cout << atlas_dp::matrix_chain_cost(dimensions);
    });
}
#endif
