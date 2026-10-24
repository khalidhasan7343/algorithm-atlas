#include "../../common.hpp"
namespace atlas_nt {
inline std::uint64_t magnitude(Integer value) {
    return value>=0 ? static_cast<std::uint64_t>(value)
                    : static_cast<std::uint64_t>(-(value+1))+1;
}
inline Integer checked_multiply(Integer a,Integer b) {
    bool negative=(a<0)!=(b<0);
    auto ma=magnitude(a),mb=magnitude(b);
    const std::uint64_t high=std::uint64_t{1}<<63;
    const std::uint64_t limit=negative?high:static_cast<std::uint64_t>(std::numeric_limits<Integer>::max());
    require(ma==0 || mb<=limit/ma,"power does not fit signed 64-bit result");
    auto product=ma*mb;
    if (negative && product==high) return std::numeric_limits<Integer>::min();
    Integer signed_product=static_cast<Integer>(product);
    return negative?-signed_product:signed_product;
}
inline Integer power(Integer base,Integer exponent) {
    operand(base);bounded(exponent,0,1000000000LL);
    Integer result=1;
    while (exponent) {
        if (exponent&1) result=checked_multiply(result,base);
        exponent>>=1;
        if (exponent) base=checked_multiply(base,base);
    }
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(2);atlas_nt::emit(atlas_nt::power(values[0],values[1]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
