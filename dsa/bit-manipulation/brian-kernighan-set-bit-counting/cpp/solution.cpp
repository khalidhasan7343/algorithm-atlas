#include "../../common.hpp"

namespace atlas_bit {
inline Value solve(Value value) {
    integer(value);
    Word word=static_cast<Word>(value);
    Value count=0;
    while (word) {
        word &= word-Word{1};
        ++count;
    }
    return count;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto values=atlas_bit::read_values(1);
        atlas_bit::require(values.size()==1, "expected exactly one integer");
        atlas_bit::emit(atlas_bit::solve(values[0]));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
