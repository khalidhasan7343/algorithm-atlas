# Sieve of Eratosthenes

## 1. Algorithm Name

Sieve of Eratosthenes

## 2. Overview

Mark composite integers by prime multiples to enumerate all primes through an inclusive limit.

## 3. Problem Statement

Return ascending primes p with 2≤p≤limit; limits zero and one return an empty list.

**API:** solve(limit), native integer 0..1000000. C++ function sieve(limit).

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

Repeated trial division wastes common work when every prime through the same limit is needed. One marking table shares composite detection across all candidates.

## 5. Real-World Applications

Bounded prime tables for arithmetic exercises, prime-factor lookup preprocessing and enumerating prime candidates in small numerical tasks; no cryptographic prime generation is claimed.

## 6. Core Intuition

Every composite has a prime divisor at most its square root. By the time p is processed, lower multiples of p have already been covered by smaller prime factors, so new marking can begin at p².

## 7. Prerequisites

Divisibility, primes, square roots, arrays and loops. Read the [Number Theory contracts](../../../docs/number-theory-conventions.md).

## 8. Step-by-Step Working Process

Validate the inclusive limit. Allocate a zeroed marking table through limit. For each p starting at two while p²≤limit, if p is unmarked mark p²,p²+p,... . Scan only positions two through limit and return those still unmarked.

**Correctness:** Before processing p, all composites with a smaller prime divisor have been marked. An unmarked p is therefore prime; marking its multiples never removes a prime. Each composite has a prime divisor at most its square root, so by the end every composite is marked. Scanning from two excludes zero and one regardless of their unused table flags.

## 9. Pseudocode

```text
marked = zero table of limit+1 entries
for p=2 while p*p<=limit:
    if not marked[p]:
        for multiple=p*p .. limit step p: marked[multiple]=true
return all unmarked positions from 2 through limit
```

## 10. Dry Run

At limit 20, p=2 marks 4,6,8,...,20. p=3 marks 9,12,15,18. p=4 is already marked; the square-root loop ends. Unmarked positions from two are [2,3,5,7,11,13,17,19].

## 11. Time Complexity

O(N log log N) marking and O(N) collection for inclusive limit N≥2, plus initialization O(N). The bound sums N/p over prime p. Tiny limits are constant work. This is not a segmented sieve.

## 12. Space Complexity

O(N) marking bytes plus O(pi(N)) returned prime integers. Python uses bytearray and C++ vector<unsigned char>; input is one scalar and there is no recursion.

## 13. Python Implementation

The implementation marks explicit bytearray entries in arithmetic-progressions and does not call a third-party prime library. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

The condition p≤limit/p avoids an overflowing square in the guard; p*p is evaluated only after it is safe. The documented 10^6 bound also keeps table and index arithmetic well within int64_t. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '20' | .venv/bin/python dsa/number-theory/sieve-of-eratosthenes/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/sieve-of-eratosthenes/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '20' | /tmp/atlas-category-example
```

Both print:

```json
[2,3,5,7,11,13,17,19]
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Zero/one are not prime and produce []; two produces [2]. Negative limits, bool, floats and values above 10^6 are rejected. Tests include prime-square boundaries and maximum limit, with 78498 returned primes ending at 999983.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

Efficient complete prime enumeration with transparent composite-marking invariants.

## 18. Disadvantages and Limitations

Memory is proportional to the entire limit. The fixed cap is an educational resource limit; this implementation neither segments nor bit-packs the table.

## 19. When to Use It

Choose when many primes in one bounded interval beginning at two are required.

## 20. When Not to Use It

For isolated large candidate tests or large sparse intervals, choose a separately specified primality test or segmented approach.

## 21. Comparison With Related Algorithms

Trial division is an independent small-input oracle but repeats divisibility tests. Factorization consumes one integer and returns prime powers rather than a complete prime table.

## 22. Interview Questions

Why start marking at p²? Why stop after the square root? Why must the output scan explicitly skip zero and one?

## 23. Practice Problems

Trace limit 30. Test limits just below/at/above a prime square. Compare every small limit against independent trial primality.

## 24. References

[NIST DLMF number-theory computation](https://dlmf.nist.gov/27.19) provides context on deterministic number-theory computation; the marking invariant and bounded API here are derived explicitly. The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
