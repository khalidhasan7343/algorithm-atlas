#include "../../common.hpp"
namespace atlas_nt {
inline Integer mod_power(Integer base,Integer exponent,Integer modulus) {
    operand(base);bounded(exponent,0,1000000000LL);bounded(modulus,1,1000000007LL);
    base%=modulus;
    if (base<0) base+=modulus;
    Integer result=1%modulus;
    while (exponent) {
        if (exponent&1) result=(result*base)%modulus;
        exponent>>=1;
        if (exponent) base=(base*base)%modulus;
    }
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(3);atlas_nt::emit(atlas_nt::mod_power(values[0],values[1],values[2]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
