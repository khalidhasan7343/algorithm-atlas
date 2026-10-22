#include "../../common.hpp"

namespace atlas_tree {

class AVLTree{
public:
    struct Node{
        Integer key;int height=1;std::unique_ptr<Node> left,right;
        explicit Node(Integer value):key(value){}
    };
    std::array<Integer,4> rotations{}; // LL, RR, LR, RL diagnostic counts
private:
    using Ptr=std::unique_ptr<Node>;
    Ptr root_;std::size_t size_=0;
    static int height(const Ptr& node){return node?node->height:0;}
    static void refresh(Node& node){node.height=1+std::max(height(node.left),height(node.right));}
    static Ptr rotate_left(Ptr node){
        auto pivot=std::move(node->right);node->right=std::move(pivot->left);pivot->left=std::move(node);
        refresh(*pivot->left);refresh(*pivot);return pivot;
    }
    static Ptr rotate_right(Ptr node){
        auto pivot=std::move(node->left);node->left=std::move(pivot->right);pivot->right=std::move(node);
        refresh(*pivot->right);refresh(*pivot);return pivot;
    }
    Ptr balance(Ptr node){
        refresh(*node);int difference=height(node->left)-height(node->right);
        if(difference>1){
            if(height(node->left->left)<height(node->left->right)){node->left=rotate_left(std::move(node->left));++rotations[2];}else ++rotations[0];
            return rotate_right(std::move(node));
        }
        if(difference<-1){
            if(height(node->right->right)<height(node->right->left)){node->right=rotate_right(std::move(node->right));++rotations[3];}else ++rotations[1];
            return rotate_left(std::move(node));
        }
        return node;
    }
    Ptr insert_node(Ptr node,Integer key){
        if(!node)return std::make_unique<Node>(key);
        if(key<node->key)node->left=insert_node(std::move(node->left),key);
        else node->right=insert_node(std::move(node->right),key);
        return balance(std::move(node));
    }
    Ptr erase_node(Ptr node,Integer key){
        if(key<node->key)node->left=erase_node(std::move(node->left),key);
        else if(key>node->key)node->right=erase_node(std::move(node->right),key);
        else{
            if(!node->left)return std::move(node->right);
            if(!node->right)return std::move(node->left);
            const Node* successor=node->right.get();while(successor->left)successor=successor->left.get();
            node->key=successor->key;node->right=erase_node(std::move(node->right),successor->key);
        }
        return balance(std::move(node));
    }
    static void range(const Node* node,Integer low,Integer high,std::vector<Integer>& result){
        if(!node)return;
        if(node->key>=low)range(node->left.get(),low,high,result);
        if(low<=node->key && node->key<high)result.push_back(node->key);
        if(node->key<high)range(node->right.get(),low,high,result);
    }
public:
    const Node* root()const{return root_.get();}
    std::size_t size()const{return size_;}
    bool contains(Integer key)const{
        key_checked(key);const Node* node=root_.get();
        while(node){if(key==node->key)return true;node=key<node->key?node->left.get():node->right.get();}return false;
    }
    bool insert(Integer key){key_checked(key);if(contains(key))return false;require(size_<1000,"set capacity");root_=insert_node(std::move(root_),key);++size_;return true;}
    bool erase(Integer key){key_checked(key);if(!contains(key))return false;root_=erase_node(std::move(root_),key);--size_;return true;}
    std::vector<Integer> keys()const{
        std::vector<Integer> result;std::vector<const Node*> stack;const Node* node=root_.get();
        while(!stack.empty() || node){while(node){stack.push_back(node);node=node->left.get();}node=stack.back();stack.pop_back();result.push_back(node->key);node=node->right.get();}return result;
    }
    std::vector<Integer> range_query(Integer low,Integer high)const{key_checked(low);key_checked(high);require(low<=high,"invalid range");std::vector<Integer> result;range(root_.get(),low,high,result);return result;}
};
inline void avl_cli(bool final=true){AVLTree tree;ordered_cli(tree,final);}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
avl_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
