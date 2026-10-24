# Extended Euclidean Algorithm

## 1. Algorithm Name

Extended Euclidean Algorithm

## 2. Overview

Track linear-combination coefficients alongside Euclidean remainder reduction to produce Bézout coefficients.

## 3. Problem Statement

Return [g,x,y] with g=gcd(a,b)≥0 and a*x+b*y=g for signed operands; (0,0) returns [0,0,0].

**API:** solve(a,b); C++ extended_gcd. Each input lies in -10^9..10^9. Coefficients follow this deterministic recurrence; other mathematically valid pairs are not considered errors.

[Shared contracts](../../../docs/number-theory-conventions.md) specify numeric/byte domains, invalid-input behavior, resource bounds and exact CLI grammar.

## 4. Why Do We Need This Algorithm?

GCD alone proves common divisibility; coefficients witness an exact integer linear combination and are useful in later algebraic derivations.

## 5. Real-World Applications

Bézout identity exercises, Diophantine consistency checks and the mathematical foundation of modular-inverse derivations when separate coprimality assumptions hold. This API does not itself add an inverse canonical.

## 6. Core Intuition

Every Euclidean remainder is an integer linear combination of the original magnitudes. Apply the same quotient subtraction to their coefficient pairs.

## 7. Prerequisites

The [Euclidean GCD](../euclidean-algorithm/README.md), quotient/remainder identities, signed magnitude and simple algebraic invariants.

## 8. Step-by-Step Working Process

Validate operands and special-case both zero. Initialize magnitude remainders (|a|,|b|) with coefficient vectors (1,0),(0,1). At each quotient, subtract quotient times the current remainder and coefficient vector from the previous ones. When remainder becomes zero, adjust coefficient signs for the original a,b and return the GCD with those coefficients.

**Correctness:** Maintain old_r=old_x*|a|+old_y*|b| and r=x*|a|+y*|b|. Subtracting the same quotient multiples preserves both identities while Euclid preserves the GCD and decreases positive remainders. At zero remainder, the previous identity witnesses the nonnegative GCD. Coefficient sign adjustment converts magnitudes back to original signed operands.

## 9. Pseudocode

```text
if a=b=0: return [0,0,0]
old_r,r=abs(a),abs(b); old_x,x=1,0; old_y,y=0,1
while r!=0:
    q=old_r divided by r
    old_r,r = r,old_r-q*r
    old_x,x = x,old_x-q*x
    old_y,y = y,old_y-q*y
adjust old_x/old_y for input signs; return [old_r,old_x,old_y]
```

## 10. Dry Run

For (30,18), quotients 1,1,2 reduce remainders to 6. Coefficients (-1,2) satisfy 30*(-1)+18*2=6. For (-30,18), adjust x to 1 so (-30)*1+18*2=6. Coefficients are verified by the identity, not by a unique-solution claim.

## 11. Time Complexity

O(log M) remainder/coefficient updates for M=max(|a|,|b|)≥2, constant time when the second magnitude is zero. Each arithmetic operation is bounded signed-64 under the ±10^9 input contract; no arbitrary-precision bit bound is claimed.

## 12. Space Complexity

O(1) auxiliary scalar state and three returned integers, with no recursive coefficient stack.

## 13. Python Implementation

Tuple assignments update both prior/current coefficient values simultaneously. Python integers are checked at input to match the C++ finite domain. Read [`python/solution.py`](python/solution.py). Importing it runs no example.

## 14. C++ Implementation

All remainders start nonnegative; quotient calculations match Python floor division on those magnitudes. The input cap keeps coefficient magnitudes and conservative quotient-times-coefficient intermediates within int64_t. Inputs are validated before negation, and final identity products are safe within the documented cap. Read [`cpp/solution.cpp`](cpp/solution.cpp). Define ALGORITHM_ATLAS_NO_MAIN in an API test driver. Both C++17 and C++20 are tested.

## 15. Input and Output Examples

From the repository root:

```sh
printf '%s\n' '-30 18' | .venv/bin/python dsa/number-theory/extended-euclidean-algorithm/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/number-theory/extended-euclidean-algorithm/cpp/solution.cpp -o /tmp/atlas-category-example
printf '%s\n' '-30 18' | /tmp/atlas-category-example
```

Both print:

```json
[6,1,2]
```

C++20 uses -std=c++20. Decimal tokens have no array length prefix; consult the shared contract for each operation’s arity and scalar-prefix or hex-string syntax.

## 16. Edge Cases

Both zero, exactly one zero, negative/equal operands, coprime pairs and Fibonacci-like sequences are explicit. Out-of-range values and nonintegers are rejected. No coefficient-minimization or inverse existence is assumed.

[Python tests](tests/test_python.py) and [C++ tests](tests/test_cpp.py) exercise deterministic vectors, independent references and invalid contracts. Actual seeds/counts/results are recorded in [checkpoints](../../../docs/number-theory-checkpoints.md).

## 17. Advantages

A constructive GCD certificate with constant working space and logarithmic reduction count.

## 18. Disadvantages and Limitations

Many Bézout coefficient pairs are valid; this recurrence selects one. Expanding inputs to full signed-64 requires revisiting coefficient/intermediate bounds.

## 19. When to Use It

Choose when a GCD certificate or linear combination is required.

## 20. When Not to Use It

Use ordinary GCD when coefficients add no value; do not infer a modular inverse unless gcd=1 and the modulus contract is separately defined.

## 21. Comparison With Related Algorithms

Ordinary Euclid tracks only remainders. Extended Euclid tracks the same reductions plus two coefficient pairs, so it remains a distinct canonical variant.

## 22. Interview Questions

Which two identities hold inside the loop? How do negative input signs affect coefficients? Why are coefficient outputs not unique? What does (0,0) require as a convention?

## 23. Practice Problems

Trace (99,78). Verify a*x+b*y=g for every signed pair in a small square. Compare only semantic identity/GCD when testing another valid implementation.

## 24. References

[Stanford Euclid/Bézout notes](https://crypto.stanford.edu/pbc/notes/numbertheory/euclid.html) and [Cornell Euclidean algorithm lecture](https://www.cs.cornell.edu/courses/cs2800/2016sp/lectures/lec11-gcd.html). The bounded API and output/tie rules are repository contracts.

## 25. Author Attribution

**MD.Khalid Hasan**, maintainer of [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas). [MIT License](../../../LICENSE).
