# Complexity Cheat Sheet

Complexity describes how resource use grows with an input size under a stated computational model. It does not measure wall-clock speed, memory in bytes, or the quality of an ML model. The tables below are conceptual references for future implementations; they are not benchmark results or claims that these algorithms are already implemented.

## Notation and assumptions

| Notation | Meaning | Example interpretation |
| --- | --- | --- |
| `O(f(n))` | Asymptotic upper bound, up to a constant factor for sufficiently large inputs | `O(n²)` alone does not assert a tight bound. |
| `Ω(f(n))` | Asymptotic lower bound | Any comparison sort has a worst-case lower bound of `Ω(n log n)` in the general comparison model. |
| `Θ(f(n))` | Matching upper and lower bounds | A full scan of `n` items is `Θ(n)` when each visit costs constant time. |
| Best / worst case | Minimum / maximum cost among inputs of a given size | A linear search may stop immediately or inspect every element. |
| Average case | Expected cost under an explicit input distribution | A claimed average must identify the distribution or assumptions. |
| Expected cost | Expectation over a stated random process | Randomized pivot choices can support an expected bound for quicksort. |
| Amortized cost | Cost per operation over a sequence, without requiring random inputs | Resizable-array append can be amortized constant time despite occasional resizing. |

Common growth rates are `1`, `log n`, `n`, `n log n`, `n²`, `2ⁿ`, and `n!`, in increasing order for sufficiently large `n`. Constant factors and crossover points still matter in actual programs. The logarithm base changes only a constant factor for ordinary asymptotic bounds.

Unless specified otherwise, tables assume constant-time comparisons and arithmetic on machine-sized values, random access for arrays, and a RAM-like model. Python's arbitrary-precision integers and operations on long strings or large matrices may violate constant-time arithmetic or comparison assumptions. Copying slices can also change an implementation's cost.

## Searching and sorting reference bounds

Here `n` is the number of elements, `k` is the size of an integer key range, `d` is the number of processed digits, and `b` is the radix size. Space refers to auxiliary storage and includes call-stack requirements where stated; it excludes the input and required output unless the note says otherwise.

| Method and variant | Time | Auxiliary space | Conditions |
| --- | --- | --- | --- |
| Linear search | Best `Θ(1)`, worst `Θ(n)` | `O(1)` | Sequential scan; a miss examines every element. |
| Iterative binary search | Best `Θ(1)`, worst `Θ(log n)` | `O(1)` | Sorted random-access input; finding the ordering first has an additional cost. |
| Early-exit Bubble Sort | Best `Θ(n)`, average/worst `Θ(n²)` | `O(1)` | Best case requires an unchanged-pass check; common average bound assumes random orderings. |
| Selection Sort | `Θ(n²)` comparisons | `O(1)` | Standard full scan for each selected position, regardless of initial order. |
| Insertion Sort | Best `Θ(n)`, average/worst `Θ(n²)` | `O(1)` | Standard in-place array variant; common average bound assumes random orderings. |
| Merge Sort | `Θ(n log n)` | `O(n)` | Standard array merge buffer; recursion stack is `O(log n)` and is dominated by the buffer. |
| Quicksort | Expected `Θ(n log n)`, worst `Θ(n²)` | Expected `O(log n)`, worst `O(n)` stack | In-place partitions with randomized pivots; naive recursion. Recursing into the smaller side can bound stack use differently. |
| Heap Sort | Worst `O(n log n)` | `O(1)` | Standard array heap with iterative sift operations. |
| Counting Sort | `Θ(n + k)` | `O(n + k)` | Standard stable variant with an output buffer; keys lie in a known bounded integer range. |
| LSD Radix Sort | `Θ(d(n + b))` | `O(n + b)` | A stable counting pass per digit; fixed representation and digit extraction assumptions apply. |

Comparison-sort lower bounds do not apply directly to Counting Sort and Radix Sort because those methods exploit additional key structure. Bucket Sort, Shell Sort, Tim Sort, interpolation search, and many variants require more specific assumptions than a single universal row can express. Their eventual READMEs must state the implemented variant and justify its bounds.

## Graphs, trees, and dynamic programming

Here `V` and `E` are vertex and edge counts, `h` is tree height, and `m` and `n` are sequence lengths. Graph space entries exclude the stored input graph. An undirected adjacency list stores each edge in both directions; that constant factor does not change `O(V + E)` storage.

