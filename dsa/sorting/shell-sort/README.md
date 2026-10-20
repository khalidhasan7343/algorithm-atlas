# Shell Sort

## 1. Algorithm Name

**Shell Sort** (Shellsort), using **Knuth's 3h + 1 gap sequence**: `1, 4, 13, 40, 121, ...`. Each pass performs insertion sorting on positions separated by the current gap. Gaps are generated as scalar values and traversed in reverse order, ending at one.

## 2. Overview

Insertion sort moves an item toward its destination one position at a time. Shell sort first lets items travel across larger gaps, then refines the order with smaller gaps. A final gap-one insertion pass establishes ordinary ascending order.

These implementations preserve the input by returning a copied container. The sorting core uses constant extra slots and no recursion. Shell sort is unstable: equal-key records can cross during a large-gap pass even though each individual insertion pass uses strict comparisons.

## 3. Problem Statement

Given a finite sequence of n consistently comparable items, return a permutation in nondecreasing order without modifying the input or its element objects. Do not assume stability.

Python exposes `shell_sort(values: Sequence[T]) -> list[T]`. C++ exposes `algorithm_atlas::shell_sort(const std::vector<T>&) -> std::vector<T>`. Elements need a consistent `<` relation; C++ elements must also be copy constructible and copy assignable. No key/comparator parameter is provided. Standalone input is signed decimal integers separated by whitespace, without a leading count.

## 4. Why Do We Need This Algorithm?

On reversed data, ordinary insertion sort can shift an item through almost the entire prefix. Large gaps let distant out-of-order items move across much of the array early. Later passes work with increasingly organized data while retaining insertion sort's simple core.

Shell sort demonstrates an intermediate design between elementary quadratic sorting and more complex divide-and-conquer methods. Its performance depends on the chosen gaps, so naming that sequence is part of specifying the algorithm rather than a minor implementation detail.

## 5. Real-World Applications

- **Moderate-sized arrays with limited core workspace:** gap insertion uses one saved item and a few indices, without a merge buffer or recursive stack. The preserving APIs here still allocate a result copy.
- **Simple native sorting routines:** a compact loop structure can be useful where implementation size and straightforward ownership are more important than stability or the strongest asymptotic guarantee. This is a design fit, not a claim of superiority over library sorting.
- **Teaching and workload experiments:** compare long-distance movement with ordinary insertion sorting and evaluate how different gap sequences affect comparisons on the same fixed datasets.

