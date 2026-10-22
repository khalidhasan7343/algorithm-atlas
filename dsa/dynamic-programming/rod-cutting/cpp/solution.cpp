#include "../../common.hpp"

namespace atlas_dp {
std::optional<Integer> rod_cutting(const std::vector<std::optional<Integer>>& prices, Integer length) {
    work_limit(prices.size(), length);
    for (auto price : prices) if (price) bounded(*price, -1000000000, 1000000000);
    std::vector<std::optional<Integer>> best(static_cast<std::size_t>(length + 1));
    best[0] = 0;
    for (Integer total = 1; total <= length; ++total) {
        for (std::size_t i = 0; i < prices.size() && i < static_cast<std::size_t>(total); ++i) {
            const auto cut = static_cast<Integer>(i + 1);
            if (prices[i] && best[total - cut]) {
                const auto candidate = *prices[i] + *best[total - cut];
                if (!best[total] || candidate > *best[total]) best[total] = candidate;
            }
        }
    }
    return best[length];  // At most length terms, magnitude <= 10^13.
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto length = atlas_dp::read_integer();
        const auto count = atlas_dp::read_integer();
        atlas_dp::bounded(count, 0, 1000);
        std::vector<std::optional<atlas_dp::Integer>> prices;
        for (atlas_dp::Integer i = 0; i < count; ++i) {
            std::string token;
            atlas_dp::require(static_cast<bool>(std::cin >> token), "missing price");
            prices.push_back(token == "x" ? std::nullopt : std::optional<atlas_dp::Integer>(atlas_dp::parse_integer(token)));
        }
        atlas_dp::end_input();
        atlas_dp::emit(atlas_dp::rod_cutting(prices, length));
    });
}
#endif
