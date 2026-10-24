#include "../../common.hpp"

namespace atlas_string {
class SuffixArray {
    std::string text_;
    int compare(int start,const std::string& pattern) const {
        int n=static_cast<int>(text_.size()),m=static_cast<int>(pattern.size()),j=0;
        while (j<m && start+j<n) {
            if (byte(text_[start+j])!=byte(pattern[j]))
                return byte(text_[start+j])<byte(pattern[j])?-1:1;
            ++j;
        }
        return j==m?0:-1;
    }
public:
    std::vector<int> sa,lcp;
    explicit SuffixArray(const std::string& text):text_(text) {
        checked(text);
        int n=static_cast<int>(text.size());
        sa.resize(n); std::iota(sa.begin(),sa.end(),0);
        std::vector<int> rank(n);
        for (int i=0;i<n;++i) rank[i]=byte(text[i]);
        for (int width=1;width<n;width*=2) {
            auto key=[&](int i) {return std::make_pair(rank[i],i+width<n?rank[i+width]:-1);};
            std::sort(sa.begin(),sa.end(),[&](int a,int b){return key(a)<key(b);});
            std::vector<int> next(n);
            for (int j=1;j<n;++j) next[sa[j]]=next[sa[j-1]]+(key(sa[j])!=key(sa[j-1]));
            rank=std::move(next);
            if (rank[sa.back()]==n-1) break;
        }
        std::vector<int> inverse(n);
        for (int j=0;j<n;++j) inverse[sa[j]]=j;
        lcp.resize(n);
        int common=0;
        for (int i=0;i<n;++i) {
            int j=inverse[i];
            if (!j) {common=0;continue;}
            int previous=sa[j-1];
            while (i+common<n && previous+common<n && text[i+common]==text[previous+common]) ++common;
            lcp[j]=common;
            if (common) --common;
        }
    }
    std::vector<int> find(const std::string& pattern) const {
        checked(pattern);
        if (pattern.empty()) return boundaries(static_cast<int>(text_.size()));
        auto bound=[&](bool upper) {
            int low=0,high=static_cast<int>(sa.size());
            while (low<high) {
                int mid=(low+high)/2,cmp=compare(sa[mid],pattern);
                if (cmp<0 || (upper && cmp==0)) low=mid+1;
                else high=mid;
            }
            return low;
        };
        int left=bound(false),right=bound(true);
        std::vector<int> result(sa.begin()+left,sa.begin()+right);
        std::sort(result.begin(),result.end());
        return result;
    }
};
inline std::vector<std::vector<int>> solve(const std::string& text,const std::string& pattern) {
    SuffixArray index(text);
    return {index.sa,index.lcp,index.find(pattern)};
}
}
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        auto text=atlas_string::read_bytes();
        auto pattern=atlas_string::read_bytes();
        atlas_string::end_input();
        atlas_string::emit(atlas_string::solve(text,pattern));
        std::cout << '\n';
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 2;
    }
}
#endif
