#ifndef ALGORITHM_ATLAS_TREE_COMMON_HPP
#define ALGORITHM_ATLAS_TREE_COMMON_HPP
#include <algorithm>
#include <array>
#include <charconv>
#include <deque>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <numeric>
#include <optional>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>
namespace atlas_tree {
using Integer=long long;
static_assert(std::numeric_limits<Integer>::digits>=63,"64-bit integers required");
inline void require(bool condition,const char* message){if(!condition)throw std::invalid_argument(message);}
inline Integer bounded(Integer value,Integer low,Integer high,const char* message){require(low<=value && value<=high,message);return value;}
inline Integer token(){
    std::string text;require(static_cast<bool>(std::cin>>text),"missing integer");Integer value=0;
    auto parsed=std::from_chars(text.data(),text.data()+text.size(),value);
    require(parsed.ec==std::errc{} && parsed.ptr==text.data()+text.size(),"invalid integer");return value;
}
inline void end_input(){std::string extra;require(!(std::cin>>extra),"trailing input");}
inline void emit(int value){std::cout<<value;}
inline void emit(Integer value){std::cout<<value;}
inline void emit(bool value){std::cout<<(value?"true":"false");}
inline void emit(const std::string& value){std::cout<<std::quoted(value);}
template<class T> inline void emit(const std::optional<T>& value){if(value)emit(*value);else std::cout<<"null";}
template<class T> inline void emit(const std::vector<T>& values){std::cout<<'[';for(std::size_t i=0;i<values.size();++i){if(i)std::cout<<',';emit(values[i]);}std::cout<<']';}
inline void values_checked(const std::vector<Integer>& values){require(values.size()<=10000,"too many values");for(auto value:values)bounded(value,-1000000000,1000000000,"value outside contract");}
struct BinaryTree{std::vector<Integer> values;std::vector<std::array<int,2>> children;int root;};
inline BinaryTree binary_tree(const std::vector<Integer>& values,const std::vector<std::array<Integer,2>>& children,Integer root){
    values_checked(values);int n=static_cast<int>(values.size());require(children.size()==values.size(),"one child pair per node required");
    BinaryTree tree{values,{},-1};std::vector<int> degree(n,0);
    for(const auto& pair:children){std::array<int,2> copied{};
        for(int slot=0;slot<2;++slot){auto child=pair[slot];bounded(child,-1,n-1,"invalid child");copied[slot]=static_cast<int>(child);if(child!=-1)require(++degree[static_cast<int>(child)]==1,"shared child");}
        tree.children.push_back(copied);
    }
    if(n==0){require(root==-1,"empty tree requires absent root");return tree;}
    tree.root=static_cast<int>(bounded(root,0,n-1,"invalid root"));require(degree[tree.root]==0,"root has a parent");
    std::vector<bool> seen(n,false);std::vector<int> stack{tree.root};int count=0;
    while(!stack.empty()){int u=stack.back();stack.pop_back();require(!seen[u],"cycle");seen[u]=true;++count;for(int v:tree.children[u])if(v!=-1)stack.push_back(v);}
    require(count==n,"tree must be connected");return tree;
}
inline BinaryTree read_binary(bool final=true){
    int n=static_cast<int>(bounded(token(),0,10000,"invalid n"));Integer root=token();
    std::vector<Integer> values;std::vector<std::array<Integer,2>> children;
    for(int i=0;i<n;++i)values.push_back(token());
    for(int i=0;i<n;++i){Integer left=token(),right=token();children.push_back({left,right});}
    if(final)end_input();return binary_tree(values,children,root);
}
struct RootedTree{std::vector<int> parent,depth;std::vector<std::vector<int>> children;int root;};
inline RootedTree rooted_tree(const std::vector<Integer>& parents,Integer root){
    require(parents.size()<=10000,"too many parents");int n=static_cast<int>(parents.size());RootedTree tree{{},std::vector<int>(n,-1),std::vector<std::vector<int>>(n),-1};
    if(!n){require(root==-1,"empty tree requires absent root");return tree;}
    tree.root=static_cast<int>(bounded(root,0,n-1,"invalid root"));
    for(int v=0;v<n;++v){Integer p=parents[v];if(v==tree.root)require(p==-1,"root parent must be absent");else bounded(p,0,n-1,"invalid parent");tree.parent.push_back(static_cast<int>(p));if(v!=tree.root)tree.children[static_cast<int>(p)].push_back(v);}
    tree.depth[tree.root]=0;std::vector<int> stack{tree.root};int count=0;
    while(!stack.empty()){int u=stack.back();stack.pop_back();++count;for(int v:tree.children[u]){require(tree.depth[v]==-1,"cycle");tree.depth[v]=tree.depth[u]+1;stack.push_back(v);}}
    require(count==n,"disconnected/cyclic parent relation");return tree;
}
inline RootedTree read_rooted(){int n=static_cast<int>(bounded(token(),0,10000,"invalid n"));Integer root=token();std::vector<Integer> parents;for(int i=0;i<n;++i)parents.push_back(token());return rooted_tree(parents,root);}
inline std::vector<Integer> read_values(){int n=static_cast<int>(bounded(token(),0,10000,"invalid n"));std::vector<Integer> values;for(int i=0;i<n;++i)values.push_back(token());values_checked(values);return values;}
inline int query_count(){return static_cast<int>(bounded(token(),0,1000,"invalid query count"));}

inline Integer key_checked(Integer key){return bounded(key,-1000000000,1000000000,"key outside contract");}
template<class Tree> inline void ordered_cli(Tree& tree,bool final=true){
    int q=query_count();
    std::cout<<'[';
    for(int i=0;i<q;++i){
        if(i)std::cout<<',';
        Integer op=bounded(token(),0,4,"invalid operation");
        if(op==3)emit(tree.keys());
        else {Integer key=token();if(op==0)emit(tree.insert(key));else if(op==1)emit(tree.erase(key));else if(op==2)emit(tree.contains(key));else{Integer high=token();emit(tree.range_query(key,high));}}
    }
    if(final)end_input();std::cout<<']';
}
} // namespace atlas_tree
#endif
