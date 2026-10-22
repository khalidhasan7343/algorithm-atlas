# Fractional Knapsack

## 1. Algorithm Name

Fractional Knapsack

## 2. Overview

Maximize total value when each item can be divided continuously. Greedy selection takes higher value per unit weight first, with exact rational arithmetic for comparisons, total value and returned fractions.

## 3. Problem Statement

Given n≤10000 positive integer weights in 1..10^6, nonnegative integer values in 0..10^6 and integer capacity C in 0..10^9, choose fractions f_i in [0,1] maximizing sum(v_i f_i), subject to sum(w_i f_i)≤C. Return (exact total value, one exact fraction per original item). Python uses Fraction; C++ uses reduced nonnegative numerator/denominator pairs in KnapsackResult. Zero/negative weights and negative values are rejected. Zero-value items remain unselected, even if capacity remains. Equal ratios prefer the earlier original position.

## 4. Why Do We Need This Algorithm?

In the divisible model, every unit of weight has a fixed marginal value. Spending capacity on a lower marginal value while a higher-value item remains available cannot improve the result. Exact comparison prevents rounding from changing that ordering.

## 5. Real-World Applications

A simplified allocation of divisible materials or bandwidth with linear independent value can use this model. Minimum batches, nonlinear prices, mandatory whole items and coupled requirements need different formulations.

## 6. Core Intuition

Order by decreasing density v/w, comparing v_a·w_b with v_b·w_a. Fill each positive-value item completely if possible; otherwise take exactly the remaining capacity divided by its weight and stop. At most one positive item is partial.

## 7. Prerequisites

Ratios, fractions, sorting and an exchange argument. Compare the completed [0/1 Knapsack](../../dynamic-programming/zero-one-knapsack/README.md), where items are indivisible and density ordering is not generally optimal.

## 8. Step-by-Step Working Process

Validate equal lengths and all domains. Sort original indices using cross products, then original-index ties. Start all fractions at zero and capacity unchanged. Take min(weight,remaining) from each positive-value item and record its reduced fraction. Add the corresponding exact value; stop at zero remaining capacity or zero density.

Greedy-choice proof: if a feasible allocation uses some lower-density weight while a higher-density item is not full, transfer equal weight to the latter. Capacity is unchanged and value does not decrease; it increases for unequal densities. Repeating this exchange yields a density-ordered prefix with at most one partial item. Equal-density transfers favor earlier indices as specified. After filling a prefix, the remaining capacity and remaining items form the same optimization problem, proving optimal substructure. Zero-value items may be omitted without lowering value.

## 9. Pseudocode

```text
order ← indices sorted by descending exact value/weight, then index
fractions[0..n-1] ← 0; total ← 0; remaining ← C
for i in order:
    if remaining=0 OR value[i]=0: break
    take ← min(weight[i],remaining)
    fractions[i] ← exact_fraction(take,weight[i])
    total ← total + value[i]*fractions[i]
    remaining ← remaining-take
return total,fractions
```

## 10. Dry Run

For weights [10,20,30], values [60,100,120], capacity 50:

| Item | Density | Remaining before | Fraction | Added value |
| --- | --- | --- | --- | --- |
| 0 | 6 | 50 | 1 | 60 |
| 1 | 5 | 40 | 1 | 100 |
| 2 | 4 | 20 | 2/3 | 80 |

The final value is 240 and fractions [1,1,2/3]. The fraction is needed: selecting only whole items cannot produce this allocation. With weight 3, value 2 and capacity 1, the exact total is 2/3, not a rounded decimal.

## 11. Time Complexity

Validation and output initialization are O(n); sorting and selection give O(n log(n+1)) worst time with O(n) scan work. Python sorting can be linear on already ordered ratios; C++ std::sort provides an O(n log(n+1)) comparison bound. No average distribution is assumed. GCD reduction and ratio comparisons operate on the documented bounded integers; if the caps are removed, bit-complexity costs must also be included.

## 12. Space Complexity

