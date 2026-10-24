#include "../../common.hpp"
namespace atlas_window {
inline std::vector<Integer> sliding_max(const std::vector<Integer>& values,Integer k) {
    array_checked(values);bounded(k,0,10000);
    if (values.empty()) {require(k==0,"empty input requires k=0");return {};}
    require(k>=1 && k<=static_cast<Integer>(values.size()),"window size must be in 1..n");
    std::size_t window=static_cast<std::size_t>(k);
    std::deque<std::size_t> queue;
    std::vector<Integer> result;
    for (std::size_t index=0;index<values.size();++index) {
        while (!queue.empty() && queue.front()+window<=index) queue.pop_front();
        while (!queue.empty() && values[queue.back()]<=values[index]) queue.pop_back();
        queue.push_back(index);
        if (index+1>=window) result.push_back(values[queue.front()]);
    }
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto input=atlas_window::read_numbers();auto k=input[0];input.erase(input.begin());atlas_window::emit(atlas_window::sliding_max(input,k));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
