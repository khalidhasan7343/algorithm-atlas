#include "../../common.hpp"

namespace atlas_string {
inline std::vector<int> bad_character(const std::string& pattern) {
    checked(pattern);
    std::vector<int> last(256,-1);
    for (int i=0; i<static_cast<int>(pattern.size()); ++i) last[byte(pattern[i])]=i;
    return last;
}
inline std::vector<int> good_suffix(const std::string& pattern) {
    checked(pattern);
    int m=static_cast<int>(pattern.size()),i=m,j=m+1;
    std::vector<int> shift(m+1),border(m+1);
    border[i]=j;
    while (i>0) {
        while (j<=m && pattern[i-1]!=pattern[j-1]) {
            if (!shift[j]) shift[j]=j-i;
            j=border[j];
        }
        --i; --j; border[i]=j;
    }
    j=border[0];
    for (i=0; i<=m; ++i) {
        if (!shift[i]) shift[i]=j;
        if (i==j) j=border[j];
    }
    return shift;
}
inline std::vector<int> solve(const std::string& text, const std::string& pattern) {
    checked(text); checked(pattern);
    int n=static_cast<int>(text.size()),m=static_cast<int>(pattern.size());
    if (!m) return boundaries(n);
    auto last=bad_character(pattern),good=good_suffix(pattern);
    std::vector<int> result;
    for (int start=0; start<=n-m;) {
        int j=m-1;
        while (j>=0 && pattern[j]==text[start+j]) --j;
        if (j<0) { result.push_back(start); start+=good[0]; }
        else start+=std::max({1,j-last[byte(text[start+j])],good[j+1]});
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