O(n) auxiliary sorted indices and O(n) fraction output; no algorithm recursion. Python sorting may allocate O(n) temporary space. Exact rational values use bounded words in C++ under this contract. The input is not mutated; streaming without sorting would require density-ordered input.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) exposes `fractional_knapsack(weights, values, capacity)`. Native integer inputs exclude bool and floating point; invalid data/resource bounds raise ValueError. Inputs are read only, results own their containers, and importing the module performs no I/O. The implementation follows the strategy in sections 6–9.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) exposes `fractional_knapsack(weights, values, capacity)` in namespace `atlas_greedy`. Define `ALGORITHM_ATLAS_NO_MAIN` when including it in an API driver. C++17 and C++20 use standard containers and signed 64-bit integers. The shared [header](../common.hpp) handles validation/CLI utilities; the algorithm itself is implemented in this canonical source. Invalid data/resource bounds throw invalid_argument. Inputs are const references.

## 15. Input and Output Examples

From the repository root, input is **capacity, count n, then n weight/value pairs**. Numeric tokens are ASCII signed decimal integers. Counts must match exactly; missing, malformed or extra tokens produce exit 2, a stderr diagnostic, and empty stdout. A successful run prints one JSON value and a newline.

```sh
printf '%s\n' '50 3 10 60 20 100 30 120' | .venv/bin/python dsa/greedy/fractional-knapsack/python/solution.py
g++ -std=c++17 -Wall -Wextra -pedantic dsa/greedy/fractional-knapsack/cpp/solution.cpp -o /tmp/atlas-fractional-knapsack
printf '%s\n' '50 3 10 60 20 100 30 120' | /tmp/atlas-fractional-knapsack
```

Both print:

```text
{"value":[240,1],"fractions":[[1,1],[1,1],[2,3]]}
```

Use `-std=c++20` for the other supported standard. Run `.venv/bin/python -m pytest dsa/greedy/fractional-knapsack --require-cpp` to execute Python, C++17 and C++20 tests. Independent expected values and boundary cases are in the [test cases](tests/cases.py).

## 16. Edge Cases

Empty input returns value 0 and []. Zero capacity returns all-zero fractions. If capacity exceeds all positive-value weight, take all positive-value items and leave zero-value ones at zero. Equal density is deterministic by original index. Invalid weights are rejected even when capacity is zero. Tests independently enumerate all small LP vertices: each has zero/one fractions except at most one partial item, then maximize exact objective and the stated allocation tie policy.

## 17. Advantages

The greedy proof applies directly to divisible linear value. Both languages return exact reduced fractions, so no tolerance is needed for their shared supported domain. Returned fractions make feasibility and value independently checkable.

## 18. Disadvantages and Limitations

Fractional selection is essential; using this strategy for indivisible 0/1 items is incorrect. The API excludes zero-weight “free value” items, negative values, real-valued inputs and nonlinear constraints. Density cross products are ≤10^12. Full-item value is ≤10^10; a total rational numerator is at most 10^10·10^6+10^12, below signed-64, with denominator≤10^6. No floating point is used internally. Converting results to float externally can round, so preserve numerator/denominator pairs for exactness.

## 19. When to Use It

Use when items are divisible, values scale linearly with amount, and a single weight capacity is the only coupling constraint.

## 20. When Not to Use It

Use 0/1 DP or another combinatorial method for indivisible choices. Use linear programming or domain-specific optimization for multiple constraints, lower bounds or nonlinear returns.

## 21. Comparison With Related Algorithms

| Problem | Fractions allowed | Optimal strategy |
| --- | --- | --- |
| This fractional knapsack | yes | density greedy |
| 0/1 knapsack | no | capacity/value DP or other exact search |
| Unbounded integer knapsack | whole repeated copies | different DP |
| General linear program | several constraints | vertex/LP methods |

## 22. Interview Questions

What exchange preserves capacity? Why can there be at most one partial positive item? Why do ratio comparisons use cross products? Why does density ordering fail for 0/1 choices? What changes if zero-weight items are supported?

## 23. Practice Problems

Verify returned fractions by computing exact used weight and value. Construct a 0/1 counterexample. Then define a separate API that permits zero-weight positive-value items and document their treatment before implementation.

## 24. References

[ETH Zürich: Greedy Algorithms lecture handout](https://lec.inf.ethz.ch/DA/2017/slides/daLecture15.en.handout.pdf) covers fractional knapsack, Activity Selection and Huffman Coding. This exact-rational API, input caps and deterministic allocation are independently specified here; no lecture implementation is copied.

## 25. Author Attribution

Algorithm Atlas is maintained by **MD.Khalid Hasan** ([GitHub](https://github.com/khalidhasan7343)). See the [repository](https://github.com/khalidhasan7343/algorithm-atlas), [MIT License](../../../LICENSE), and [contribution policy](../../../CONTRIBUTING.md).
