#include "../../common.hpp"

namespace atlas_dp {
Integer edit_distance(const std::string& first_utf8, const std::string& second_utf8) {
    auto first = codepoints(first_utf8), second = codepoints(second_utf8);
    if (first.size() < second.size()) first.swap(second);
    std::vector<Integer> previous(second.size() + 1);
    for (std::size_t j = 0; j <= second.size(); ++j) previous[j] = static_cast<Integer>(j);
    for (std::size_t i = 1; i <= first.size(); ++i) {
        std::vector<Integer> current(second.size() + 1);
        current[0] = static_cast<Integer>(i);
        for (std::size_t j = 1; j <= second.size(); ++j)
            current[j] = std::min({previous[j] + 1, current[j-1] + 1,
                                   previous[j-1] + (first[i-1] != second[j-1])});
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
        std::cout << atlas_dp::edit_distance(first, second);
    });
}
#endif
