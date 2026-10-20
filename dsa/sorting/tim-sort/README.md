# Tim Sort

## 1. Algorithm Name

**Tim Sort (Timsort)**, named for Tim Peters. This lesson implements an educational version of the classic stable natural-run algorithm: run detection, computed minrun, stable binary insertion, a corrected run-stack merge policy, and galloping searches.

The merge policy is the classic length-invariant policy with the four-run lookback correction. It is distinct from the Powersort policy used by newer CPython releases. Its full forward buffers and fixed galloping trigger are explicit simplifications, described below.

## 2. Overview

Tim Sort looks for order that already exists instead of splitting every input at predetermined positions. It finds monotonic runs, reverses strictly descending runs, extends short runs with binary insertion, and merges neighboring runs in a controlled order.

During a merge, a run that repeatedly supplies the next item can be searched exponentially to copy a whole winning block. This galloping step can reduce comparisons when the runs have long noninterleaving regions. The public functions return stable sorted copies and preserve their inputs.

## 3. Problem Statement

Given `n` elements with a consistent `<` ordering, return them in nondecreasing order while retaining the original relative order of equivalent elements. Do not modify the supplied sequence.

- Python: `tim_sort(values: Sequence[T]) -> list[T]`.
- C++: `algorithm_atlas::tim_sort<T>(const std::vector<T>& values) -> std::vector<T>`.

Elements need only `<` for ordering. Python copies references into a new list. C++ requires elements that can be copied, assigned, and swapped; they need not be default-constructible. Comparisons must not mutate their operands and must define a consistent strict weak ordering. Floating NaNs do not provide the required ordering.

Both CLIs accept whitespace-separated signed ASCII decimal integers. Python integers have arbitrary precision subject to resources. C++ CLI integers must fit the platform's `long long`, commonly the signed 64-bit interval.

## 4. Why Do We Need This Algorithm?

Data is often already ordered in stretches: an old sorted batch followed by a new batch, a descending export, or groups retaining a prior order. Ignoring those runs can waste comparisons. Tim Sort combines linear detection of that structure with a general O(n log n) worst-case sorting strategy.

Stability also makes successive sorts useful. If records are already ordered by a secondary key, a stable sort on the primary key retains the secondary ordering within each primary-key group. An explicit comparator or key interface is not included here; records express their comparison key through `<`.

## 5. Real-World Applications

- **Object sorting in language runtimes:** OpenJDK includes a [TimSort implementation](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/TimSort.java) for object arrays. This establishes a concrete use of the algorithm family, not a claim that this educational source is the JDK implementation.
- **Historical Python list sorting:** CPython's [3.10 design notes](https://raw.githubusercontent.com/python/cpython/3.10/Objects/listsort.txt) document the classic natural-run approach. The [current notes](https://github.com/python/cpython/blob/main/Objects/listsort.txt) describe a Powersort merge policy and further refinements; this lesson intentionally teaches the earlier length-invariant policy.
- **Partially ordered application records:** combining ordered batches of timestamps, scores, or display records can expose long runs. Stable merging preserves equal-key order, such as an existing arrival order.
- **Multiple-key ordering:** a stable primary-key sort can retain an earlier secondary-key order. This is a general stability application and assumes the record's `<` compares the intended key.

No deployment or benchmark result is claimed for the repository implementation.

## 6. Core Intuition

Imagine receiving several sorted piles already placed consecutively on a table. Keep useful piles intact. Turn a strictly descending pile around. If a pile is tiny, insert a few following elements into it to avoid excessive tiny merges.

Remember the pending piles on a stack. Merge adjacent piles when their sizes become poorly balanced; keeping much larger piles lower in the stack prevents an uncontrolled accumulation of pending work. When one pile repeatedly wins a merge, jump ahead to the boundary of its winning block rather than comparing every item with the opposing head.

## 7. Prerequisites