Shell sort is not a universal default. The [NIST definition](https://xlinux.nist.gov/dads/HTML/shellsort.html) emphasizes diminishing gaps and their importance to efficiency; this lesson specifically chooses Knuth gaps.

## 6. Core Intuition

For gap four, treat positions `0,4,8,...` as one short sequence, `1,5,9,...` as another, and so on. Insertion-sort each sequence. The resulting array is **4-sorted**: no item is smaller than the item four places before it.

Reduce the gap and repeat. The last gap is one, so its single sequence contains every position. That final insertion pass guarantees a completely sorted result. Earlier passes reduce the disorder it must repair, though their benefit depends on the data and gaps.

## 7. Prerequisites

Understand arrays, indices, integer division, loops, and [Insertion Sort](../insertion-sort/README.md). A gap pass applies the same prefix-insertion invariant to each residue class of indices. See the [glossary](../../../docs/glossary.md) for stability and the [complexity guide](../../../docs/complexity-cheatsheet.md) for bound notation.

No third-party runtime dependencies are required. Tests need pytest and a C++17/C++20 compiler using the setup in [CONTRIBUTING.md](../../../CONTRIBUTING.md).

## 8. Step-by-Step Working Process

1. Copy the sequence into `result`, leaving the input untouched.
2. Start `gap = 1`. While `gap < floor(n/3)`, replace it with `3*gap + 1`. This generates a suitable largest Knuth gap without storing the sequence.
3. For each index from `gap` through `n-1`, save its item. Walk backward by `gap`, shifting larger predecessors right by `gap`. Insert the saved item into its resulting position.
4. After the full pass, every gap-spaced subsequence is ordered.
5. Divide the gap by three using integer division. For these gaps, `floor((3h+1)/3) = h`, so the predecessor is recovered exactly.
6. Finish after processing gap one, when integer division produces zero. Return the copied result.

**Pass invariant:** before processing an index, earlier items in the same residue class are ordered. Shifting predecessors strictly larger than the saved item creates its insertion point and extends that ordered prefix. Other residue classes are unaffected by this insertion. Thus the complete pass makes the array gap-sorted.

The final pass has gap one, so its pass invariant proves global sortedness. Shifts and reinsertion preserve every item. Both the backward walk and decreasing gap sequence terminate.

## 9. Pseudocode

```text
SHELL_SORT(values):
    result = shallow copy of values
    gap = 1
    while gap < floor(length(result) / 3):
        gap = 3*gap + 1
    while gap >= 1:
        for index from gap through length(result)-1:
            item = result[index]
            position = index
            while position >= gap AND item < result[position-gap]:
                result[position] = result[position-gap]
                position = position - gap
            result[position] = item
        gap = floor(gap / 3)
    return result
```

The boundary comparison short-circuits before subtracting the gap. In C++, `gap < size/3` also guarantees that computing `3*gap+1` cannot overflow the unsigned size type. No list of gaps, recursive stack, built-in sort, or heap operation is used.

## 10. Dry Run

Input `[23, 12, 1, 8, 34, 54, 2, 3, 7, 4]` has n = 10. Gap generation starts at one: `1 < floor(10/3)`, so the first gap is four; the next growth test fails. The passes use gaps four and one.

| Gap | Processed index / action | Array afterward |
| --- | --- | --- |
| 4 | Indices 4, 5, 6 need no shifts | `[23, 12, 1, 8, 34, 54, 2, 3, 7, 4]` |
| 4 | Index 7: insert 3 ahead of 8 | `[23, 12, 1, 3, 34, 54, 2, 8, 7, 4]` |
| 4 | Index 8: shift 34 and 23, insert 7 at 0 | `[7, 12, 1, 3, 23, 54, 2, 8, 34, 4]` |
| 4 | Index 9: shift 54 and 12, insert 4 at 1 | `[7, 4, 1, 3, 23, 12, 2, 8, 34, 54]` |
| 1 | Index 1: insert 4 before 7 | `[4, 7, 1, 3, 23, 12, 2, 8, 34, 54]` |
| 1 | Index 2: insert 1 at 0 | `[1, 4, 7, 3, 23, 12, 2, 8, 34, 54]` |
| 1 | Index 3: insert 3 after 1 | `[1, 3, 4, 7, 23, 12, 2, 8, 34, 54]` |
| 1 | Index 4: 23 already fits | `[1, 3, 4, 7, 23, 12, 2, 8, 34, 54]` |
| 1 | Index 5: insert 12 before 23 | `[1, 3, 4, 7, 12, 23, 2, 8, 34, 54]` |
| 1 | Index 6: insert 2 after 1 | `[1, 2, 3, 4, 7, 12, 23, 8, 34, 54]` |
| 1 | Index 7: insert 8 before 12 | `[1, 2, 3, 4, 7, 8, 12, 23, 34, 54]` |
| 1 | Indices 8 and 9 already fit | `[1, 2, 3, 4, 7, 8, 12, 23, 34, 54]` |

The original sequence is unchanged. For instability, `[2a, 2b, 0c, 0d, 0e, 3f]` uses gap four. Inserting `0e` moves `2a` to index four, past `2b`. The final gap-one pass yields `[0e, 0c, 0d, 2b, 2a, 3f]`, reversing the two equivalent twos.

## 11. Time Complexity

Let n count elements, with O(1) comparisons and copies. There are Θ(log n) Knuth gap passes. Their costs depend on how far items move along each gap-spaced sequence.

| Case | Bound | Explanation |
| --- | --- | --- |
| Best, sorted or all-equivalent input | Θ(n log n) | Every gap pass visits its n−gap insertion positions; no whole-sort early exit exists. |
| Average | No universal tight bound claimed | Depends on gap sequence and input distribution; no unspecified average exponent is asserted. |
| Worst, these Knuth gaps | O(n^(3/2)) | Standard comparison bound for the 3h+1 sequence; gap choice is essential. |
| Empty or singleton | Θ(1) | No insertion positions are visited. |

On ordered data, every visited item needs one unsuccessful `<` comparison. Summing `n-gap` over logarithmically many geometric gaps gives Θ(n log n). Initial copying and gap generation add O(n) and O(log n), respectively.

The [authors' Princeton Shell implementation](https://github.com/kevin-wayne/algs4/blob/master/src/main/java/edu/princeton/cs/algs4/Shell.java) documents the 3h+1 comparison/exchange bound. This lesson uses shifting and one reinsertion instead of repeated adjacent-gap exchanges; shifts correspond to those exchanges, preserving the upper-bound analysis. This is not a claim that all Shell-sort gap choices share that bound. Expensive record or big-integer operations add their own costs.

## 12. Space Complexity

The core stores a gap, loop indices, and one saved item: Θ(1) extra slots. Gaps are generated and reversed arithmetically; no gap array or recursion is allocated. The preserving API's returned copy needs Θ(n) new storage, so total additional storage relative to the input is Θ(n).

Python copies references shallowly. C++ copies element objects and uses one temporary item; element-owned resources may change actual byte costs. CLI parsing also buffers textual input and values, so constant core workspace does not mean constant whole-process memory.

## 13. Python Implementation

[`python/solution.py`](python/solution.py) provides `shell_sort(values: Sequence[T]) -> list[T]`. It uses only `<`, copies the sequence once, then executes gap insertion directly. Tuple inputs are accepted and produce lists. Element objects are not modified or deep-copied.

For example, `shell_sort((3, 1, 2))` returns `[1, 2, 3]`. Importing the module does not execute its main guard. Python integers can exceed the C++ CLI range, subject to memory and the interpreter's integer-string digit limit.

## 14. C++ Implementation

[`cpp/solution.cpp`](cpp/solution.cpp) defines `algorithm_atlas::shell_sort(const std::vector<T>&)` with standard C++17/C++20 headers. Define `ALGORITHM_ATLAS_NO_MAIN` before including it in an educational API driver.

Indices use `std::size_t`. The guard precedes `position-gap`, avoiding unsigned underflow. Gap growth checks `gap < size/3` before multiplying by three, avoiding overflow; subsequent division reaches one and then zero. The implementation does not default construct record elements. The CLI uses range-checked `std::from_chars` after validating signed ASCII decimal grammar.

## 15. Input and Output Examples

From the repository root:

```sh
printf '23 12 1 8 34 54 2 3 7 4\n' | .venv/bin/python dsa/sorting/shell-sort/python/solution.py
c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/shell-sort/cpp/solution.cpp -o /tmp/atlas-shell-sort
printf '23 12 1 8 34 54 2 3 7 4\n' | /tmp/atlas-shell-sort
```

Both print:

```text
1 2 3 4 7 8 12 23 34 54
```

There is **no leading count**. Input `3 -1 0 -1 3` prints `-1 -1 0 3 3`. Empty input prints one newline. Input can span lines and tabs. Tokens `+2`, `-0`, and `0001` are valid, and output uses normalized decimal formatting.

Run Python and C++17/C++20 tests:

```sh
.venv/bin/python -m pytest dsa/sorting/shell-sort/tests --require-cpp
```

Tests cover known answers, the dry-run result, fixed-seed random inputs around gap boundaries, large ordered/reversed/gap-spaced patterns, strict-`<` tagged records, instability, unchanged input, signed extremes, generic strings, sorted-input pass counts, and CLI failures.

## 16. Edge Cases

- Empty/singleton inputs allocate new containers but perform no insertion work.
- Short inputs may use only gap one, behaving as insertion sort.
- Gap generation uses integer `n/3`; lengths near 3, 4, 12, 13, 39, 40, and 121 test boundaries, along with actual growth-transition neighbors.
- Equal keys remain ordered within a single gap subsequence, but can cross globally. Stability is not guaranteed.
- Negatives and signed integer extremes need no key arithmetic, so sorting does not overflow their values.
- Incomparable Python items raise `TypeError` without changing the input. NaN and inconsistent custom comparisons violate the ordering contract.
- CLI tokens such as `1.5`, `0x10`, `1_000`, bare signs, and non-ASCII digits are rejected before output. C++ values must fit `long long`: −2⁶³ through 2⁶³−1 on tested 64-bit platforms. Python accepts larger values within conversion/resource limits.
- Allocation and comparison errors are not converted into custom return values.

## 17. Advantages

The implementation is iterative, compact, and generic over comparable records. Large gaps move items across the array before the final insertion pass. It needs no merge buffer, recursive call stack, or stored gap sequence beyond the returned copy. Knuth gaps provide a documented subquadratic worst-case bound.

## 18. Disadvantages and Limitations

It is unstable, and its performance depends strongly on gap selection. Sorted data still incurs logarithmically many full passes, so this version does not have insertion sort's linear ordered-input best case. The worst bound is weaker than O(n log n) comparison sorting. Its preserving API still allocates linear result storage. No key/comparator parameter, custom gap list, external sorting, or benchmark advantage is claimed.

## 19. When to Use It

Use it for studying gap-based insertion sorting, or for modest random-access workloads where an iterative, simple core and small workspace are useful and stable ties are unnecessary. Evaluate actual workload performance before choosing it for a native application. The preserving API fits cases where keeping the original sequence justifies allocation.

## 20. When Not to Use It

Choose [Insertion Sort](../insertion-sort/README.md) for very small or already ordered inputs when its linear best case matters. Choose [Merge Sort](../merge-sort/README.md) or [Tim Sort](../tim-sort/README.md) for stable ordering. Choose [Heap Sort](../heap-sort/README.md) for constant core workspace with a stronger O(n log n) worst bound. Use production library sorting when its existing features and tuning meet the application's requirements.

## 21. Comparison With Related Algorithms

Extra space below excludes optional preserving result copies. Bounds refer to the named variants and comparison assumptions.

| Algorithm / variant | Best | Worst | Stable? | Core space |
| --- | --- | --- | --- | --- |
| This Shell Sort, Knuth gaps | Θ(n log n) | O(n^(3/2)) | No | Θ(1) |
| Standard Insertion Sort | Θ(n) | Θ(n²) | Yes, strict shifts | Θ(1) |
| This project's iterative Heap Sort | Θ(n), all equal | Θ(n log n) | No | Θ(1) |
| Standard top-down Merge Sort | Θ(n log n) | Θ(n log n) | Yes | Θ(n) buffer plus stack |
| Adaptive Tim Sort family | Θ(n) | O(n log n) | Yes | O(n) |

A gap pass completely insertion-sorts every residue class. This distinguishes Shell sort from merely comparing each pair at that distance once. Another gap sequence needs its own analysis; these bounds do not apply automatically.

## 22. Interview Questions

1. What does h-sorted mean? Show the four residue classes for a gap-four pass on ten items.
2. Why does finishing with gap one guarantee sortedness even if the earlier passes were unhelpful?
3. Why can strict comparison preserve ties within a pass but fail to provide global stability? Trace the tagged example.
4. Why is sorted-input work Θ(n log n) here? Count `n-gap` visits per pass rather than assuming an early global exit.
5. How do scalar 3h+1 generation and integer division avoid a stored list of gaps?
6. What prevents unsigned underflow and gap-growth overflow in C++?

## 23. Practice Problems

1. Trace gaps four and one on `[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]`, showing each residue class.
2. Count comparisons on sorted input of size 100 and verify `(100-40)+(100-13)+(100-4)+(100-1) = 342`.
3. Construct another labeled instability example and distinguish key correctness from stability.
4. Compare several explicitly defined gap sequences using fixed seeds and identical input arrays. Report measurements separately from asymptotic proofs.
5. Design a mutating API and restate its memory contract; consider how comparison exceptions can leave partially rearranged data.

These exercises describe further study, not extra shipped algorithm variants.

## 24. References

- Robert Sedgewick and Kevin Wayne, [Shell.java in the authors' Algorithms repository](https://github.com/kevin-wayne/algs4/blob/master/src/main/java/edu/princeton/cs/algs4/Shell.java) — primary reference for Knuth gaps, complexity, and instability. Its implementation uses exchanges; this lesson independently implements insertion shifts.
- [NIST Dictionary of Algorithms and Data Structures: Shell sort](https://xlinux.nist.gov/dads/HTML/shellsort.html) — diminishing-increment definition and the importance of gap choice. NIST discusses other increments too; this lesson's bound is tied to 3h+1.
- [Algorithm Atlas complexity guide](../../../docs/complexity-cheatsheet.md) — notation and space accounting.

References provide conceptual and analytical background. No reference source code or licensed explanatory passages are copied.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). This lesson belongs to [Algorithm Atlas](../../../README.md) and is distributed under its [MIT License](../../../LICENSE). Read [CONTRIBUTING.md](../../../CONTRIBUTING.md) for attribution, testing, and phase-review requirements.
