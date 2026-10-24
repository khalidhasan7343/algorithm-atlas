#include "../../common.hpp"

namespace atlas_string {
inline std::vector<int> prefix_function(const std::string& pattern) {
    checked(pattern);
    int m=static_cast<int>(pattern.size());
    std::vector<int> lps(m);
    for (int i=1; i<m; ++i) {
        int j=lps[i-1];
        while (j && pattern[i]!=pattern[j]) j=lps[j-1];
        if (pattern[i]==pattern[j]) ++j;
        lps[i]=j;
    }
    return lps;
}
inline std::vector<int> solve(const std::string& text, const std::string& pattern) {
    checked(text);
    auto lps=prefix_function(pattern);
    int n=static_cast<int>(text.size()), m=static_cast<int>(pattern.size());
    if (!m) return boundaries(n);
    std::vector<int> result;
    int j=0;
    for (int i=0; i<n; ++i) {
        while (j && text[i]!=pattern[j]) j=lps[j-1];
        if (text[i]==pattern[j]) ++j;
        if (j==m) { result.push_back(i-j+1); j=lps[j-1]; }
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
