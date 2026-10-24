#ifndef ATLAS_NUMBER_COMMON_HPP
#define ATLAS_NUMBER_COMMON_HPP
#include <algorithm>
#include <charconv>
#include <cstdint>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <system_error>
#include <vector>

namespace atlas_nt {
using Integer=std::int64_t;
inline void require(bool ok, const char* message) {
    if (!ok) throw std::invalid_argument(message);
}
inline void bounded(Integer value, Integer low, Integer high) {
    require(value>=low && value<=high, "integer outside supported range");
}
inline void operand(Integer value) {bounded(value,-1000000000LL,1000000000LL);}
inline std::vector<Integer> read_numbers(std::size_t arity) {
    std::vector<Integer> values;
    std::string token;
    while (std::cin>>token) {
        require(values.size()<arity && token.size()<=20, "incorrect input size");
        std::size_t first=(token[0]=='+' || token[0]=='-')?1:0;
        require(first<token.size(),"missing digits");
        for (std::size_t i=first;i<token.size();++i)
            require(token[i]>='0' && token[i]<='9',"expected decimal digits");
        Integer value=0;
        auto begin=token.data()+(token[0]=='+');
        auto parsed=std::from_chars(begin,token.data()+token.size(),value,10);
        require(parsed.ec==std::errc{} && parsed.ptr==token.data()+token.size(),"invalid integer");
        values.push_back(value);
    }
    require(values.size()==arity,"missing input");
    return values;
}
inline void emit(Integer value) {std::cout<<value;}
template<class T> void emit(const std::vector<T>& values) {
    std::cout<<'[';
    for (std::size_t i=0;i<values.size();++i) {if (i) std::cout<<',';emit(values[i]);}
    std::cout<<']';
}
}
#endif
