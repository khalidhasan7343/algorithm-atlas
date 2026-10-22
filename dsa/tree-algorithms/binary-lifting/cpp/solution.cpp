#include "../../common.hpp"

namespace atlas_tree {

class BinaryLifting{
    std::vector<std::vector<int>> up_;std::vector<int> depth_;
public:
    explicit BinaryLifting(const RootedTree& tree):up_{tree.parent},depth_(tree.depth){
        std::size_t levels=1;while((std::size_t{1}<<levels)<tree.parent.size()+1)++levels;
        for(std::size_t j=1;j<levels;++j){const auto& previous=up_.back();std::vector<int> next;for(int p:previous)next.push_back(p==-1?-1:previous[p]);up_.push_back(std::move(next));}
    }
    std::optional<int> kth_ancestor(Integer vertex,Integer k)const{
        int v=static_cast<int>(bounded(vertex,0,static_cast<Integer>(depth_.size())-1,"invalid vertex"));bounded(k,0,1000000000000000000LL,"invalid k");
        if(k>depth_[v])return std::nullopt;std::size_t bit=0;
        while(k){if(k&1)v=up_[bit][v];k>>=1;++bit;}return v;
    }
    int lca(Integer first,Integer second)const{
        int n=static_cast<int>(depth_.size());int a=static_cast<int>(bounded(first,0,n-1,"invalid vertex")),b=static_cast<int>(bounded(second,0,n-1,"invalid vertex"));
        if(depth_[a]<depth_[b])std::swap(a,b);a=*kth_ancestor(a,depth_[a]-depth_[b]);if(a==b)return a;
        for(auto it=up_.rbegin();it!=up_.rend();++it)if((*it)[a]!=(*it)[b]){a=(*it)[a];b=(*it)[b];}return up_[0][a];
    }
};
inline void lifting_cli(bool final=true){auto tree=read_rooted();BinaryLifting index(tree);int q=query_count();std::vector<std::optional<int>> result;
    for(int i=0;i<q;++i){Integer op=bounded(token(),0,1,"invalid operation"),a=token(),b=token();result.push_back(op==0?index.kth_ancestor(a,b):std::optional<int>(index.lca(a,b)));}
    if(final)end_input();emit(result);
}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
lifting_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