- Stable [insertion sort](../insertion-sort/README.md) and [merge sort](../merge-sort/README.md).
- Arrays, stacks, binary search, and exponential search.
- [Complexity notation](../../../docs/complexity-cheatsheet.md) and [stability vocabulary](../../../docs/glossary.md).
- The distinction between an element being equivalent under `<` and being identical as an object.

The implementation uses an iterative pending-run stack; it does not recurse.

## 8. Step-by-Step Working Process

1. Copy the input. Compute minrun by repeatedly shifting the length right until it is below `64`, remembering whether any discarded bit was `1`, then adding that bit to the remaining length. For lengths at least `64`, minrun lies in `[32, 64]`; shorter inputs use their length.
2. Scan from the next unprocessed position. A natural run is nondecreasing or **strictly** descending. Reverse only the latter. Strictness prevents reversal from exchanging equal-key items.
3. If the run is shorter than minrun, extend it to minrun or the end of input, whichever comes first. Stable binary insertion finds the position **after** earlier equivalent keys, then shifts the intervening items.
4. Push its `(start, length)` onto the pending-run stack. Restore the length inequalities by merging adjacent runs chosen by the corrected collapse policy below.
5. Each merge writes from left to right, selecting the left run on ties. After seven consecutive wins from one run, use exponential search followed by binary search to find a whole block that can be copied.
6. Continue discovering runs. Once all input is processed, force-collapse the remaining stack, choosing between the top two adjacent merge opportunities by neighboring lengths, until one run remains.

