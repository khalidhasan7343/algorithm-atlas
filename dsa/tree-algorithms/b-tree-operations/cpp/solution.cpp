#include "../../common.hpp"

namespace atlas_tree {

class BTree{
public:
    struct Node{bool leaf;std::vector<Integer> keys;std::vector<std::unique_ptr<Node>> children;explicit Node(bool is_leaf=true):leaf(is_leaf){}};
    std::array<Integer,7> stats{};
private:
    using Ptr=std::unique_ptr<Node>;int degree_;Ptr root_=std::make_unique<Node>();std::size_t size_=0;
    static std::size_t position(const Node& node,Integer key){return static_cast<std::size_t>(std::lower_bound(node.keys.begin(),node.keys.end(),key)-node.keys.begin());}
    void split(Node& parent,std::size_t i){
        auto& left=*parent.children[i];auto right=std::make_unique<Node>(left.leaf);Integer median=left.keys[degree_-1];
        right->keys.assign(left.keys.begin()+degree_,left.keys.end());left.keys.resize(degree_-1);
        if(!left.leaf){for(std::size_t j=degree_;j<left.children.size();++j)right->children.push_back(std::move(left.children[j]));left.children.resize(degree_);}
        parent.keys.insert(parent.keys.begin()+i,median);parent.children.insert(parent.children.begin()+i+1,std::move(right));++stats[0];
    }
    void insert_node(Node& node,Integer key){
        auto i=position(node,key);if(node.leaf){node.keys.insert(node.keys.begin()+i,key);return;}
        if(node.children[i]->keys.size()==static_cast<std::size_t>(2*degree_-1)){split(node,i);if(key>node.keys[i])++i;}
        insert_node(*node.children[i],key);
    }
    void merge(Node& parent,std::size_t i){
        auto& left=*parent.children[i];auto right=std::move(parent.children[i+1]);
        left.keys.push_back(parent.keys[i]);left.keys.insert(left.keys.end(),right->keys.begin(),right->keys.end());
        if(!left.leaf)for(auto& child:right->children)left.children.push_back(std::move(child));
        parent.keys.erase(parent.keys.begin()+i);parent.children.erase(parent.children.begin()+i+1);++stats[3];
    }
    std::size_t strengthen(Node& parent,std::size_t i){
        auto& child=*parent.children[i];
        if(i>0 && parent.children[i-1]->keys.size()>=static_cast<std::size_t>(degree_)){
            auto& left=*parent.children[i-1];child.keys.insert(child.keys.begin(),parent.keys[i-1]);parent.keys[i-1]=left.keys.back();left.keys.pop_back();
            if(!child.leaf){child.children.insert(child.children.begin(),std::move(left.children.back()));left.children.pop_back();}++stats[1];
        }else if(i<parent.keys.size() && parent.children[i+1]->keys.size()>=static_cast<std::size_t>(degree_)){
            auto& right=*parent.children[i+1];child.keys.push_back(parent.keys[i]);parent.keys[i]=right.keys.front();right.keys.erase(right.keys.begin());
            if(!child.leaf){child.children.push_back(std::move(right.children.front()));right.children.erase(right.children.begin());}++stats[2];
        }else{if(i==parent.keys.size())--i;merge(parent,i);}return i;
    }
    void erase_node(Node& node,Integer key){
        auto i=position(node,key);
        if(i<node.keys.size() && node.keys[i]==key){
            if(node.leaf)node.keys.erase(node.keys.begin()+i);
            else if(node.children[i]->keys.size()>=static_cast<std::size_t>(degree_)){
                const Node* p=node.children[i].get();while(!p->leaf)p=p->children.back().get();Integer replacement=p->keys.back();node.keys[i]=replacement;++stats[5];erase_node(*node.children[i],replacement);
            }else if(node.children[i+1]->keys.size()>=static_cast<std::size_t>(degree_)){
                const Node* p=node.children[i+1].get();while(!p->leaf)p=p->children.front().get();Integer replacement=p->keys.front();node.keys[i]=replacement;++stats[6];erase_node(*node.children[i+1],replacement);
            }else{merge(node,i);erase_node(*node.children[i],key);}
        }else{if(node.children[i]->keys.size()==static_cast<std::size_t>(degree_-1))i=strengthen(node,i);erase_node(*node.children[i],key);}
    }
    static void enumerate(const Node& node,std::vector<Integer>& result){for(std::size_t i=0;i<node.keys.size();++i){if(!node.leaf)enumerate(*node.children[i],result);result.push_back(node.keys[i]);}if(!node.leaf)enumerate(*node.children.back(),result);}
    static void range(const Node& node,Integer low,Integer high,std::vector<Integer>& result){
        auto i=position(node,low);if(!node.leaf)range(*node.children[i],low,high,result);
        while(i<node.keys.size() && node.keys[i]<high){result.push_back(node.keys[i]);++i;if(!node.leaf)range(*node.children[i],low,high,result);}
    }
public:
    explicit BTree(Integer degree=2):degree_(static_cast<int>(bounded(degree,2,8,"degree"))){}
    const Node* root()const{return root_.get();}std::size_t size()const{return size_;}int degree()const{return degree_;}
    bool contains(Integer key)const{key_checked(key);const Node* node=root_.get();while(true){auto i=position(*node,key);if(i<node->keys.size() && node->keys[i]==key)return true;if(node->leaf)return false;node=node->children[i].get();}}
    bool insert(Integer key){
        key_checked(key);if(contains(key))return false;require(size_<1000,"set capacity");
        if(root_->keys.size()==static_cast<std::size_t>(2*degree_-1)){auto parent=std::make_unique<Node>(false);parent->children.push_back(std::move(root_));root_=std::move(parent);split(*root_,0);}
        insert_node(*root_,key);++size_;return true;
    }
    bool erase(Integer key){key_checked(key);if(!contains(key))return false;erase_node(*root_,key);--size_;if(!root_->leaf && root_->keys.empty()){auto old=std::move(root_);root_=std::move(old->children[0]);++stats[4];}return true;}
    std::vector<Integer> keys()const{std::vector<Integer> result;enumerate(*root_,result);return result;}
    std::vector<Integer> range_query(Integer low,Integer high)const{key_checked(low);key_checked(high);require(low<=high,"invalid range");std::vector<Integer> result;if(low<high)range(*root_,low,high,result);return result;}
};
inline void b_tree_cli(bool final=true){BTree tree(token());ordered_cli(tree,final);}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
b_tree_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
