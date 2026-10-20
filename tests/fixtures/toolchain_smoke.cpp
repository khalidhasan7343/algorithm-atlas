// Infrastructure smoke test only: no syllabus algorithm is implemented here.
#include <iostream>
#include <optional>
#include <string_view>

#if __cplusplus >= 202002L
#include <concepts>
static_assert(std::integral<int>);
#else
static_assert(__cplusplus >= 201703L, "C++17 or newer is required");
#endif

int main() {
    const std::optional<std::string_view> message{"Algorithm Atlas toolchain ready"};
    std::cout << message.value() << '\n';
    return 0;
}
