#include "../../common.hpp"

namespace atlas_nt {
inline Integer gcd(Integer a,Integer b) {
    operand(a);operand(b);
    if (a<0) a=-a;
    if (b<0) b=-b;
    while (b) {Integer remainder=a%b;a=b;b=remainder;}
    return a;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(2);atlas_nt::emit(atlas_nt::gcd(values[0],values[1]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