| Method and representation | Time | Auxiliary space / caveat |
| --- | --- | --- |
| BFS or DFS over a full adjacency-list graph | `O(V + E)` | `O(V)` visited state and frontier/stack; a traversal from one source may visit only its reachable component. |
| BFS or DFS with an adjacency matrix | `O(V²)` for full traversal | `O(V)` traversal state, in addition to the `Θ(V²)` input representation. |
| Dijkstra with binary heap and decrease-key | `O((V + E) log V)` | `O(V)` heap and state; nonnegative edge weights. A lazy duplicate-entry heap may use `O(V + E)` state and `log E` heap factors. |
| Bellman–Ford | `O(VE)` worst case | `O(V)` distances and predecessors; detects reachable negative cycles with an extra pass. |
| Floyd–Warshall | `Θ(V³)` | `Θ(V²)` distance table; whether it is auxiliary depends on in-place reuse and the input/output contract. |
| Kruskal with sorted edges and Union-Find | `O(E log E)` for sorting plus near-linear Union-Find work | `O(V)` Union-Find state, plus the chosen sorting and edge storage. |
| Balanced binary search tree operation | `O(log n)` | Balance guarantees are required; an unbalanced tree may have height `Θ(n)`. |
| Tree traversal | `Θ(n)` | DFS stack `O(h)`; level-order queue `O(w)` where `w` is maximum frontier width. |
| Fenwick Tree update or prefix query | `O(log n)` | Tree storage `O(n)`; linear-time construction is possible but depends on the method. |
| Segment Tree point update or range query | `O(log n)` | `O(n)` tree storage for the usual balanced array representation. |
| LCS with a full DP table | `Θ(mn)` | `Θ(mn)` table; length-only rolling rows reduce storage to `O(min(m,n))`. |
| 0/1 Knapsack capacity DP | `Θ(nW)` | `O(W)` with the appropriate one-dimensional update order; `W` is integer capacity. |

The Knapsack bound is **pseudo-polynomial**: `W` is a numeric value, while its binary representation uses only `Θ(log W)` bits. Polynomial in a numeric value need not be polynomial in input bit length. Also distinguish an algorithm's auxiliary space from storage for all reported paths, subsets, or permutations: output size itself can be exponential or factorial.

## AI search and model-dependent analysis

For tree-search analyses, define branching factor `b`, solution depth `d`, maximum search depth `m`, and repeated-state handling. A full breadth-first exploration to depth `d` has `Θ(1 + b + … + bᵈ)` nodes when every node has `b` children; for fixed `b > 1`, this is `Θ(bᵈ)`. A graph-search implementation with visited-state storage needs a separate analysis based on the reachable state graph. Heuristic strength, admissibility, consistency, and duplicate handling affect informed search behavior and guarantees.

Machine learning has no universal training or prediction complexity. Define the dataset size `N`, feature count `D`, epochs `T`, batch size `B`, parameter count `P`, sequence length `L`, hidden width, layer count, optimizer, and data representation as needed. Separate preprocessing, fitting, inference, and model storage.

| Concrete computation | Reference cost and assumptions |
| --- | --- |
| Dense linear-model full-batch gradient step | `Θ(ND)` for a single output and direct dense matrix-vector products; `T` such steps cost `Θ(TND)`. This is not the cost of every regression solver. |
| Brute-force KNN query | `Θ(ND)` for distance calculation, plus the chosen neighbor-selection cost; stored dense training data uses `Θ(ND)` space. Index structures change the analysis. |
| Lloyd K-Means iterations | `O(TNKD)` for `K` clusters with direct dense assignment and update calculations; initialization, convergence, and alternative distance routines need separate treatment. |
| One dense layer for a batch | `Θ(B D_in D_out)` multiply-add work; parameter storage `Θ(D_in D_out)` plus biases. Training also stores activations and optimizer state. |
| Standard dense self-attention core | `Θ(B L² D)` score/value work and `Θ(B L²)` attention-score storage for aggregate width `D`; projections add `Θ(B L D²)` when widths are `D`. This excludes feed-forward layers and depends on the attention implementation. |

Do not transfer one row's bound to an entire family such as SVMs, Transformers, GNNs, diffusion models, or neural networks. Architecture, solver, sparsity, number of training steps, and implementation choices change their resource use. Any measured runtime or memory claim must state the workload and environment.

## Checklist for each future algorithm

Define all variables and the exact variant; identify the counted operation and representation; derive time from the work done; account for memory, recursion and output; state distribution or randomization assumptions; separate preprocessing from queries or training from inference; and explain which input conditions attain each meaningful case. Use the [development guide](development.md) for the full documentation requirements.
