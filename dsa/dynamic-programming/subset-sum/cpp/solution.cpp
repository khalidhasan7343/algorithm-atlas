#include "../../common.hpp"

namespace atlas_dp {
bool subset_sum(const std::vector<Integer>& values, Integer target) {
    work_limit(values.size(), target);
    for (auto value : values) bounded(value, 0, 1000000000);
    std::vector<bool> reachable(static_cast<std::size_t>(target+1), false);
    reachable[0] = true;
    for (auto value : values)
        for (Integer total = target; total >= value; --total)
            reachable[total] = reachable[total] || reachable[total-value];
    return reachable[target];
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto target = atlas_dp::read_integer();
        const auto values = atlas_dp::read_vector();
        atlas_dp::end_input();
        std::cout << std::boolalpha << atlas_dp::subset_sum(values, target);
    });
}
#endif
