# Modular Exponentiation

## 1. Algorithm Name

Modular Exponentiation

## 2. Overview

Compute a nonnegative-exponent power modulo a bounded positive modulus with binary exponentiation.

## 3. Problem Statement

Return the least nonnegative residue of base^exponent modulo modulus, including negative bases and exponent zero.

**API:** solve(base,exponent,modulus); C++ mod_power. Base ±10^9, exponent 0..10^9, modulus 1..1000000007.

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Constructing the exact power can require enormous integers; modular reduction after every multiplication keeps operands small.

## 5. Real-World Applications

Bounded modular-identity exercises, repeated modular powers and number-theory demonstrations. This variable-time educational routine is not a hardened cryptographic primitive.

## 6. Core Intuition

Binary exponent digits select powers base^(1),base^(2),base^(4),... . Squaring supplies the next power; modular reduction preserves every needed congruence.

## 7. Prerequisites

Remainders, congruences, nonnegative binary exponents and multiplication bounds. No primality or coprimality of the modulus is required.

## 8. Step-by-Step Working Process

Validate all domains and normalize base into [0,m). Start result=1 mod m. While exponent is positive, multiply result by base modulo m if the low bit is one, shift exponent right, and square the base modulo m if more bits remain. Return result.

**Correctness:** The invariant result*base^remaining is congruent to the originally requested power. An odd-bit multiplication removes one base factor; halving the remaining exponent and squaring preserves the rest. Each remainder operation preserves congruence and the chosen range. At remaining zero the invariant identifies result as the required residue.

## 9. Pseudocode

```text
validate base,e,m; base=nonnegative_residue(base,m); result=1 mod m
while e>0:
    if e odd: result=(result*base) mod m
    e=floor(e/2)
    if e>0: base=(base*base) mod m
return result
```

## 10. Dry Run

For (-2,5,13), normalize base to 11 and start result 1. Low bit multiplies to 11, then base squares to 4; the next bit is zero and base squares to 3. Final selected multiplication 11*3 mod 13 gives 7. For modulus 1, every result including exponent zero is 0.

## 11. Time Complexity

O(log(e+1)) fixed-width modular multiplications, constant work for exponent zero. Products are constant-width under the declared modulus cap; this is not an arbitrary-precision bit-complexity claim.

## 12. Space Complexity

O(1) auxiliary state and one scalar output. The full integer power is never materialized.

## 13. Python Implementation

Python’s positive-modulus % directly normalizes negative bases. The implementation still enforces the same finite modulus and input limits as C++, rather than claiming arbitrary-precision equivalence. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

Negative remainder is adjusted by adding modulus once. Reduced factors are at most 1000000006, so their product is below INT64_MAX; no __int128, floating multiplication or overflow-prone unrestricted modulus is used. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '-2 5 13' | .venv/bin/python dsa/number-theory/modular-exponentiation/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/modular-exponentiation/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '-2 5 13' | /tmp/atlas-category-example
```

Both print:

```json
7
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Exponent zero, 0^0, zero base, negative bases, composite modulus and modulus 1 are explicit. Zero/negative modulus, negative exponent and out-of-range operands are rejected. Negative exponents do not request modular inverses.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

Logarithmic exponent processing with bounded residues and exact integer arithmetic.

## 18. Disadvantages and Limitations

The modulus cap is part of overflow safety. This is neither a modular-inverse API nor constant-time cryptographic code.

## 19. When to Use It

Choose for bounded nonnegative-exponent modular powers and congruence checks.

## 20. When Not to Use It

For unrestricted 64-bit moduli use an independently specified overflow-safe multiplication method; do not merely enlarge this cap.

## 21. Comparison With Related Algorithms

Fast Exponentiation computes an exact signed-64 result and may reject overflow; this canonical keeps only residues. Both teach repeated squaring without replacing core logic by pow.

## 22. Interview Questions

Why does normalization differ between Python and C++? Is a prime modulus necessary? What is result for exponent zero and modulus one? Which product bound prevents overflow?

## 23. Practice Problems

Trace 3^13 mod 17. Compare random cases with built-in modular pow only in an oracle. Test negative bases with composite moduli and prove no coprimality assumption is used.

## 24. References

[Stanford Euclidean number-theory notes](https://crypto.stanford.edu/pbc/notes/numbertheory/euclid.html) for congruence context and [C++17 arithmetic rules](https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf). The binary invariant is derived here. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
