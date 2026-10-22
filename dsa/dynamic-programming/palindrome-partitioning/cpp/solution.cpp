#include "../../common.hpp"

namespace atlas_dp {
Integer minimum_palindrome_cuts(const std::string& utf8) {
    const auto text = codepoints(utf8);
    const auto n = text.size();
    std::vector<std::vector<unsigned char>> palindrome(n, std::vector<unsigned char>(n, 0));
    for (std::size_t left = n; left-- > 0;) {
        for (std::size_t right = left; right < n; ++right)
            palindrome[left][right] = text[left] == text[right]
                && (right-left < 2 || palindrome[left+1][right-1]);
    }
    std::vector<Integer> pieces(n+1, static_cast<Integer>(n+1));
    pieces[0] = 0;
    for (std::size_t end = 1; end <= n; ++end)
        for (std::size_t start = 0; start < end; ++start)
            if (palindrome[start][end-1]) pieces[end] = std::min(pieces[end], pieces[start]+1);
    return n ? pieces[n]-1 : 0;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto text = atlas_dp::read_line();
        atlas_dp::end_lines();
        std::cout << atlas_dp::minimum_palindrome_cuts(text);
    });
}
#endif
