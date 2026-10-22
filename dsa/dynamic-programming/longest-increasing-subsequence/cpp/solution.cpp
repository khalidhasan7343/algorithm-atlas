#include "../../common.hpp"

namespace atlas_dp {
Integer lis_length(const std::vector<Integer>& values) {
    require(values.size() <= 1000, "at most 1000 values required");
    for (auto value : values) bounded(value, -1000000000, 1000000000);
    std::vector<Integer> best(values.size(), 1);
    Integer answer = 0;
    for (std::size_t end = 0; end < values.size(); ++end) {
        for (std::size_t previous = 0; previous < end; ++previous)
            if (values[previous] < values[end]) best[end] = std::max(best[end], best[previous] + 1);
        answer = std::max(answer, best[end]);
    }
    return answer;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto values = atlas_dp::read_vector();
        atlas_dp::end_input();
        std::cout << atlas_dp::lis_length(values);
    });
}
#endif
