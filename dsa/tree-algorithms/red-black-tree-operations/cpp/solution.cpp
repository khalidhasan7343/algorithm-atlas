#include "../../common.hpp"

namespace atlas_tree {

class RedBlackTree{
public:
    struct Node{Integer key;bool red=true;std::unique_ptr<Node> left,right;explicit Node(Integer value):key(value){}};
    std::array<Integer,5> stats{}; // left/right rotations, flips, move-red-left/right
private:
    using Ptr=std::unique_ptr<Node>;Ptr root_;std::size_t size_=0;
    static bool red(const Node* node){return node && node->red;}
    Ptr rotate_left(Ptr node){
        auto pivot=std::move(node->right);node->right=std::move(pivot->left);pivot->left=std::move(node);
        pivot->red=pivot->left->red;pivot->left->red=true;++stats[0];return pivot;
    }
    Ptr rotate_right(Ptr node){
        auto pivot=std::move(node->left);node->left=std::move(pivot->right);pivot->right=std::move(node);
        pivot->red=pivot->right->red;pivot->right->red=true;++stats[1];return pivot;
    }
    void flip(Node& node){node.red=!node.red;if(node.left)node.left->red=!node.left->red;if(node.right)node.right->red=!node.right->red;++stats[2];}
    Ptr fix(Ptr node){
        if(red(node->right.get()))node=rotate_left(std::move(node));
        if(red(node->left.get()) && red(node->left->left.get()))node=rotate_right(std::move(node));
        if(red(node->left.get()) && red(node->right.get()))flip(*node);
        return node;
    }
    Ptr move_red_left(Ptr node){
        ++stats[3];flip(*node);
        if(node->right && red(node->right->left.get())){node->right=rotate_right(std::move(node->right));node=rotate_left(std::move(node));flip(*node);}return node;
    }
    Ptr move_red_right(Ptr node){
        ++stats[4];flip(*node);
        if(node->left && red(node->left->left.get())){node=rotate_right(std::move(node));flip(*node);}return node;
    }
    Ptr insert_node(Ptr node,Integer key){
        if(!node)return std::make_unique<Node>(key);
        if(key<node->key)node->left=insert_node(std::move(node->left),key);else node->right=insert_node(std::move(node->right),key);
        if(red(node->right.get()) && !red(node->left.get()))node=rotate_left(std::move(node));
        if(red(node->left.get()) && red(node->left->left.get()))node=rotate_right(std::move(node));
        if(red(node->left.get()) && red(node->right.get()))flip(*node);
        return node;
    }
    Ptr delete_min(Ptr node){
        if(!node->left)return nullptr;
        if(!red(node->left.get()) && !red(node->left->left.get()))node=move_red_left(std::move(node));
        node->left=delete_min(std::move(node->left));return fix(std::move(node));
    }
    Ptr erase_node(Ptr node,Integer key){
        if(key<node->key){
            if(!red(node->left.get()) && !red(node->left?node->left->left.get():nullptr))node=move_red_left(std::move(node));
            node->left=erase_node(std::move(node->left),key);
        }else{
            if(red(node->left.get()))node=rotate_right(std::move(node));
            if(key==node->key && !node->right)return nullptr;
            if(!red(node->right.get()) && !red(node->right?node->right->left.get():nullptr))node=move_red_right(std::move(node));
            if(key==node->key){const Node* successor=node->right.get();while(successor->left)successor=successor->left.get();node->key=successor->key;node->right=delete_min(std::move(node->right));}
            else node->right=erase_node(std::move(node->right),key);
        }
        return fix(std::move(node));
    }
    static void range(const Node* node,Integer low,Integer high,std::vector<Integer>& result){
        if(!node)return;if(node->key>=low)range(node->left.get(),low,high,result);
        if(low<=node->key && node->key<high)result.push_back(node->key);
        if(node->key<high)range(node->right.get(),low,high,result);
    }
public:
    const Node* root()const{return root_.get();}
    std::size_t size()const{return size_;}
    bool contains(Integer key)const{key_checked(key);const Node* node=root_.get();while(node){if(key==node->key)return true;node=key<node->key?node->left.get():node->right.get();}return false;}
    bool insert(Integer key){key_checked(key);if(contains(key))return false;require(size_<1000,"set capacity");root_=insert_node(std::move(root_),key);root_->red=false;++size_;return true;}
    bool erase(Integer key){
        key_checked(key);if(!contains(key))return false;if(!red(root_->left.get()) && !red(root_->right.get()))root_->red=true;
        root_=erase_node(std::move(root_),key);if(root_)root_->red=false;--size_;return true;
    }
    std::vector<Integer> keys()const{std::vector<Integer> result;std::vector<const Node*> stack;const Node* node=root_.get();while(!stack.empty() || node){while(node){stack.push_back(node);node=node->left.get();}node=stack.back();stack.pop_back();result.push_back(node->key);node=node->right.get();}return result;}
    std::vector<Integer> range_query(Integer low,Integer high)const{key_checked(low);key_checked(high);require(low<=high,"invalid range");std::vector<Integer> result;range(root_.get(),low,high,result);return result;}
};
inline void red_black_cli(bool final=true){RedBlackTree tree;ordered_cli(tree,final);}

}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main(){try{using namespace atlas_tree;
red_black_cli();
std::cout<<'\n';
}catch(const std::exception& error){std::cerr<<"error: "<<error.what()<<'\n';return 2;}}
#endif
