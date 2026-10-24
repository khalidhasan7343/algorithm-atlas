#include "../../common.hpp"

namespace atlas_string {
inline std::vector<std::vector<int>> radii(const std::string& text) {
    checked(text);
    int n=static_cast<int>(text.size()),left=0,right=-1;
    std::vector<int> odd(n),even(n);
    for (int i=0; i<n; ++i) {
        int k=i>right?1:std::min(odd[left+right-i],right-i+1);
        while (i-k>=0 && i+k<n && text[i-k]==text[i+k]) ++k;
        odd[i]=k;
        if (i+k-1>right) { left=i-k+1; right=i+k-1; }
    }
    left=0; right=-1;
    for (int i=0; i<n; ++i) {
        int k=i>right?0:std::min(even[left+right-i+1],right-i+1);
        while (i-k-1>=0 && i+k<n && text[i-k-1]==text[i+k]) ++k;
        even[i]=k;
        if (i+k-1>right) { left=i-k; right=i+k-1; }
    }
    return {odd,even};
}
inline std::vector<std::vector<int>> solve(const std::string& text) {
    auto result=radii(text);
    int start=0,end=0;
    auto consider=[&](int a,int b) {
        if (b-a>end-start || (b-a==end-start && a<start)) { start=a; end=b; }
    };
    for (int i=0; i<static_cast<int>(text.size()); ++i) {
        consider(i-result[0][i]+1,i+result[0][i]);
        consider(i-result[1][i],i+result[1][i]);
    }
    result.push_back({start,end});
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto text=atlas_string::read_bytes();
        atlas_string::end_input();
        atlas_string::emit(atlas_string::solve(text));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
