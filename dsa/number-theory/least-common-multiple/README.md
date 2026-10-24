# Least Common Multiple (LCM)

## 1. Algorithm Name

Least Common Multiple (LCM)

## 2. Overview

Use the canonical Euclidean GCD to divide before multiplying nonnegative magnitudes.

## 3. Problem Statement

Return the least nonnegative common multiple, with lcm(a,0)=lcm(0,b)=0 including (0,0).

**API:** solve(a,b), each native integer -10^9..10^9. C++ function lcm(a,b). The result is an exact nonnegative integer at most 10^18.

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Multiples need not be searched one by one. The GCD measures shared prime-factor contribution, which must be included only once in the least common multiple.

## 5. Real-World Applications

Combining integer periods and divisibility schedules under a bounded exact-integer model, and fraction common-denominator exercises.

## 6. Core Intuition

For nonzero operands, gcd(a,b)*lcm(a,b)=|a*b|. Divide one magnitude by the GCD first, then multiply by the other magnitude to avoid an unnecessarily large intermediate.

## 7. Prerequisites

GCD, integer divisibility, sign/magnitude handling and the product identity. See the [canonical Euclidean lesson](../euclidean-algorithm/README.md).

## 8. Step-by-Step Working Process

Validate both operands. Return zero immediately if either is zero, avoiding division by gcd(0,0). Otherwise call the canonical GCD, divide |a| by it and multiply by |b|. Return the nonnegative result without mutating inputs.

**Correctness:** In prime exponents, the product adds exponents and GCD selects the minimum; dividing therefore leaves the maximum exponent required by a common multiple. The resulting number is divisible by both magnitudes and divides every other common multiple. Signs do not affect divisibility, and zero follows the explicit convention.

## 9. Pseudocode

```text
validate a,b
if a=0 or b=0: return 0
g = canonical_gcd(a,b)
return (abs(a) divided exactly by g) * abs(b)
```

## 10. Dry Run

For (-12,18), gcd=6, so (12/6)*18=36. Both 12 and 18 divide 36; any common multiple must include the maximum prime powers 2² and 3². For (0,18), return zero before division.

## 11. Time Complexity

O(log M) remainder steps from the reused Euclidean GCD, plus O(1) magnitude/division/multiplication. A zero operand takes O(1) work. M=max(|a|,|b|); no multiple enumeration or factorization occurs.

## 12. Space Complexity

O(1) arithmetic workspace beyond the reused iterative GCD. Python module import metadata is fixed program infrastructure, not input-dependent algorithm storage.

## 13. Python Implementation

The module loads the existing Euclidean canonical and calls its solve routine. There is a single production GCD implementation, not a copied loop or math.gcd shortcut. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

LCM includes the canonical Euclidean source with its executable main disabled locally. The LCM source still has its own normal main. Validation makes negation safe; divide-first multiplication is at most 10^18, below INT64_MAX, including coprime boundary operands. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '-12 18' | .venv/bin/python dsa/number-theory/least-common-multiple/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/least-common-multiple/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '-12 18' | /tmp/atlas-category-example
```

Both print:

```json
36
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Both zero, one zero, equal operands, negative operands and coprime boundary values are defined. Inputs beyond ±10^9 and nonintegers are rejected. Worst coprime near-boundary output 999999999000000000 is tested exactly.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

Exact result with a reused small GCD primitive and explicit safe multiplication order.

## 18. Disadvantages and Limitations

No arbitrary-precision or full-int64 input range is claimed. Even divide-first cannot prevent overflow for unrestricted inputs; the documented finite domain supplies the guarantee.

## 19. When to Use It

Choose for exact common periods/divisibility quantities inside the bounded domain.

## 20. When Not to Use It

Do not extend inputs to arbitrary signed-64 without adding checked multiplication and safe magnitude rules.

## 21. Comparison With Related Algorithms

GCD returns the greatest shared divisor; LCM returns the least common multiple. Factorization can derive both but is unnecessary work here. This is a separate canonical topic reusing the GCD implementation.

## 22. Interview Questions

Why handle zero before dividing? Why divide before multiplication? Does a negative input require a negative LCM? What changes for unbounded input domains?

## 23. Practice Problems

Verify gcd*lcm=|a*b| on nonzero signed pairs. Derive LCM from prime exponents for 12 and 18. Construct large coprime values showing why the numeric domain matters.

## 24. References

[Stanford Euclidean number-theory notes](https://crypto.stanford.edu/pbc/notes/numbertheory/euclid.html), with the prime-exponent product identity derived in this lesson. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
