# GCD using Euclidean Algorithm

## 1. Algorithm Name

GCD using Euclidean Algorithm

## 2. Overview

Replace a pair of nonnegative magnitudes by divisor and remainder until the remainder is zero.

## 3. Problem Statement

Return the greatest common divisor of signed inputs, choosing a nonnegative result and gcd(0,0)=0.

**API:** solve(a,b), each native integer in -10^9..10^9. C++ function gcd(a,b).

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Enumerating divisors grows with operand magnitude; remainder reduction rapidly shrinks the problem while preserving the complete common-divisor set.

## 5. Real-World Applications

Reducing rational numbers, divisibility checks and reusable arithmetic primitives such as the canonical LCM implementation.

## 6. Core Intuition

A number divides a and b exactly when it divides b and a mod b. The remainder is smaller than the positive divisor, guaranteeing progress.

## 7. Prerequisites

Integer division/remainders, divisibility, absolute magnitude and loop invariants. Inputs are bounded before taking magnitudes.

## 8. Step-by-Step Working Process

Validate both operands and take nonnegative magnitudes. While b is nonzero, compute a%b and replace (a,b) by (b,remainder). Return a once b is zero.

**Correctness:** The common divisors of (a,b) equal those of (b,a mod b), since a=q*b+r. The invariant therefore preserves their greatest nonnegative common divisor. Remainders strictly decrease while positive, so termination is finite. At b=0, gcd(a,0)=a; both-zero input returns the chosen zero convention.

## 9. Pseudocode

```text
validate a,b; a=abs(a); b=abs(b)
while b != 0:
    a,b = b,a modulo b
return a
```

## 10. Dry Run

For (-48,18), magnitudes (48,18) become (18,12), (12,6), (6,0). Return 6; it divides both original signed inputs.

## 11. Time Complexity

O(log M) remainder steps for M=max(|a|,|b|)≥2, best O(1) when b=0 or division finishes immediately. Consecutive Fibonacci values realize many steps. Fixed-width division is treated as constant time; arbitrary-precision bit complexity is not claimed.

## 12. Space Complexity

O(1) auxiliary storage for a,b and remainder; no divisor list or recursive stack.

## 13. Python Implementation

A tuple assignment performs the iterative Euclidean recurrence after shared native-int/range validation. math.gcd is used only by tests, not by production. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

Operands are limited to ±10^9 before negation, so INT64_MIN negation cannot occur. Remainders operate only on nonnegative operands with b>0, matching Python behavior without negative-modulo differences. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '-48 18' | .venv/bin/python dsa/number-theory/euclidean-algorithm/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/euclidean-algorithm/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '-48 18' | /tmp/atlas-category-example
```

Both print:

```json
6
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Zero with either sign of the other operand, both zero, equal values, coprime inputs, Fibonacci pairs and negative pairs are supported. Out-of-domain input, bool and nonintegers are rejected.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

Short, deterministic and reusable, with logarithmic remainder count and constant working memory.

## 18. Disadvantages and Limitations

The signed input range is deliberately smaller than int64_t so magnitude and dependent LCM/extended arithmetic share safe bounds. The routine returns no Bézout coefficients.

## 19. When to Use It

Choose for ordinary bounded signed-integer GCD and dependent arithmetic.

## 20. When Not to Use It

Use the distinct Extended Euclidean canonical when coefficients are required; do not duplicate this loop in LCM.

## 21. Comparison With Related Algorithms

LCM reuses this canonical rather than implementing its own GCD. Extended Euclid augments remainder reduction with coefficient updates. Trial divisor enumeration is a slower independent conceptual baseline.

## 22. Interview Questions

Why does the common-divisor set remain unchanged? Why is the result nonnegative? Which inputs make the remainder sequence long?

## 23. Practice Problems

Trace gcd(270,192). Verify every returned nonzero result divides both operands. Compare signed random inputs with an independent library oracle.

## 24. References

[Cornell CS2800 Euclidean algorithm lecture](https://www.cs.cornell.edu/courses/cs2800/2016sp/lectures/lec11-gcd.html) and [Stanford number-theory notes](https://crypto.stanford.edu/pbc/notes/numbertheory/euclid.html). The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
