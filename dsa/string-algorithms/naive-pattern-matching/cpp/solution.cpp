#include "../../common.hpp"

namespace atlas_string {
inline std::vector<int> solve(const std::string& text, const std::string& pattern) {
    checked(text); checked(pattern);
    int n=static_cast<int>(text.size()), m=static_cast<int>(pattern.size());
    std::vector<int> result;
    for (int start=0; start<=n-m; ++start) {
        int j=0;
        while (j<m && text[start+j]==pattern[j]) ++j;
        if (j==m) result.push_back(start);
    }
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto text=atlas_string::read_bytes();
        auto pattern=atlas_string::read_bytes();
        atlas_string::end_input();
        atlas_string::emit(atlas_string::solve(text,pattern));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
