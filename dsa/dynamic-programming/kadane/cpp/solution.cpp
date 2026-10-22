#include "../../common.hpp"

namespace atlas_dp {
struct Subarray {
    Integer sum;
    std::size_t start;
    std::size_t end;
};
std::optional<Subarray> maximum_subarray(const std::vector<Integer>& values) {
    require(values.size() <= 10000, "at most 10000 values required");
    for (auto value : values) bounded(value, -1000000000, 1000000000);
    std::optional<Subarray> best;
    Integer current_sum = 0;
    std::size_t current_start = 0;
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index == 0 || current_sum < 0) {
            current_sum = values[index];
            current_start = index;
        } else current_sum += values[index];
        // Keeping a zero-sum prefix preserves the earlier start on ties.
        const Subarray candidate{current_sum, current_start, index+1};
        if (!best || candidate.sum > best->sum
            || (candidate.sum == best->sum && (candidate.start < best->start
                || (candidate.start == best->start && candidate.end < best->end))))
            best = candidate;
    }
    return best;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto values = atlas_dp::read_vector(10000);
        atlas_dp::end_input();
        const auto result = atlas_dp::maximum_subarray(values);
        if (!result) std::cout << "null";
        else std::cout << "[\"" << result->sum << "\"," << result->start << ',' << result->end << ']';
    });
}
#endif
