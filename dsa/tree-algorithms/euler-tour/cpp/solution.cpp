#include "../../common.hpp"

namespace atlas_tree {

struct EulerTour{std::vector<int> order,tin,tout;};
inline EulerTour euler_tour(const RootedTree& tree){
    EulerTour r{{},std::vector<int>(tree.parent.size()),std::vector<int>(tree.parent.size())};std::vector<std::pair<int,bool>> stack;
    if(tree.root!=-1)stack.push_back({tree.root,false});
    while(!stack.empty()){auto [u,exiting]=stack.back();stack.pop_back();if(exiting)r.tout[u]=static_cast<int>(r.order.size());else{r.tin[u]=static_cast<int>(r.order.size());r.order.push_back(u);stack.push_back({u,true});for(auto it=tree.children[u].rbegin();it!=tree.children[u].rend();++it)stack.push_back({*it,false});}}
    return r;
}
inline void emit(const EulerTour& r){std::cout<<"{\"order\":";emit(r.order);std::cout<<",\"tin\":";emit(r.tin);std::cout<<",\"tout\":";emit(r.tout);std::cout<<'}';}
inline void euler_cli(bool final=true){auto tree=read_rooted();if(final)end_input();emit(euler_tour(tree));}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
euler_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
