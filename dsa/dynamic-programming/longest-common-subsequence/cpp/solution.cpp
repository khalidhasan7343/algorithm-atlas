#include "../../common.hpp"

namespace atlas_dp {
Integer lcs_length(const std::string& first_utf8, const std::string& second_utf8) {
    auto first = codepoints(first_utf8), second = codepoints(second_utf8);
    if (first.size() < second.size()) first.swap(second);
    std::vector<Integer> previous(second.size() + 1, 0);
    for (auto left : first) {
        std::vector<Integer> current(second.size() + 1, 0);
        for (std::size_t j = 1; j <= second.size(); ++j)
            current[j] = left == second[j-1] ? previous[j-1] + 1
                                            : std::max(previous[j], current[j-1]);
        previous.swap(current);
    }
    return previous.back();
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto first = atlas_dp::read_line();
        const auto second = atlas_dp::read_line();
        atlas_dp::end_lines();
        std::cout << atlas_dp::lcs_length(first, second);
    });
}
#endif
