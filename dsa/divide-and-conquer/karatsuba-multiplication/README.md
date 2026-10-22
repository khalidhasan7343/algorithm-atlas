# Karatsuba Multiplication

## 1. Algorithm Name

Karatsuba Multiplication

## 2. Overview

Multiply signed integers through three recursive half-size magnitude products instead of four. Sign normalization surrounds the nonnegative core.

## 3. Problem Statement

Python accepts two native arbitrary-size integers and returns their exact integer product. C++ accepts two nonempty signed ASCII decimal strings and returns a normalized signed decimal string, with no leading zeros or negative zero. The Python and C++ CLIs both take exactly two decimal operands and return the exact product as a JSON string. Leading + and zeros are valid CLI/C++ input; malformed digits, missing/extra operands, and Python bool/float/string operands are invalid.

## 4. Why Do We Need This Algorithm?

Schoolbook multiplication creates four products when two operands are split in half. An algebraic identity recovers the cross term from a third product, reducing large-operand work.

## 5. Real-World Applications

- Teach the transition from quadratic digit multiplication to subquadratic arithmetic.
- Build exact educational large-integer arithmetic without a C++ big-integer dependency.
- Compare intermediate arithmetic and operand representation costs. This implementation is not a constant-time cryptographic primitive.

## 6. Core Intuition

Write x=xh·B+xl and y=yh·B+yl. Compute z0=xl·yl, z2=xh·yh, z1=(xl+xh)(yl+yh)-z0-z2. Then xy=z2·B²+z1·B+z0. Only three recursive products are needed.

## 7. Prerequisites

Understand positional notation, quotient/remainder splitting, sign arithmetic, recursive termination, and recurrences. Python splits binary magnitudes; C++ splits decimal digit strings. The radix changes representation, not the Karatsuba identity.

## 8. Step-by-Step Working Process

1. Validate operands and separate the result sign from absolute magnitudes.
2. Return zero immediately if either magnitude is zero.
3. Python uses direct multiplication only when both magnitudes fit 16 bits; C++ uses direct digit multiplication only for one-digit operands (at most 9·9).
4. Split at roughly half the larger width; a shorter operand may have zero high part.
5. Recursively compute low, high, and sum products; subtract low/high to obtain the cross term.
6. Shift by radix places and add; apply sign unless the result is zero. Expansion of the identity proves correctness inductively. Width shrinks toward the base; carry-expanded sum operands can add a digit, with small residual widths still decreasing in numeric magnitude until the leaf.

## 9. Pseudocode

```text
multiply(x,y):
  if x=0 or y=0: return 0
  if width fits leaf: return small x*y
  split x=xh*B+xl, y=yh*B+yl
  z0=multiply(xl,yl); z2=multiply(xh,yh)
  z1=multiply(xl+xh,yl+yh)-z0-z2
  return z2*B²+z1*B+z0
normalize signs; multiply magnitudes; restore sign
```

## 10. Dry Run

Decimal illustration 1234·5678: split B=100, giving xh=12,xl=34,yh=56,yl=78. z2=672, z0=2652, sum product=(12+34)(56+78)=46·134=6164. Cross term=6164-672-2652=2840. Recombine 672·10000+2840·100+2652=7006652. C++ recurses within these products down to one-digit leaves. Python uses binary splitting and a 16-bit base threshold, so this small example is a base case there; larger tested operands exercise its recursion. With -1234 and 5678 the magnitude is unchanged and the final sign is negative.

## 11. Time Complexity

Let n be the larger operand width (bits in Python, decimal digits in C++). For comparable-width dense operands, T(n)=3T(n/2+O(1))+Θ(n), yielding O(n^log₂3) ≈ O(n^1.585) digit/bit work. Carry handling and shifts/additions are linear in width; direct multiplication is restricted to constant-size leaves. Zero returns after validation/normalization; unequal widths or zero high/low pieces can reduce work, so not every input attains the worst bound. No random-input average is asserted.

## 12. Space Complexity

Peak auxiliary digit/bit storage is O(n) for sequential recursive children and retained intermediate products: active operand widths form a geometric series, while stack depth is O(log n). Output has at most the sum of input widths. C++ substring creation and decimal addition are included in these bounds; Python integer objects add allocation overhead. CLI text and conversion buffers are additional.

## 13. Python Implementation

[Complete runnable Python source](python/solution.py). API: `karatsuba_multiplication(a,b) -> int`. Integer fields require native int; bools, floats, strings, None, and int subclasses are invalid integer fields (TypeError). Domain/shape/range errors raise ValueError. Sequence inputs must be finite and indexable. Inputs are read only; outputs own their storage. The main guard prevents import-time demonstrations. No third-party runtime dependency is needed.

