#include "../../common.hpp"
namespace atlas_nt {
inline std::vector<Integer> extended_gcd(Integer a,Integer b) {
    operand(a);operand(b);
    if (!a && !b) return {0,0,0};
    Integer old_r=a<0?-a:a,r=b<0?-b:b;
    Integer old_x=1,x=0,old_y=0,y=1;
    while (r) {
        Integer quotient=old_r/r;
        Integer next_r=old_r-quotient*r;old_r=r;r=next_r;
        Integer next_x=old_x-quotient*x;old_x=x;x=next_x;
        Integer next_y=old_y-quotient*y;old_y=y;y=next_y;
    }
    return {old_r,a<0?-old_x:old_x,b<0?-old_y:old_y};
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto values=atlas_nt::read_numbers(2);atlas_nt::emit(atlas_nt::extended_gcd(values[0],values[1]));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
