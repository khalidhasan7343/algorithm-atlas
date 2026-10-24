#include "../../common.hpp"

namespace atlas_bit {
inline std::vector<Value> partition_candidates(const std::vector<Value>& values) {
    sequence(values);
    require(values.size()>=2 && values.size()%2==0, "expected positive even length");
    Word total=0;
    for (Value value : values) total ^= static_cast<Word>(value);
    require(total!=0, "distinct singleton words must have nonzero XOR");
    const Word differing_bit=total & static_cast<Word>(Word{0}-total);
    Word first=0,second=0;
    for (Value value : values) {
        const Word word=static_cast<Word>(value);
        if (word & differing_bit) first ^= word;
        else second ^= word;
    }
    std::vector<Value> result={signed_value(first),signed_value(second)};
    if (result[0]>result[1]) std::swap(result[0],result[1]);
    return result;
}
inline std::vector<Value> solve(const std::vector<Value>& values) {
    paired(values,2);
    return partition_candidates(values);
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
