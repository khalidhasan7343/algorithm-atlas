#ifndef ATLAS_WINDOW_COMMON_HPP
#define ATLAS_WINDOW_COMMON_HPP
#include "../string-algorithms/common.hpp"
#include <charconv>
#include <deque>
#include <system_error>

namespace atlas_window {
using Integer=std::int64_t;
using atlas_string::require;
using atlas_string::emit;
inline void bounded(Integer value,Integer low,Integer high) {
    require(value>=low && value<=high,"integer outside supported range");
}
inline void array_checked(const std::vector<Integer>& values) {
    require(values.size()<=10000,"too many values");
    for (Integer value:values) bounded(value,-1000000000LL,1000000000LL);
}
inline std::vector<Integer> read_numbers() {
    std::vector<Integer> values;
    std::string token;
    while (std::cin>>token) {
        require(values.size()<10001 && token.size()<=20,"input size limit");
        std::size_t first=(token[0]=='+' || token[0]=='-')?1:0;
        require(first<token.size(),"missing digits");
        for (std::size_t i=first;i<token.size();++i)
            require(token[i]>='0' && token[i]<='9',"expected decimal integer");
        Integer value=0;
        const char* begin=token.data()+(token[0]=='+');
        auto parsed=std::from_chars(begin,token.data()+token.size(),value,10);
        require(parsed.ec==std::errc{} && parsed.ptr==token.data()+token.size(),"invalid integer");
        values.push_back(value);
    }
    require(!values.empty(),"missing scalar prefix");
    return values;
}
}
#endif