## 14. C++ Implementation

[Complete runnable C++ source](cpp/solution.cpp). API in namespace `algorithm_atlas`: `karatsuba_multiplication(const string&,const string&) -> string`. Define `ALGORITHM_ATLAS_NO_MAIN` before including it in a driver. Supported standards are C++17 and C++20; only standard headers are used. Invalid input raises std::invalid_argument. Resource failures remain errors. Exact numeric representation and bounds are part of the contract above; there is no silent overflow or approximate-success fallback.

## 15. Input and Output Examples

Run from this algorithm directory:

```sh
printf '1234 -5678\n' | python3 python/solution.py
g++ -std=c++17 -O2 -Wall -Wextra -pedantic cpp/solution.cpp -o /tmp/atlas-karatsuba-multiplication
printf '1234 -5678\n' | /tmp/atlas-karatsuba-multiplication
```

Both commands print:

```json
"-7006652"
```

CLI grammar: exactly two operands. Whitespace-separated ASCII signed decimal tokens only.
Output is one compact JSON value and newline. Invalid input exits nonzero,
writes stderr, and produces no result. Decimal strings in JSON preserve exact
integers without relying on a consumer's floating-point numeric precision.

From the repository root, run both language suites:

```sh
.venv/bin/python -m pytest -q --require-cpp dsa/divide-and-conquer/karatsuba-multiplication/tests
```


## 16. Edge Cases

Zero, negative zero in decimal input, all sign combinations, leading zeros, unequal lengths, carry-heavy nines, and signed-64 boundaries are tested. Python tests compare native multiplication; C++ decimal outputs are checked against that independent oracle up to thousands of bits, including zero against a 1001-digit operand. Invalid C++ strings and both CLIs are exercised. Built-in large multiplication appears only in test expectations, never as the recursive core.

## 17. Advantages

Exact results beyond machine-integer range with no external runtime dependency. The implementation exposes the algebra and supports very unequal signed operands.

## 18. Disadvantages and Limitations

String allocation and a one-digit C++ leaf threshold make this educational implementation slower than tuned integer libraries for many sizes. Python and C++ use different radices and thresholds. No maximum digit count is imposed; allocation, conversion, runtime, and stack resources impose practical limits. The code is neither constant-time nor a substitute for a security-reviewed arithmetic library.

## 19. When to Use It

Use it to study exact recursive multiplication and compare asymptotic arithmetic costs on moderate operand sizes.

## 20. When Not to Use It

Avoid it when a tuned library product, constant-time behavior, or strict resource/cancellation guarantees are required.

## 21. Comparison With Related Algorithms

| Method | Arithmetic work | Core idea |
| --- | --- | --- |
| Schoolbook | Θ(n²) | All digit pair products |
| Karatsuba | O(n^log₂3) | Three half-width products |
| [Strassen](../strassen-matrix-multiplication/README.md) | O(n^log₂7) matrix arithmetic | Seven block products; different problem |

## 22. Interview Questions

1. Derive the middle-product identity.
2. Why is the subtraction nonnegative for magnitudes?
3. How can sum operands gain a digit without invalidating the asymptotic recurrence?
4. Why must a large-integer leaf fallback have a fixed threshold?

## 23. Practice Problems

1. Trace 99·99 including carry-expanded sums.
2. Compare widths for a 200-digit times a one-digit operand.
3. Experiment with a separately documented larger constant leaf threshold and measure allocation costs.

## 24. References

- [University of Hawaii ICS311: divide/conquer, maximum subarray, and recurrences](https://courses.ics.hawaii.edu/ics311_f26/Notes/Topic-07.html).
- [Carnegie Mellon: deterministic closest-pair lecture and strip analysis](https://www.cs.cmu.edu/~15451-f18/lectures/lec23-closest-pair.pdf).
- [Carnegie Mellon algorithm notes](https://www.cs.cmu.edu/~avrim/451f11/lectures/lects1-10.pdf), including Karatsuba and Strassen algebra. Code and contract-specific proofs in this lesson are original educational implementations.

## 25. Author Attribution

Algorithm Atlas is maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). See the [MIT license](../../../LICENSE), [contribution policy](../../../CONTRIBUTING.md), and [development standards](../../../docs/development.md). This canonical A4 topic does not authorize implementing any other category. Passing tests does not imply owner review or phase approval.
