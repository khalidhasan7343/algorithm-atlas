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
        std::size_t parsed = 0;
        long long value = 0;
        try {
            value = std::stoll(token, &parsed, 10);
        } catch (const std::invalid_argument&) {
            throw std::invalid_argument("integer outside long long range");
        } catch (const std::out_of_range&) {
            throw std::invalid_argument("integer outside long long range");
        }
        if (parsed != token.size()) {
            throw std::invalid_argument("integer outside long long range");
        }
        values.push_back(value);
    }
    if (!std::cin.eof()) { throw std::invalid_argument("input failure"); }
    return values;
}
std::string trim(const std::string& value) {
    const auto first = value.find_first_not_of('0');
    return first == std::string::npos ? "0" : value.substr(first);
}
std::string unsigned_add(const std::string& a, const std::string& b) {
    std::string result;
    auto i=a.size(), j=b.size(); int carry=0;
    while (i || j || carry) {
        int sum=carry;
        if (i) { sum += a[--i]-'0'; }
        if (j) { sum += b[--j]-'0'; }
        result.push_back(static_cast<char>('0'+sum%10)); carry=sum/10;
    }
    std::reverse(result.begin(),result.end()); return trim(result);
}
// Precondition: normalized a >= normalized b, as ensured by Karatsuba's identity.
std::string unsigned_subtract(const std::string& a, const std::string& b) {
    std::string result; auto i=a.size(), j=b.size(); int borrow=0;
    while (i) {
        int digit=a[--i]-'0'-borrow; borrow=0;
        if (j) { digit -= b[--j]-'0'; }
        if (digit < 0) { digit += 10; borrow=1; }
        result.push_back(static_cast<char>('0'+digit));
    }
    if (borrow || j) { throw std::logic_error("invalid magnitude subtraction"); }
    std::reverse(result.begin(),result.end()); return trim(result);
}
std::string shift_decimal(std::string value, std::size_t places) {
    if (value != "0") { value.append(places,'0'); }
    return value;
}
std::string multiply_unsigned(const std::string& a, const std::string& b) {
    if (a == "0" || b == "0") { return "0"; }
    const auto n=std::max(a.size(),b.size());
    if (n == 1) { return std::to_string((a[0]-'0')*(b[0]-'0')); }
    const auto half=n/2;
    const auto split=[&](const std::string& v) {
        if (v.size() <= half) { return std::make_pair(std::string("0"),v); }
        return std::make_pair(trim(v.substr(0,v.size()-half)),trim(v.substr(v.size()-half)));
    };
    const auto x=split(a), y=split(b);
    const auto low=multiply_unsigned(x.second,y.second);
    const auto high=multiply_unsigned(x.first,y.first);
    const auto sum=multiply_unsigned(unsigned_add(x.first,x.second),unsigned_add(y.first,y.second));
    const auto middle=unsigned_subtract(unsigned_subtract(sum,low),high);
    return unsigned_add(unsigned_add(shift_decimal(high,2*half),shift_decimal(middle,half)),low);
}
std::string karatsuba_multiplication(const std::string& a, const std::string& b) {
    if (!decimal_token(a) || !decimal_token(b)) { throw std::invalid_argument("expected signed ASCII decimal operands"); }
    const bool negative=(a[0]=='-') != (b[0]=='-');
    const auto first=[](const std::string& v) { return (v[0]=='+' || v[0]=='-') ? v.substr(1) : v; };
    const auto result=multiply_unsigned(trim(first(a)),trim(first(b)));
    return negative && result != "0" ? "-"+result : result;
}

}  // namespace algorithm_atlas
#ifndef ALGORITHM_ATLAS_NO_MAIN
int main() {
    try {
        std::string a,b,extra;
        if (!(std::cin >> a >> b) || (std::cin >> extra)) { throw std::invalid_argument("exactly two operands required"); }
        const auto result=algorithm_atlas::karatsuba_multiplication(a,b);
        std::cout << '"' << result << '"';
        std::cout << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
#endif
