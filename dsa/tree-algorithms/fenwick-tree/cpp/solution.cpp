#include "../../common.hpp"

namespace atlas_tree {

class FenwickTree{
    std::vector<Integer> values_,bit_;
public:
    explicit FenwickTree(const std::vector<Integer>& values):values_(values),bit_(values.size()+1,0){
        values_checked(values);for(std::size_t i=1;i<bit_.size();++i){bit_[i]+=values_[i-1];auto parent=i+(i&(~i+1));if(parent<bit_.size())bit_[parent]+=bit_[i];}
    }
    void add(Integer index,Integer delta){
        auto i=static_cast<std::size_t>(bounded(index,0,static_cast<Integer>(values_.size())-1,"invalid index"));bounded(delta,-2000000000LL,2000000000LL,"invalid delta");
        Integer value=bounded(values_[i]+delta,-1000000000,1000000000,"updated value outside contract");values_[i]=value;
        for(++i;i<bit_.size();i+=i&(~i+1))bit_[i]+=delta;
    }
    Integer prefix_sum(Integer end)const{
        auto i=static_cast<std::size_t>(bounded(end,0,static_cast<Integer>(values_.size()),"invalid prefix end"));Integer total=0;
        for(;i;i-=i&(~i+1))total+=bit_[i];return total;
    }
    Integer range_sum(Integer left,Integer right)const{bounded(left,0,static_cast<Integer>(values_.size()),"invalid left");bounded(right,left,static_cast<Integer>(values_.size()),"invalid right");return prefix_sum(right)-prefix_sum(left);}
};
inline void fenwick_cli(bool final=true){FenwickTree tree(read_values());int q=query_count();std::vector<std::optional<Integer>> result;
    for(int j=0;j<q;++j){Integer op=bounded(token(),0,2,"invalid operation"),first=token();if(op==0){Integer delta=token();tree.add(first,delta);result.push_back(std::nullopt);}else if(op==1)result.push_back(tree.prefix_sum(first));else{Integer right=token();result.push_back(tree.range_sum(first,right));}}
    if(final)end_input();emit(result);
}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
fenwick_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
