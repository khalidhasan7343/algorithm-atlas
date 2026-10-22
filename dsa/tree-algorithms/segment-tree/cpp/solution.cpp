#include "../../common.hpp"

namespace atlas_tree {

class SegmentTree{
    std::size_t n_,base_=1;std::vector<Integer> tree_;
public:
    explicit SegmentTree(const std::vector<Integer>& values):n_(values.size()){
        values_checked(values);while(base_<n_)base_*=2;tree_.assign(2*base_,0);std::copy(values.begin(),values.end(),tree_.begin()+static_cast<std::ptrdiff_t>(base_));
        for(std::size_t u=base_-1;u>0;--u)tree_[u]=tree_[2*u]+tree_[2*u+1];
    }
    void set(Integer index,Integer value){
        auto u=base_+static_cast<std::size_t>(bounded(index,0,static_cast<Integer>(n_)-1,"invalid index"));bounded(value,-1000000000,1000000000,"value outside contract");tree_[u]=value;
        for(u/=2;u;u/=2)tree_[u]=tree_[2*u]+tree_[2*u+1];
    }
    Integer range_sum(Integer left,Integer right)const{
        bounded(left,0,static_cast<Integer>(n_),"invalid left");bounded(right,left,static_cast<Integer>(n_),"invalid right");
        auto l=base_+static_cast<std::size_t>(left),r=base_+static_cast<std::size_t>(right);Integer total=0;
        while(l<r){if(l&1)total+=tree_[l++];if(r&1)total+=tree_[--r];l/=2;r/=2;}return total;
    }
};
inline void segment_cli(bool final=true){SegmentTree tree(read_values());int q=query_count();std::vector<std::optional<Integer>> result;
    for(int j=0;j<q;++j){Integer op=bounded(token(),0,1,"invalid operation"),a=token(),b=token();if(op==0){tree.set(a,b);result.push_back(std::nullopt);}else result.push_back(tree.range_sum(a,b));}
    if(final)end_input();emit(result);
}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
segment_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
