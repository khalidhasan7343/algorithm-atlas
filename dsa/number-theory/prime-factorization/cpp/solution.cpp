#include "../../common.hpp"
namespace atlas_nt {
inline std::vector<std::vector<Integer>> factorize(Integer value) {
    bounded(value,1,1000000000000LL);
    std::vector<std::vector<Integer>> factors;
    for (Integer divisor=2;divisor<=value/divisor;divisor=divisor==2?3:divisor+2) {
        Integer exponent=0;
        while (value%divisor==0) {value/=divisor;++exponent;}
        if (exponent) factors.push_back({divisor,exponent});
    }
    if (value>1) factors.push_back({value,1});
    return factors;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(1);atlas_nt::emit(atlas_nt::factorize(values[0]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
