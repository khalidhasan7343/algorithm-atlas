# Fast Exponentiation

## 1. Algorithm Name

Fast Exponentiation

## 2. Overview

Use repeated squaring and checked signed-64 multiplication to compute an exact nonnegative-exponent integer power.

## 3. Problem Statement

Return base^exponent exactly when it fits signed 64-bit, otherwise reject overflow rather than wrap or silently use larger Python results.

**API:** solve(base,exponent); C++ power. Base ±10^9 and exponent 0..10^9; result range -2^63..2^63-1, with 0^0=1.

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Multiplying base e times is unnecessary; binary exponent structure reduces the number of products to logarithmic work while explicit checks preserve cross-language exactness.

## 5. Real-World Applications

Bounded exact powers in arithmetic exercises, geometric-growth calculations and verifying overflow-aware integer routines.

## 6. Core Intuition

Process the exponent’s low bits: a set bit contributes the current base power, and squaring moves to the next binary place. Only products actually needed by the remaining exponent should be computed.

## 7. Prerequisites

Binary representations, exponent identities, signed ranges and overflow preconditions. Understand why a final unused square must not invalidate a fitting answer.

## 8. Step-by-Step Working Process

Validate base/exponent. Start result one. On a set bit, multiply result by base through a checked helper. Shift exponent right. Square base through the same helper only if exponent remains nonzero. Return result. The helper compares unsigned magnitudes against a sign-specific product limit before C++ multiplication.

**Correctness:** In exact arithmetic, result*base^remaining equals the requested power throughout binary reduction. Checked products either preserve that identity exactly or prove a required product cannot fit the supported range. For |base|≥2, required intermediate exponents do not exceed the requested exponent; trivial 0/±1 are also safe. Avoiding an unused final square prevents false overflow rejection. Sign-specific magnitude checks admit the negative limit -2^63 while rejecting positive 2^63.

## 9. Pseudocode

```text
result=1
while e>0:
    if e odd: result=checked_multiply(result,base)
    e=floor(e/2)
    if e>0: base=checked_multiply(base,base)
return result
checked_multiply(a,b):
    determine sign; compute unsigned magnitudes without negating INT64_MIN
    require magnitude_product <= 2^63 if negative, else 2^63-1
    return exact signed product, handling negative limit explicitly
```

## 10. Dry Run

For 3^5: result becomes 3 at the low bit; squaring gives 9, then 81; the final selected product is 243. For (-2)^63 the final result is INT64_MIN and is accepted. For 2^62 the result fits even though an additional unused square would overflow; that square is skipped.

## 11. Time Complexity

O(log(e+1)) checked multiplications and shifts, with O(1) work for exponent zero. Overflow may reject earlier. Python intermediate products are at most products of checked signed-64 operands; no unbounded output magnitude is promised.

## 12. Space Complexity

O(1) fixed-width algorithm state and scalar output. Python’s temporary product is bounded to at most about 128 bits before the explicit range check.

## 13. Python Implementation

The helper computes a product then enforces signed-64 bounds with ValueError. Production never delegates exponentiation to built-in pow; tests use it independently. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

The helper forms unsigned magnitudes as -(value+1)+1 for negatives, avoiding signed INT64_MIN negation. It divides the allowed limit before multiplication, uses uint64_t for magnitude products, and returns the negative boundary before any out-of-range signed cast. No signed overflow or compiler extension is required. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '-2 63' | .venv/bin/python dsa/number-theory/fast-exponentiation/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/fast-exponentiation/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '-2 63' | /tmp/atlas-category-example
```

Both print:

```json
-9223372036854775808
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Zero exponent and 0^0 return one. Huge exponents for 0/±1 remain cheap. Negative exponents, out-of-domain base/exponent and exact powers outside signed-64 are rejected. Positive 2^63 is rejected; (-2)^63 is accepted.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

Logarithmic exact arithmetic with explicit overflow behavior and cross-language boundary agreement.

## 18. Disadvantages and Limitations

An otherwise mathematically valid power may exceed the supported result range. This is not an arbitrary-precision power implementation, and multiplication timing is not cryptographically constant.

## 19. When to Use It

Choose when a finite exact integer power and explicit overflow rejection are required.

## 20. When Not to Use It

Use a separately defined arbitrary-precision API for large exact outputs, or Modular Exponentiation when only a residue is needed.

## 21. Comparison With Related Algorithms

Modular Exponentiation reduces every product and does not report full-power overflow. Linear repeated multiplication is a simple small-input oracle but uses O(e) products.

## 22. Interview Questions

Why can computing one extra square be wrong? Why must negative and positive magnitude limits differ? How can INT64_MIN’s magnitude be obtained without signed overflow?

## 23. Practice Problems

Check (-2)^63 and 2^63. Find a case where the requested power fits but an unused square does not. Compare bounded random exact results and overflow cases with Python pow in tests.

## 24. References

[C++17 working draft N4659](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf), integer conversions and arithmetic rules. The checked binary-power invariant and API are derived in this lesson. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
