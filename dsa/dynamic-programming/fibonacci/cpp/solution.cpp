#include "../../common.hpp"

namespace atlas_dp {
Integer fibonacci(Integer n) {
    require(n >= 0, "negative index");
    if (n > 92) throw std::overflow_error("F(n) exceeds signed 64-bit");
    if (n == 0) return 0;
    Integer previous = 0, current = 1;
    for (Integer i = 2; i <= n; ++i) {
        const Integer next = previous + current;  // At most F(92).
        previous = current;
        current = next;
    }
    return current;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    return atlas_dp::cli([] {
        const auto n = atlas_dp::read_integer();
        atlas_dp::end_input();
        std::cout << atlas_dp::fibonacci(n);
    });
}
#endif
