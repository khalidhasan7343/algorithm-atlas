#include "../../common.hpp"

namespace atlas_tree {
inline std::vector<std::vector<int>> level_order(const BinaryTree& tree){
    std::vector<std::vector<int>> levels;std::deque<int> queue;if(tree.root!=-1)queue.push_back(tree.root);
    while(!queue.empty()){std::vector<int> level;auto width=queue.size();for(std::size_t i=0;i<width;++i){int u=queue.front();queue.pop_front();level.push_back(u);for(int child:tree.children[u])if(child!=-1)queue.push_back(child);}levels.push_back(level);}
    return levels;
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
emit(level_order(read_binary()));
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
