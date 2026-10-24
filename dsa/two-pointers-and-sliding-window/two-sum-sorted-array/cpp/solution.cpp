#include "../../common.hpp"
namespace atlas_window {
inline std::vector<Integer> two_sum(const std::vector<Integer>& values,Integer target) {
    array_checked(values);bounded(target,-2000000000LL,2000000000LL);
    for (std::size_t i=1;i<values.size();++i) require(values[i-1]<=values[i],"values must be sorted");
    Integer left=0,right=static_cast<Integer>(values.size())-1;
    while (left<right) {
        Integer total=values[left]+values[right];
        if (total<target) ++left;
        else if (total>target) --right;
        else {
            while (right>left+1 && values[right-1]==values[right]) --right;
            return {left,right};
        }
    }
    return {};
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto input=atlas_window::read_numbers();auto target=input[0];input.erase(input.begin());
atlas_window::emit(atlas_window::two_sum(input,target));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
