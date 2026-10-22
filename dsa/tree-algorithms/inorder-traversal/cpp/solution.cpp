#include "../../common.hpp"

namespace atlas_tree {
inline std::vector<int> inorder(const BinaryTree& tree){
    std::vector<int> result,stack;int current=tree.root;
    while(!stack.empty() || current!=-1){
        while(current!=-1){stack.push_back(current);current=tree.children[current][0];}
        current=stack.back();stack.pop_back();result.push_back(current);current=tree.children[current][1];
    }return result;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
emit(inorder(read_binary()));
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
