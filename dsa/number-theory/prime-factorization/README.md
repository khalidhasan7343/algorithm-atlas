# Prime Factorization

## 1. Algorithm Name

Prime Factorization

## 2. Overview

Divide out factors two and then odd candidates, returning sorted prime powers for a bounded positive integer.

## 3. Problem Statement

Return ascending [prime,exponent] rows whose product reconstructs n. One returns []; zero and negative integers are outside the supported domain.

**API:** solve(n); C++ factorize(n). Native integer 1..10^12, exact deterministic factorization.

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

A prime-power decomposition exposes divisibility structure and supplies compact certificates for many arithmetic exercises.

## 5. Real-World Applications

Small exact-integer decomposition, divisor-count derivations and independent reconstruction/primality checks. Trial division is not a modern large cryptographic-factorization method.

## 6. Core Intuition

After removing smaller prime factors, any new divisor that divides the remainder is prime. If no candidate through the square root divides it, a remainder above one is itself prime.

## 7. Prerequisites

Primes, divisibility, unique factorization and square-root factor bounds. See the [Sieve lesson](../sieve-of-eratosthenes/README.md) for a different prime-table task.

## 8. Step-by-Step Working Process

Validate n≥1 and the resource cap. Try divisor two, dividing out all copies and recording a positive exponent. Continue with odd candidates while divisor≤remaining/divisor, shrinking the remaining value. After the loop append any remainder above one with exponent one.

**Correctness:** At each candidate, all smaller prime factors have been removed and the original n equals recorded prime powers times the remainder. A divisor found now cannot have an unremoved smaller factor, so it is prime. Once the candidate exceeds the square-root bound, a composite remainder would need a smaller prime divisor, contradicting the invariant. Recorded factors are strictly ascending and reconstruct n exactly.

## 9. Pseudocode

```text
require 1<=n<=10^12; factors=[]; d=2
while d<=n/d:
    e=0
    while n divisible by d: n=n/d; e+=1
    if e>0: append [d,e]
    d=3 if d=2 else d+2
if n>1: append [n,1]
return factors
```

## 10. Dry Run

For 360, divide by two three times to leave 45 and record [2,3]. Divide by three twice to leave 5 and record [3,2]. The square-root loop ends and append [5,1]. Their product 8*9*5 reconstructs 360.

## 11. Time Complexity

O(sqrt(n)) trial candidates in the worst case for the original n, plus O(log n) successful divisions. Shrinking the remainder can substantially reduce actual work. This is a deterministic bound, not a probabilistic primality guarantee or subexponential factorization claim.

## 12. Space Complexity

O(1) arithmetic state beyond O(t) returned prime-power rows for t distinct factors. No sieve through sqrt(n) or complete divisor table is stored.

## 13. Python Implementation

The loop tests d≤remaining//d and changes from two to odd candidates. It neither calls a factorization library nor returns a raw list of guessed divisors. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

The division guard avoids a d*d overflow pattern. n≤10^12 and all candidates/remainders fit int64_t; division is exact inside the factor-removal loop. Exponents are positive and bounded by log2(n). Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '360' | .venv/bin/python dsa/number-theory/prime-factorization/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/prime-factorization/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '360' | /tmp/atlas-category-example
```

Both print:

```json
[[2,3],[3,2],[5,1]]
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

One gives no factors; primes give one row; prime squares and high powers give grouped exponents. The 10^12 boundary and a near-million prime square are tested. Zero, negatives, bool and values beyond the cap are rejected.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

Exact, deterministic and easy to certify with prime checks and product reconstruction.

## 18. Disadvantages and Limitations

Trial work is slow for large primes/semiprimes. The explicit cap is a practical limit, not a claim that arbitrary large integers are efficiently factored.

## 19. When to Use It

Choose for bounded positive integers where transparent factor decomposition and simple proofs are desired.

## 20. When Not to Use It

Use an appropriately specified faster factorization method for cryptographic-scale integers; no such extra canonical is added here.

## 21. Comparison With Related Algorithms

Sieve returns every prime through a limit, while factorization finds factors of one integer. GCD often avoids factorization entirely for common-divisor queries.

## 22. Interview Questions

Why is the leftover remainder prime? Why are even candidates after two unnecessary? Why must n=0 be rejected? Why use d≤remaining/d instead of d*d≤remaining?

## 23. Practice Problems

Factor 7560 and verify the product. Test every positive integer through 300 with an independent oracle. Construct prime-square and large-prime worst-case inputs inside the bound.

## 24. References

[NIST DLMF §27.19, Methods of Computation: Factorization](https://dlmf.nist.gov/27.19) provides deterministic/probabilistic factorization context. This lesson implements only the explicit bounded trial method. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
