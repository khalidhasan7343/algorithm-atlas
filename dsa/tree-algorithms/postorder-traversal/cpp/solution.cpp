#include "../../common.hpp"

namespace atlas_tree {
inline std::vector<int> postorder(const BinaryTree& tree){
    std::vector<int> result;std::vector<std::pair<int,bool>> stack;if(tree.root!=-1)stack.push_back({tree.root,false});
    while(!stack.empty()){auto [u,returning]=stack.back();stack.pop_back();if(returning)result.push_back(u);else{stack.push_back({u,true});int left=tree.children[u][0],right=tree.children[u][1];if(right!=-1)stack.push_back({right,false});if(left!=-1)stack.push_back({left,false});}}
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
emit(postorder(read_binary()));
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
