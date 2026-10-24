#include "../../common.hpp"

namespace atlas_bit {
inline std::vector<std::vector<Value>> solve(const std::vector<Value>& values) {
    sequence(values,16);
    const Word limit=Word{1} << values.size();
    std::vector<std::vector<Value>> result;
    result.reserve(limit);
    for (Word mask=0; mask<limit; ++mask) {
        std::vector<Value> row;
        for (std::size_t index=0; index<values.size(); ++index)
            if (mask & (Word{1} << index)) row.push_back(values[index]);
        result.push_back(std::move(row));
    }
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto values=atlas_bit::read_values(16);
        atlas_bit::emit(atlas_bit::solve(values));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
