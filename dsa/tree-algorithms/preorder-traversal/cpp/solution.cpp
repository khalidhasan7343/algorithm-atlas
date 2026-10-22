#include "../../common.hpp"

namespace atlas_tree {
inline std::vector<int> preorder(const BinaryTree& tree){
    std::vector<int> result,stack;if(tree.root!=-1)stack.push_back(tree.root);
    while(!stack.empty()){int u=stack.back();stack.pop_back();result.push_back(u);int left=tree.children[u][0],right=tree.children[u][1];if(right!=-1)stack.push_back(right);if(left!=-1)stack.push_back(left);}
    return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
emit(preorder(read_binary()));
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
