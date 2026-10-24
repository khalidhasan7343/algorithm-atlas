#include "../../common.hpp"
#ifndef ALGORITHM_ATLAS_NO_MAIN
#define ATLAS_LCM_OWNS_MAIN
#define ALGORITHM_ATLAS_NO_MAIN
#endif
#include "../../euclidean-algorithm/cpp/solution.cpp"
#ifdef ATLAS_LCM_OWNS_MAIN
#undef ALGORITHM_ATLAS_NO_MAIN
#endif

namespace atlas_nt {
inline Integer lcm(Integer a,Integer b) {
    operand(a);operand(b);
    if (!a || !b) return 0;
    Integer divisor=atlas_nt::gcd(a,b);
    if (a<0) a=-a;
    if (b<0) b=-b;
    return (a/divisor)*b;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(2);atlas_nt::emit(atlas_nt::lcm(values[0],values[1]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
