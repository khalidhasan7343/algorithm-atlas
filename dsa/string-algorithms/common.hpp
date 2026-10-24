#ifndef ATLAS_STRING_COMMON_HPP
#define ATLAS_STRING_COMMON_HPP
#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <queue>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace atlas_string {
inline void require(bool ok, const char* message) {
    if (!ok) throw std::invalid_argument(message);
}
inline void checked(const std::string& s, std::size_t limit=10000) {
    require(s.size() <= limit, "byte string too long");
}
inline int byte(char ch) { return static_cast<unsigned char>(ch); }
inline std::string read_bytes() {
    std::string token;
    require(static_cast<bool>(std::cin >> token), "missing hex string");
    if (token == "-") return {};
    require(token.size() <= 20000 && token.size() % 2 == 0, "invalid hex length");
    auto digit=[](char ch) {
        if (ch >= '0' && ch <= '9') return ch-'0';
        if (ch >= 'a' && ch <= 'f') return ch-'a'+10;
        if (ch >= 'A' && ch <= 'F') return ch-'A'+10;
        throw std::invalid_argument("invalid hex digit");
    };
    std::string result;
    for (std::size_t i=0; i<token.size(); i+=2)
        result.push_back(static_cast<char>(16*digit(token[i])+digit(token[i+1])));
    return result;
}
inline int read_count() {
    std::string token;
    require(static_cast<bool>(std::cin >> token), "missing pattern count");
    int value=0;
    for (char ch:token) {
        require(ch >= '0' && ch <= '9', "invalid pattern count");
        value=value*10+(ch-'0');
        require(value<=256, "pattern count too large");
    }
    return value;
}
inline void end_input() {
    std::string extra;
    require(!(std::cin >> extra), "extra input");
}
inline void emit(int value) { std::cout << value; }
template<class T> void emit(const std::vector<T>& values) {
    std::cout << '[';
    for (std::size_t i=0; i<values.size(); ++i) {
        if (i) std::cout << ',';
        emit(values[i]);
    }
    std::cout << ']';
}
inline std::vector<int> boundaries(int n) {
    std::vector<int> result(n+1);
    std::iota(result.begin(),result.end(),0);
    return result;
}
}
#endif
