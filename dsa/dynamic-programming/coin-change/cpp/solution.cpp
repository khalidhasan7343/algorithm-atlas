#include "../../common.hpp"

namespace atlas_dp {
std::vector<Integer> denominations(std::vector<Integer> coins, Integer amount) {
    work_limit(coins.size(), amount);
    for (auto coin : coins) bounded(coin, 1, 1000000000);
    std::sort(coins.begin(), coins.end());
    coins.erase(std::unique(coins.begin(), coins.end()), coins.end());
    return coins;
}
std::optional<Integer> minimum_coins(const std::vector<Integer>& input, Integer amount) {
    const auto coins = denominations(input, amount);
    std::vector<Integer> best(static_cast<std::size_t>(amount + 1), amount + 1);
    best[0] = 0;
    for (Integer total = 1; total <= amount; ++total)
        for (auto coin : coins)
            if (coin <= total) best[total] = std::min(best[total], best[total - coin] + 1);
    if (best[amount] > amount) return std::nullopt;
    return best[amount];
}
Integer count_combinations(const std::vector<Integer>& input, Integer amount) {
    const auto coins = denominations(input, amount);
    std::vector<Integer> ways(static_cast<std::size_t>(amount + 1), 0);
    ways[0] = 1;
    for (auto coin : coins)
        for (Integer total = coin; total <= amount; ++total)
            ways[total] = checked_count_add(ways[total], ways[total - coin]);
    return ways[amount];
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto amount = atlas_dp::read_integer();
        const auto coins = atlas_dp::read_vector();
        atlas_dp::end_input();
        const auto minimum = atlas_dp::minimum_coins(coins, amount);
        const auto ways = atlas_dp::count_combinations(coins, amount);
        std::cout << '['; atlas_dp::emit(minimum); std::cout << ',' << ways << ']';
    });
}
#endif
