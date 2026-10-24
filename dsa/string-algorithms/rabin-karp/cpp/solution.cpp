#include "../../common.hpp"

namespace atlas_string {
constexpr std::int64_t BASE=257, MODULUS=1000000007;
inline void parameters(std::int64_t base, std::int64_t modulus) {
    require(base>=1 && base<=1000000007 && modulus>=2 && modulus<=1000000007,
            "invalid rolling hash parameters");
}
inline std::int64_t fingerprint(const std::string& data, std::int64_t base=BASE,
                                std::int64_t modulus=MODULUS) {
    checked(data); parameters(base,modulus);
    std::int64_t value=0;
    for (char ch:data) value=(value*base+byte(ch)+1)%modulus;
    return value;
}
inline std::vector<int> solve(const std::string& text, const std::string& pattern,
                             std::int64_t base=BASE, std::int64_t modulus=MODULUS) {
    checked(text); checked(pattern); parameters(base,modulus);
    int n=static_cast<int>(text.size()), m=static_cast<int>(pattern.size());
    if (!m) return boundaries(n);
    if (m>n) return {};
    std::int64_t high=1;
    for (int i=1; i<m; ++i) high=high*base%modulus;
    auto target=fingerprint(pattern,base,modulus);
    auto window=fingerprint(text.substr(0,m),base,modulus);
    std::vector<int> result;
    for (int start=0; start<=n-m; ++start) {
        if (window==target) {
            int j=0;
            while (j<m && text[start+j]==pattern[j]) ++j;
            if (j==m) result.push_back(start);
        }
        if (start+m<n) {
            auto removed=(byte(text[start])+1)*high%modulus;
            window=(window-removed+modulus)%modulus;
            window=(window*base+byte(text[start+m])+1)%modulus;
        }
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
