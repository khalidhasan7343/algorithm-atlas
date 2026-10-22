#include "../../common.hpp"

namespace atlas_tree {

class LCA{
    RootedTree tree_;
public:
    explicit LCA(RootedTree tree):tree_(std::move(tree)){}
    int query(Integer first,Integer second)const{
        int n=static_cast<int>(tree_.parent.size());int a=static_cast<int>(bounded(first,0,n-1,"invalid vertex")),b=static_cast<int>(bounded(second,0,n-1,"invalid vertex"));
        while(tree_.depth[a]>tree_.depth[b])a=tree_.parent[a];while(tree_.depth[b]>tree_.depth[a])b=tree_.parent[b];
        while(a!=b){a=tree_.parent[a];b=tree_.parent[b];}return a;
    }
};
inline void lca_cli(bool final=true){auto tree=read_rooted();LCA index(std::move(tree));int q=query_count();std::vector<int> result;for(int i=0;i<q;++i){Integer a=token(),b=token();result.push_back(index.query(a,b));}if(final)end_input();emit(result);}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
lca_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
