#include "../../common.hpp"
namespace atlas_window {
inline std::vector<Integer> longest_distinct(const std::string& text) {
    atlas_string::checked(text);
    std::array<Integer,256> last;last.fill(-1);
    Integer left=0,start=0,end=0;
    for (Integer right=0;right<static_cast<Integer>(text.size());++right) {
        int byte=atlas_string::byte(text[right]);
        left=std::max(left,last[byte]+1);
        last[byte]=right;
        if (right+1-left>end-start) {start=left;end=right+1;}
    }
    return {start,end};
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{auto text=atlas_string::read_bytes();atlas_string::end_input();atlas_window::emit(atlas_window::longest_distinct(text));std::cout<<'\n';}
catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
