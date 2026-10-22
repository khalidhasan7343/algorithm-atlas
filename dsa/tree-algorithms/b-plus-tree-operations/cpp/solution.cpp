#include "../../common.hpp"

namespace atlas_tree {

class BPlusTree{
public:
    struct Node{bool leaf;std::vector<Integer> keys;std::vector<std::unique_ptr<Node>> children;Node* next=nullptr;std::optional<Integer> minimum;explicit Node(bool is_leaf=true):leaf(is_leaf){}};
    std::array<Integer,6> stats{};
private:
    using Ptr=std::unique_ptr<Node>;int degree_;Ptr root_=std::make_unique<Node>();std::size_t size_=0;
    static std::size_t position(const Node& node,Integer key){return static_cast<std::size_t>(std::upper_bound(node.keys.begin(),node.keys.end(),key)-node.keys.begin());}
    static void refresh(Node& node){
        if(node.leaf){node.minimum=node.keys.empty()?std::optional<Integer>{}:std::optional<Integer>{node.keys.front()};return;}
        node.minimum=node.children.front()->minimum;node.keys.clear();for(std::size_t i=1;i<node.children.size();++i){require(node.children[i]->minimum.has_value(),"empty internal child");node.keys.push_back(*node.children[i]->minimum);}
    }
    const Node* leaf(Integer key)const{const Node* node=root_.get();while(!node->leaf)node=node->children[position(*node,key)].get();return node;}
    Ptr insert_node(Node& node,Integer key){
        if(node.leaf){
            node.keys.insert(std::lower_bound(node.keys.begin(),node.keys.end(),key),key);refresh(node);if(node.keys.size()<static_cast<std::size_t>(2*degree_))return nullptr;
            auto right=std::make_unique<Node>();right->keys.assign(node.keys.begin()+degree_,node.keys.end());node.keys.resize(degree_);right->next=node.next;node.next=right.get();refresh(node);refresh(*right);++stats[0];return right;
        }
        auto i=position(node,key);auto right=insert_node(*node.children[i],key);if(right)node.children.insert(node.children.begin()+i+1,std::move(right));refresh(node);
        if(node.children.size()<=static_cast<std::size_t>(2*degree_))return nullptr;
        right=std::make_unique<Node>(false);for(std::size_t j=degree_;j<node.children.size();++j)right->children.push_back(std::move(node.children[j]));node.children.resize(degree_);refresh(node);refresh(*right);++stats[1];return right;
    }
    bool underfull(const Node& node)const{return node.leaf?node.keys.size()<static_cast<std::size_t>(degree_-1):node.children.size()<static_cast<std::size_t>(degree_);}
    bool spare(const Node& node)const{return node.leaf?node.keys.size()>static_cast<std::size_t>(degree_-1):node.children.size()>static_cast<std::size_t>(degree_);}
    void repair(Node& parent,std::size_t i){
        auto& child=*parent.children[i];
        if(i>0 && spare(*parent.children[i-1])){
            auto& left=*parent.children[i-1];if(child.leaf){child.keys.insert(child.keys.begin(),left.keys.back());left.keys.pop_back();}
            else{child.children.insert(child.children.begin(),std::move(left.children.back()));left.children.pop_back();}refresh(left);refresh(child);++stats[2];
        }else if(i+1<parent.children.size() && spare(*parent.children[i+1])){
            auto& right=*parent.children[i+1];if(child.leaf){child.keys.push_back(right.keys.front());right.keys.erase(right.keys.begin());}
            else{child.children.push_back(std::move(right.children.front()));right.children.erase(right.children.begin());}refresh(right);refresh(child);++stats[3];
        }else{
            if(i==parent.children.size()-1)--i;
            auto& left=*parent.children[i];auto right=std::move(parent.children[i+1]);
            if(left.leaf){left.keys.insert(left.keys.end(),right->keys.begin(),right->keys.end());left.next=right->next;}
            else for(auto& item:right->children)left.children.push_back(std::move(item));
            parent.children.erase(parent.children.begin()+i+1);refresh(left);++stats[4];
        }refresh(parent);
    }
    void erase_node(Node& node,Integer key){
        if(node.leaf){node.keys.erase(std::lower_bound(node.keys.begin(),node.keys.end(),key));refresh(node);return;}
        auto i=position(node,key);erase_node(*node.children[i],key);if(underfull(*node.children[i]))repair(node,i);refresh(node);
    }
public:
    explicit BPlusTree(Integer degree=2):degree_(static_cast<int>(bounded(degree,2,8,"degree"))){}
    const Node* root()const{return root_.get();}std::size_t size()const{return size_;}int degree()const{return degree_;}
    bool contains(Integer key)const{key_checked(key);const Node* node=leaf(key);auto it=std::lower_bound(node->keys.begin(),node->keys.end(),key);return it!=node->keys.end() && *it==key;}
    bool insert(Integer key){
        key_checked(key);if(contains(key))return false;require(size_<1000,"set capacity");auto right=insert_node(*root_,key);
        if(right){auto parent=std::make_unique<Node>(false);parent->children.push_back(std::move(root_));parent->children.push_back(std::move(right));refresh(*parent);root_=std::move(parent);}++size_;return true;
    }
    bool erase(Integer key){
        key_checked(key);if(!contains(key))return false;erase_node(*root_,key);--size_;
        if(!root_->leaf && root_->children.size()==1){auto old=std::move(root_);root_=std::move(old->children[0]);++stats[5];}return true;
    }
    std::vector<Integer> keys()const{const Node* node=root_.get();while(!node->leaf)node=node->children.front().get();std::vector<Integer> result;while(node){result.insert(result.end(),node->keys.begin(),node->keys.end());node=node->next;}return result;}
    std::vector<Integer> range_query(Integer low,Integer high)const{
        key_checked(low);key_checked(high);require(low<=high,"invalid range");std::vector<Integer> result;const Node* node=leaf(low);auto i=static_cast<std::size_t>(std::lower_bound(node->keys.begin(),node->keys.end(),low)-node->keys.begin());
        while(node){while(i<node->keys.size()){if(node->keys[i]>=high)return result;result.push_back(node->keys[i++]);}node=node->next;i=0;}return result;
    }
};
inline void b_plus_cli(bool final=true){BPlusTree tree(token());ordered_cli(tree,final);}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
b_plus_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