**Pending-stack invariants:** after normal collapse, lengths decrease from bottom to top, and each older length exceeds the sum of the next two: `A > B + C` and `B > C`. The corrected rule also checks the triple one level below the top triple. A merge can violate that deeper inequality even when the top three appear valid. The [2015 CPython issue](https://github.com/python/cpython/issues/67703) records why the older check was insufficient.

**Correctness and stability:** each discovered or extended run is an ordered, stable permutation of its input interval. Only adjacent intervals merge, preserving the original order between equal keys from different intervals. Ordinary merge takes left ties first; a left gallop includes keys equivalent to the right head, while a right gallop stops before keys equivalent to the left head. Merging therefore preserves the invariant that every pending run is ordered and stable. Each merge removes one stack entry, and scanning advances by a positive run length, so both processes terminate. The final run covers every element exactly once.

## 9. Pseudocode

All array intervals are half-open. `length[i]` denotes the length of pending run `i`, from oldest to newest.

```text
MINRUN(n):
    discarded = 0
    while n >= 64:
        discarded = discarded OR (n AND 1)
        n = n >> 1
    return n + discarded

TIM_SORT(input):
    a = copy(input)
    if length(a) < 2: return a
    minimum = MINRUN(length(a))
    stack = []
    start = 0
    while start < length(a):
        run = next nondecreasing or strictly descending natural run
        if descending: reverse that run
        target = min(minimum, length(a) - start)
        if run.length < target:
            binary-insert following items into the run, after equivalent keys
            run.length = target
        push (start, run.length)
        COLLAPSE(a, stack)
        start = start + run.length
    while stack has at least 2 entries:
        i = stack.size - 2
        if i > 0 and length[i - 1] < length[i + 1]: i = i - 1
        MERGE_AT(a, stack, i)
    return a

COLLAPSE(a, stack):
    while stack has at least 2 entries:
        i = stack.size - 2
        top_bad = i > 0 and length[i - 1] <= length[i] + length[i + 1]
        deeper_bad = i > 1 and length[i - 2] <= length[i - 1] + length[i]
        if top_bad or deeper_bad:
            if length[i - 1] < length[i + 1]: i = i - 1
        else if length[i] > length[i + 1]:
            return
        MERGE_AT(a, stack, i)

MERGE_AT(a, stack, i):
    merge adjacent runs i and i + 1 stably
    replace those two stack entries with their combined interval
```

The merge and galloping operations match the actual implementation:

```text
STABLE_MERGE(a, start, middle, end):
    if not (a[middle] < a[middle - 1]): return
    left = copy(a[start:middle]); right = copy(a[middle:end])
    i = j = 0; out = start; left_wins = right_wins = 0
    while both runs have items:
        if right[j] < left[i]:
            a[out] = right[j]; j += 1
            right_wins += 1; left_wins = 0
        else:
            a[out] = left[i]; i += 1
            left_wins += 1; right_wins = 0
        out += 1
        if either run is exhausted: break
        if left_wins >= 7:
            stop = GALLOP_BOUND(left, i, length(left), right[j], upper=true)
            copy left[i:stop] to a at out; advance i and out
            left_wins = 0
        else if right_wins >= 7:
            stop = GALLOP_BOUND(right, j, length(right), left[i], upper=false)
            copy right[j:stop] to a at out; advance j and out
            right_wins = 0
    copy the unconsumed tail into a

GALLOP_BOUND(run, start, end, pivot, upper):
    precedes(x) = not (pivot < x) if upper, otherwise x < pivot
    if start = end or not precedes(run[start]): return start
    low = start + 1; offset = 1
    while start + offset < end and precedes(run[start + offset]):
        low = start + offset + 1
        offset = 2 * offset + 1
    high = min(end, start + offset + 1)
    binary-search [low, high) for the first item not satisfying precedes
    return that boundary
```

C++ caps the exponential offset before multiplication to avoid unsigned overflow. Binary insertion similarly uses an upper-bound search under `<`, then explicit rightward shifts.

## 10. Dry Run

Use an input large enough to require actual natural-run merges:

```text
[96, 97, ..., 127,  64, 65, ..., 95,  32, 33, ..., 63,  0, 1, ..., 31]
```

There are `128` elements. Minrun is `32`, so each natural ascending run already meets the threshold. No binary extension is needed.

| Event | Pending lengths before collapse | Merge and result |
| --- | --- | --- |
| Discover `[96..127]` | `[32]` | Keep the run |
| Discover `[64..95]` | `[32, 32]` | Merge intervals `[0,32)` and `[32,64)` into `[64..127]`; stack `[64]` |
| Discover `[32..63]` | `[64, 32]` | `64 > 32`, so keep both |
| Discover `[0..31]` | `[64, 32, 32]` | `64 <= 32 + 32`: merge the top two into `[0..63]`, giving `[64, 64]` |
| Continue collapse | `[64, 64]` | Merge into `[0..127]`; stack `[128]` |

Inside the first merge, right values `64` through `70` win seven comparisons. The right gallop searches the remaining right run for the first value not strictly below left head `96`. Every remaining right item qualifies, so it copies `71..95` as one block and then appends left tail `96..127`. The next two merges work analogously. The tested merge intervals are `(0,32,64)`, `(64,96,128)`, and `(0,64,128)`.

A stability example uses left keys `[0a, 1a, ..., 20a]` and right keys `[10b, 11b, ..., 30b]`. When a left gallop reaches key `10`, its upper-bound rule includes `10a` before `10b`. In the opposite arrangement, a right gallop uses a strict lower bound and stops before a key equal to the left head. Thus both directions retain earlier-run ties first.

## 11. Time Complexity

Let `n` be the number of elements, assuming constant-time comparisons and copies or assignments.

| Case | Bound | Explanation |
| --- | --- | --- |
| Best: one nondecreasing, strictly descending, or all-equal run | Θ(n) | Copy, scan with `n - 1` comparisons, and possibly reverse; no merge |
| Average over uniformly random permutations of distinct keys | Θ(n log n) | Many short runs require general comparison sorting |
| Worst | O(n log n) | Corrected classic merge policy controls merge work; each merge is linear in its combined lengths |
| Empty or singleton input | O(1) | Copy and immediate return |

Run discovery is linear. Binary insertion may move quadratically many items within one extended run, but each extension is at most `64` items; treating that fixed threshold as a constant gives O(n) total extension work. The corrected merge strategy supplies the O(n log n) worst-case bound; an arbitrary sequence of merges, such as repeatedly merging a huge prefix with one tiny run, would not justify that claim. The [TimSort complexity paper](https://arxiv.org/abs/1805.08612) analyzes the classic policies.

Galloping locates a block of length `b` with O(1 + log(b + 1)) comparisons, including the empty-block case, and then copies its `b` elements. This does not make an entire merge logarithmic: elements must still be written. Its fixed trigger changes constants, not the O(n log n) upper bound. A linear best case reflects actual detected runs, not a guarantee for every informally “nearly sorted” pattern.

Python big integers, strings, and user-defined comparisons can have nonconstant operation costs. CLI parsing and formatting also depend on textual input length. No measured speed advantage over native sorting libraries is claimed.

## 12. Space Complexity

- **Returned copied container:** O(n) slots in both languages, even for an already ordered input.
- **Merge buffers:** O(n) worst-case additional slots; this implementation copies both participating runs, whose combined length is at most `n`.
- **Pending-run stack:** O(log n) entries. The strict size inequalities make older lengths grow at least geometrically toward the bottom; a transient push adds only one entry.
- **Recursive call stack:** O(1); the implementation is iterative.

Overall additional space relative to the caller's input is **O(n)**. A single natural run needs no merge buffer, but the public copy still costs O(n). Python slices used for block copies can create temporary O(n) lists within the same bound; objects themselves are not deep-copied. C++ copies element objects into its buffers. CLI token storage adds space proportional to the input text.

## 13. Python Implementation

Source: [python/solution.py](python/solution.py).

`tim_sort` creates a list copy and delegates to `_TimSorter`, which owns the pending intervals. Separate helpers implement natural runs, stable binary insertion, galloping bounds, and merges. `_collapse_choice` makes the four-run policy explicit and independently testable.

Only `<` compares elements. Descending reversal uses swaps, and ordinary merge selects the left item when `right < left` is false. No `sorted()` or `list.sort()` delegates the algorithm. The CLI is guarded so imports do not execute it; malformed tokens produce a nonzero exit and stderr error before any sorted output.

## 14. C++ Implementation

Source: [cpp/solution.cpp](cpp/solution.cpp).

The template API lives in `algorithm_atlas`; its implementation helpers live in `tim_sort_detail`. `TimSorter<T>` copies the supplied vector, tracks adjacent `(start, length)` intervals, and returns its owned storage by move. Buffers use iterator-range constructors rather than default-sized vectors, supporting copyable records with deleted default constructors.

The implementation checks bounds before subtracting indices or doubling galloping offsets. Adjacent run lengths sum to at most the input size, so their bookkeeping sums are representable. Define `ALGORITHM_ATLAS_NO_MAIN` before including the source in a driver to omit its CLI. C++17 and C++20 are supported.

The CLI validates a complete decimal token before `std::from_chars`, handles a leading `+` explicitly, and rejects overflow or partial conversion. No output is produced until every input token has been parsed successfully.

## 15. Input and Output Examples

Run these commands **from the repository root**. Python requires Python 3.11+ without third-party runtime packages; C++ requires a supporting compiler.

```sh
printf '5 2 4 2 1\n' | python3 dsa/sorting/tim-sort/python/solution.py
# Output: 1 2 2 4 5

c++ -std=c++17 -Wall -Wextra -pedantic dsa/sorting/tim-sort/cpp/solution.cpp -o /tmp/atlas-tim-sort
printf '5 2 4 2 1\n' | /tmp/atlas-tim-sort
# Output: 1 2 2 4 5

printf '+3 -7 0 -7\n' | /tmp/atlas-tim-sort
# Output: -7 -7 0 3

printf '' | python3 dsa/sorting/tim-sort/python/solution.py
# Output: one empty line
```

There is no length prefix. Every successful output ends in a newline. The short numeric example demonstrates the CLI; the 128-element trace above and persistent tests demonstrate the natural-run merge path. Run both language test suites, including compiled and executed C++17/C++20:

```sh
.venv/bin/python -m pytest dsa/sorting/tim-sort/tests --require-cpp
```

Tests cover natural runs, minrun boundaries, seeded differential cases, large arrays, tagged stability, the four-run regression, adversarial stack patterns, gallop bounds, both gallop directions, input preservation, exact monotone comparison counts, and CLI validity. A comparison-budget test verifies that galloping actually skips a long winning block rather than merely naming a scalar merge “galloping.”

## 16. Edge Cases

| Condition | Behavior |
| --- | --- |
| Empty or singleton sequence | Separate empty or one-item result |
| Already nondecreasing | One natural run; `n - 1` comparisons |
| Strictly descending | Reverse one run; `n - 1` comparisons |
| Descending data with equal-key plateaus | Strict descent stops at equality; later stable processing retains tag order |
| All keys equal | Nondecreasing run; no reversal or unstable movement |
| Last run shorter than minrun | Extend only to the actual end; no out-of-bounds read |
| Lengths around `31`, `32`, `63`, `64`, `65`, `127`, `128`, `129` | Correct threshold/rounding behavior and merge boundaries |
| Long overlapping runs with ties | Left ties first in scalar and galloping paths |
| Many irregular run lengths | Corrected four-run collapse restores all inequalities |
| Incomparable Python elements | Comparison raises, while caller's container stays unchanged |
| C++ non-default-constructible record | Supported when copy/assignment and `<` satisfy the contract |
| Invalid CLI token | Nonzero exit, stderr error, no partial stdout |
| C++ CLI out-of-range integer | Rejected by checked conversion |

CLI tokens allow one optional sign followed by ASCII digits; underscores, hexadecimal notation, decimals, sign-only tokens, and non-ASCII digit spellings are rejected. Python CLI disables its decimal conversion digit guard only when run, allowing arbitrary-precision integer input subject to resources. Resource exhaustion and inconsistent comparators do not produce a guaranteed successful sort.

## 17. Advantages

- Exploits existing monotonic runs, giving linear behavior on one-run inputs.
- Preserves equal-key order through every stage.
- Provides a general O(n log n) worst-case bound while adapting to structure.
- Galloping reduces comparisons over long winning regions.
- Supports generic comparable records without requiring a small integer key range.
- Keeps input preservation explicit through a copy-returning API.

## 18. Disadvantages and Limitations

- More moving parts than a basic merge sort make invariants and tie rules easy to get wrong.
- Requires O(n) memory in this copy-returning, buffered implementation.
- Full forward buffers copy both runs; there is no smaller-run buffer selection, backward `merge_hi`, buffer reuse, or pre-merge trimming optimization.
- Galloping uses a fixed seven-win trigger and returns to scalar merging after each copied block. It does not adapt the trigger or implement a sustained adaptive gallop mode.
- The merge policy and classic minrun rule intentionally differ from current CPython Powersort and later minrun refinements.
- The API has no comparator/key parameter; records must define `<`. Python copying is shallow.
- This is an educational implementation, with no performance or production-equivalence claim relative to CPython or OpenJDK.

These simplifications retain natural runs, computed minrun, stable binary extension, corrected stack management, and actual exponential galloping. A fixed-block bottom-up merge sort alone would not implement these defining behaviors.

## 19. When to Use It

Study or choose this approach when stable ordering matters, inputs may contain long ordered runs, and linear auxiliary storage is acceptable. It is especially informative for understanding how a practical sorter combines several simple techniques with careful global invariants. In application code, prefer the language's mature sorting facilities unless implementing the algorithm itself is the goal.

## 20. When Not to Use It

Use a simpler method for a very small standalone example, a space-conscious heap-based design when memory is tight, or an explicitly external-memory sort for data too large for RAM. An integer-key method may be preferable when a small bounded domain is known. This implementation also does not accept partial orders, arbitrary key callbacks, or an infinite stream.

## 21. Comparison With Related Algorithms

The space column includes the returned copy used by this repository's comparison-sort APIs.

| Method | Best | Worst | Stable? | Additional space | Main distinction |
| --- | --- | --- | --- | --- | --- |
| Tim Sort here | Θ(n) | O(n log n) | Yes | O(n) | Natural runs, binary extension, corrected stack, galloping |
| [Merge sort](../merge-sort/README.md), basic top-down | Θ(n log n) | Θ(n log n) | Yes | O(n) | Fixed recursive partitioning without natural-run discovery |
| [Insertion sort](../insertion-sort/README.md) | Θ(n) | Θ(n²) | Yes | O(n) with returned copy | Simple shifts; adapts to inversion count |
| [Heap sort](../heap-sort/README.md) | Depends on keys | O(n log n) | No | O(n) with returned copy | Constant-workspace heap core; no natural-run adaptation |
| [Quick sort](../quick-sort/README.md) | O(n) with all-equal three-way partition | O(n²) | No | O(n) with returned copy | Partitioning; recursion bounded separately from runtime |

Powersort shares natural-run detection and stable merging but chooses merge order using a different policy. This lesson does not create a separate Powersort catalog implementation or claim optimal merging for every run distribution.

## 22. Interview Questions

1. **Why must descending runs be strict?** Reversing an equal-key pair would reverse its original order before merging could preserve it.
2. **What does binary insertion do on equality?** It places a later item after existing equivalent items by taking the upper bound.
3. **Why are only adjacent runs merged?** Intervening runs may contain equal keys whose original relative order must remain intact.
4. **Why check four pending runs?** Merging near the top can break the preceding triple's inequality while the top triple looks valid.
5. **Do both gallop directions use the same bound?** No: left-run blocks may include ties with the right head; right-run blocks must stop before ties with the left head.
6. **Is a merge logarithmic because it gallops?** Boundary search can be logarithmic in block size, but copying and output writes still take linear work.
7. **Is the run stack a recursive call stack?** No; it is an explicit O(log n) collection of pending intervals in an iterative algorithm.

## 23. Practice Problems

1. Compute minrun for lengths `63`, `64`, `65`, `127`, `128`, `129`, and `2112`. Explain why the last value gives runs closer to a power-of-two count.
2. Trace the 128-item example and identify every collapse decision before looking at the expected merge intervals.
3. Explain why stack lengths `[120, 80, 45, 30]` require another merge even though the top three satisfy their local inequalities.
4. Write a test with equal-key tagged records spanning two runs. Show how an inclusive right gallop would break stability.
5. Instrument comparisons and writes separately on disjoint, overlapping, and alternating runs. Explain when galloping can save comparisons without avoiding output movement.
6. Design a smaller-run buffer merge as a separate exercise. Work out the reversed tie rule needed when writing from the high end before implementing it.

## 24. References

- Tim Peters and CPython contributors, [classic sorting design notes, CPython 3.10](https://raw.githubusercontent.com/python/cpython/3.10/Objects/listsort.txt) — natural runs, minrun, stability, and galloping.
- CPython, [Issue 67703: Bad logic in timsort's merge_collapse](https://github.com/python/cpython/issues/67703) — the correction tracked originally as issue 23515.
- OpenJDK, [TimSort.java](https://github.com/openjdk/jdk/blob/master/src/java.base/share/classes/java/util/TimSort.java) — a primary implementation reference with the corrected deeper-triple check. Its constants and buffer strategies need not match this lesson.
- Nicolas Auger, Vincent Jugé, Cyril Nicaud, and Carine Pivoteau, [On the Worst-Case Complexity of TimSort](https://arxiv.org/abs/1805.08612), 2018 — analysis of classic merge policies.
- CPython, [current sorting design notes](https://github.com/python/cpython/blob/main/Objects/listsort.txt) — explains the newer Powersort strategy and subsequent implementation refinements.

The repository implementations were written for this lesson, with the stated educational simplifications; they do not copy the runtimes' source or promise their exact operation counts.

## 25. Author Attribution

Algorithm Atlas is authored and maintained by [MD.Khalid Hasan](https://github.com/khalidhasan7343). Contributions follow the [project standards](../../../CONTRIBUTING.md), and this lesson uses the repository's [MIT License](../../../LICENSE).

[Sorting category](../README.md) · [Project home](../../../README.md) · [Progress](../../../docs/progress.md)
