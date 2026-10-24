#include "../../common.hpp"

namespace atlas_string {
inline std::vector<int> z_values(const std::vector<int>& values) {
    int n=static_cast<int>(values.size()),left=0,right=0;
    std::vector<int> z(n);
    for (int i=1; i<n; ++i) {
        if (i<right) z[i]=std::min(right-i,z[i-left]);
        while (i+z[i]<n && values[z[i]]==values[i+z[i]]) ++z[i];
        if (i+z[i]>right) { left=i; right=i+z[i]; }
    }
    return z;
}
inline std::vector<int> z_array(const std::string& text) {
    checked(text);
    std::vector<int> values;
    for (char ch:text) values.push_back(byte(ch));
    return z_values(values);
}
inline std::vector<int> solve(const std::string& text, const std::string& pattern) {
    checked(text); checked(pattern);
    int n=static_cast<int>(text.size()), m=static_cast<int>(pattern.size());
    if (!m) return boundaries(n);
    std::vector<int> values;
    for (char ch:pattern) values.push_back(byte(ch));
    values.push_back(256);
    for (char ch:text) values.push_back(byte(ch));
    auto z=z_values(values);
    std::vector<int> result;
    for (int i=m+1; i<static_cast<int>(values.size()); ++i)
        if (z[i]>=m) result.push_back(i-m-1);
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
