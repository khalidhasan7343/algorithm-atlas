#include <algorithm>
#include <array>
#include <charconv>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <optional>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace algorithm_atlas {
bool decimal_token(const std::string& token) {
    if (token.empty()) { return false; }
    std::size_t i = (token[0] == '+' || token[0] == '-') ? 1 : 0;
    if (i == token.size()) { return false; }
    for (; i < token.size(); ++i) { if (token[i] < '0' || token[i] > '9') { return false; } }
    return true;
}
std::vector<long long> read_integers() {
    std::vector<long long> values;
    std::string token;
    while (std::cin >> token) {
        if (!decimal_token(token)) { throw std::invalid_argument("expected decimal integers"); }
        const char* first = token.data() + (token[0] == '+' ? 1 : 0);
        long long value = 0;
        const auto result = std::from_chars(first, token.data() + token.size(), value);
        if (result.ec != std::errc{} || result.ptr != token.data() + token.size()) {
            throw std::invalid_argument("integer outside long long range");
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) { throw std::invalid_argument("input failure"); }
    return values;
}
using Matrix=std::vector<std::vector<long long>>;
constexpr std::size_t max_size=128, base_threshold=2;
constexpr long long entry_limit=1000;
Matrix combine(const Matrix& a,const Matrix& b,long long sign=1) {
    const auto n=a.size();Matrix c(n,std::vector<long long>(n));
    for (std::size_t r=0;r<n;++r) { for (std::size_t col=0;col<n;++col) {
        c[r][col]=a[r][col]+sign*b[r][col];
    } }
    return c;
}
std::array<Matrix,4> split(const Matrix& a) {
    const auto h=a.size()/2;
    std::array<Matrix,4> parts;
    for (auto& part:parts) { part=Matrix(h,std::vector<long long>(h)); }
    for (std::size_t r=0;r<h;++r) { for (std::size_t c=0;c<h;++c) {
        parts[0][r][c]=a[r][c];parts[1][r][c]=a[r][c+h];
        parts[2][r][c]=a[r+h][c];parts[3][r][c]=a[r+h][c+h];
    } }
    return parts;
}
Matrix multiply_blocks(const Matrix& a,const Matrix& b) {
    const auto n=a.size();
    if (n<=base_threshold) {
        Matrix c(n,std::vector<long long>(n,0));
        for (std::size_t r=0;r<n;++r) { for (std::size_t col=0;col<n;++col) {
            for (std::size_t k=0;k<n;++k) { c[r][col]+=a[r][k]*b[k][col]; }
        } }
        return c;
    }
    const auto x=split(a),y=split(b);
    const auto m1=multiply_blocks(combine(x[0],x[3]),combine(y[0],y[3]));
    const auto m2=multiply_blocks(combine(x[2],x[3]),y[0]);
    const auto m3=multiply_blocks(x[0],combine(y[1],y[3],-1));
    const auto m4=multiply_blocks(x[3],combine(y[2],y[0],-1));
    const auto m5=multiply_blocks(combine(x[0],x[1]),y[3]);
    const auto m6=multiply_blocks(combine(x[2],x[0],-1),combine(y[0],y[1]));
    const auto m7=multiply_blocks(combine(x[1],x[3],-1),combine(y[2],y[3]));
    const auto ca=combine(combine(combine(m1,m4),m5,-1),m7);
    const auto cb=combine(m3,m5),cc=combine(m2,m4);
    const auto cd=combine(combine(combine(m1,m2,-1),m3),m6);
    Matrix result(n,std::vector<long long>(n));const auto h=n/2;
    for (std::size_t r=0;r<h;++r) { for (std::size_t c=0;c<h;++c) {
        result[r][c]=ca[r][c];result[r][c+h]=cb[r][c];
        result[r+h][c]=cc[r][c];result[r+h][c+h]=cd[r][c];
    } }
    return result;
}
Matrix strassen_multiply(const Matrix& a,const Matrix& b) {
    const auto n=a.size();
    if (b.size()!=n || n>max_size) { throw std::invalid_argument("same-size square n<=128 required"); }
    for (const auto* matrix:{&a,&b}) {
        for (const auto& row:*matrix) {
            if (row.size()!=n) { throw std::invalid_argument("square matrix required"); }
            for (auto value:row) {
                if (value < -entry_limit || value > entry_limit) { throw std::invalid_argument("entry outside [-1000,1000]"); }
            }
        }
    }
    if (!n) { return {}; }
    std::size_t size=1;while (size<n) { size*=2; }
    Matrix pa(size,std::vector<long long>(size)),pb=pa;
    for (std::size_t r=0;r<n;++r) { for (std::size_t c=0;c<n;++c) { pa[r][c]=a[r][c];pb[r][c]=b[r][c]; } }
    auto result=multiply_blocks(pa,pb);
    result.resize(n);for (auto& row:result) { row.resize(n); }
    return result;
}
void print_result(const Matrix& matrix) {
    std::cout << '[';
    for (std::size_t r=0;r<matrix.size();++r) {
        if (r) { std::cout << ','; }std::cout << '[';
        for (std::size_t c=0;c<matrix[r].size();++c) { if (c) { std::cout << ','; }std::cout << matrix[r][c]; }
        std::cout << ']';
    }
    std::cout << ']';
}

}  // namespace algorithm_atlas
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        const auto numbers=algorithm_atlas::read_integers();
        if (numbers.empty() || numbers[0]<0 || numbers[0]>128) { throw std::invalid_argument("n in 0..128 required"); }
        const auto n=static_cast<std::size_t>(numbers[0]);
        if (numbers.size()!=1+2*n*n) { throw std::invalid_argument("matrix count mismatch"); }
        algorithm_atlas::Matrix a(n,std::vector<long long>(n)),b=a;
        std::size_t i=1;
        for (auto* matrix:{&a,&b}) { for (auto& row:*matrix) { for (auto& value:row) { value=numbers[i++]; } } }
        algorithm_atlas::print_result(algorithm_atlas::strassen_multiply(a,b));
        std::cout << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
