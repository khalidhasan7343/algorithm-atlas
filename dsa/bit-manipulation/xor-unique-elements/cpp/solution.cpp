#include "../../common.hpp"

namespace atlas_bit {
inline Value xor_candidate(const std::vector<Value>& values) {
    sequence(values);
    require(!values.empty() && values.size()%2==1, "expected nonempty odd input");
    Word word=0;
    for (Value value : values) word ^= static_cast<Word>(value);
    return signed_value(word);
}
inline Value solve(const std::vector<Value>& values) {
    paired(values,1);
    return xor_candidate(values);
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto values=atlas_bit::read_values();
        atlas_bit::emit(atlas_bit::solve(values));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
