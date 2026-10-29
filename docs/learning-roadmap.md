# Learning Roadmap

Progress from foundational problem solving to specialized AI topics. These levels describe a study order, not repository development phases: learning a later level does not authorize implementation outside the approved development phase.

**Current scope:** Phase 15 B3 Ensemble Methods only, following explicit approval of the latest B1 audit and all previous work. Follow [scope](ensemble-methods-scope.md), [contracts](ensemble-methods-conventions.md) and [checkpoints](ensemble-methods-checkpoints.md). New Phase 15 review approval is pending; no later category is authorized.

## Level 1 — DSA Foundations

**Prerequisites:** variables, conditionals, loops, functions, arrays/lists, integer arithmetic, and the ability to run a small Python or C++ program. Become comfortable reading input, checking an output, and explaining what a loop does.

Study basic ordering, lookup, and arithmetic:

- [Bubble Sort](../dsa/sorting/bubble-sort/), [Selection Sort](../dsa/sorting/selection-sort/), and [Insertion Sort](../dsa/sorting/insertion-sort/): compare movement of values, comparisons, stability, and input order.
- [Linear Search](../dsa/searching/linear-search/) and [Binary Search](../dsa/searching/binary-search/): connect the input contract to the available speedup.
- [Euclidean Algorithm](../dsa/number-theory/euclidean-algorithm/): practice reasoning about a decreasing problem size and integer properties.

**Before moving on:** explain the difference between a result and an invariant, trace loops on a small input, and distinguish linear, logarithmic, and quadratic growth. Review the [glossary](glossary.md) and [complexity cheat sheet](complexity-cheatsheet.md).

## Level 2 — Core DSA

**Prerequisites:** Level 1, basic recursion and call stacks, sets/maps, and an introductory understanding of trees and adjacency lists. Learn to state a problem's input, output, and constraints before choosing a technique.

Explore decomposition, search, and reusable state:

- [Merge Sort](../dsa/sorting/merge-sort/) and [Quick Sort](../dsa/sorting/quick-sort/): connect recursion to partitioning, combining, and resource costs.
- [Maximum Subarray using Divide and Conquer](../dsa/divide-and-conquer/maximum-subarray-divide-and-conquer/), [Karatsuba Multiplication](../dsa/divide-and-conquer/karatsuba-multiplication/), [Closest Pair of Points](../dsa/divide-and-conquer/closest-pair-of-points/), and [Strassen's Matrix Multiplication](../dsa/divide-and-conquer/strassen-matrix-multiplication/): derive divide/conquer/combine recurrences and distinguish arithmetic from bit complexity.
- [N-Queens](../dsa/recursion-and-backtracking/n-queens/): study partial solutions, constraints, and undoing choices.
- [Inorder Traversal](../dsa/tree-algorithms/inorder-traversal/) and [Breadth-First Search](../dsa/graph-algorithms/breadth-first-search/): compare traversal order and visited-state tracking.
- [Activity Selection](../dsa/greedy/activity-selection/), [0/1 Knapsack](../dsa/dynamic-programming/zero-one-knapsack/), and [Longest Common Subsequence](../dsa/dynamic-programming/longest-common-subsequence/): distinguish a provable greedy choice from a dynamic-programming state and recurrence.

**Greedy algorithms implemented in Phase 6:** [Activity Selection](../dsa/greedy/activity-selection/), [Fractional Knapsack](../dsa/greedy/fractional-knapsack/), [Huffman Coding](../dsa/greedy/huffman-coding/) and [Job Sequencing with Deadlines](../dsa/greedy/job-sequencing-with-deadlines/). These four Greedy-owned topics received explicit owner approval before Phase 7.

**Graph algorithms that also use the Greedy paradigm:** [Dijkstra](../dsa/graph-algorithms/dijkstra/) fixes a smallest tentative-distance vertex under nonnegative weights; [Prim](../dsa/graph-algorithms/prim/) grows an MST through a cheapest cut edge; [Kruskal](../dsa/graph-algorithms/kruskal/) adds a cheapest cycle-free edge. These conceptual links preserve Graph canonical ownership. Their implementations are now completed under the explicit Phase 7 authorization, with Phase 7 explicitly owner-approved. Phase 6 approval covers its four Greedy-owned implementations. No membership or canonical-topic count changes.

**Before moving on:** justify a base case, detect repeated subproblems, explain why a greedy decision is safe when applicable, and choose relevant boundary tests instead of reusing one test list for every problem.

## Level 3 — Advanced DSA

**Prerequisites:** Level 2, asymptotic analysis, graph traversal, balanced-tree concepts, proof by induction, and basic priority queues. Familiarity with binary representations helps with indexed-tree structures.

Deepen representation and algorithm-selection skills:

- [Fenwick Tree](../dsa/tree-algorithms/fenwick-tree/) and [Red-Black Tree Operations](../dsa/tree-algorithms/red-black-tree-operations/): study supported operations and structural invariants.
- [Dijkstra's Algorithm](../dsa/graph-algorithms/dijkstra/) and [Tarjan's Strongly Connected Components](../dsa/graph-algorithms/tarjan-strongly-connected-components/): distinguish weighted path assumptions from connectivity structure.
- [Knuth-Morris-Pratt](../dsa/string-algorithms/knuth-morris-pratt/): learn how preprocessing can reuse information during matching.

**Before moving on:** derive bounds from a representation, include preprocessing and recursion storage, and explain which assumptions are necessary for correctness. Continue through the remaining advanced trees, graph, string, and optimization topics in the complete index.

## Level 4 — Machine Learning Foundations

**Prerequisites:** Level 1 problem-solving skills, vectors and matrices, elementary probability and statistics, derivatives, and basic numeric programming. Learn training/validation/test separation, suitable evaluation metrics, and leakage prevention before comparing models.

Start with interpretable supervised models and basic clustering:

- [Linear Regression](../machine-learning/supervised-learning/regression/linear-regression/): connect an objective, fitted parameters, and predictions.
- [Logistic Regression](../machine-learning/supervised-learning/classification/logistic-regression/) and [Gaussian Naive Bayes](../machine-learning/supervised-learning/classification/gaussian-naive-bayes/): compare discriminative and generative assumptions and classification evaluation.
- [K-Means](../machine-learning/unsupervised-learning/clustering/k-means/) and [DBSCAN](../machine-learning/unsupervised-learning/clustering/dbscan/): examine how distance, scaling, and density assumptions change cluster structure.

**Before moving on:** use a small reproducible dataset, fit preprocessing on permitted training data only, report an appropriate held-out metric, and explain why an evaluation procedure matches the intended task.

## Level 5 — Advanced Machine Learning

**Prerequisites:** Level 4, overfitting and regularization, cross-validation, feature scaling, eigendecomposition/SVD concepts, and an understanding of why time-series evaluation preserves time order.

Study combinations, representations, and structured data:

- [Random Forest](../machine-learning/ensemble-methods/random-forest/) and [CatBoost](../machine-learning/ensemble-methods/catboost/): compare ensemble construction and model-selection controls.
- [Principal Component Analysis](../machine-learning/unsupervised-learning/dimensionality-reduction/principal-component-analysis/): connect a projection to variance, scaling, and information loss.
- [ARIMA](../machine-learning/time-series/arima/) and [Hidden Markov Models](../machine-learning/time-series/hidden-markov-models/): distinguish observed temporal structure from latent state modeling.
- [TF-IDF](../machine-learning/natural-language-processing/tf-idf/) and [Word2Vec](../machine-learning/natural-language-processing/word2vec/): compare sparse count-derived representations and learned embeddings.

**Before moving on:** explain a method's modeling assumptions, distinguish training from inference cost, and choose evaluation splits for sequential, grouped, or ordinary independent examples as appropriate.

## Level 6 — Deep Learning

**Prerequisites:** Levels 4–5, matrix calculus fundamentals, gradients and the chain rule, numerical optimization, tensor shapes, and the difference between training and inference. Basic convolution and sequence modeling help with later architectures.

Develop from feed-forward computation to structured and generative models:

- [Multilayer Perceptron](../machine-learning/deep-learning/multilayer-perceptron/): reason about layers, activations, loss, and gradient flow.
- [Convolutional Neural Networks](../machine-learning/deep-learning/convolutional-neural-networks/): connect local structure and weight sharing to image-like inputs.
- [Long Short-Term Memory](../machine-learning/deep-learning/long-short-term-memory/): study recurrent state and sequence dependencies.
- [Transformers](../machine-learning/deep-learning/transformers/): track tokens, attention, projections, and architecture-dependent resource use.
- [Generative Adversarial Networks](../machine-learning/deep-learning/generative-adversarial-networks/): understand coupled objectives and training limitations before larger generative families.

**Before moving on:** verify tensor shapes and gradient behavior in a compact experiment, report seeds and resource needs, and distinguish a miniature educational model from a production architecture or pretrained system. Extend to the index's RNN, autoencoder, graph, residual, and diffusion topics afterward.

## Level 7 — Reinforcement Learning and AI Search

**Prerequisites:** Level 2 graph/search concepts, Level 4 probability and evaluation, Markov decision process basics, returns and discounting, and policy/value terminology. Neural RL also needs Level 6. Learn heuristic admissibility and consistency before relying on informed-search guarantees.

Compare explicit planning with learning from interaction:

- [Breadth-First Search](../dsa/graph-algorithms/breadth-first-search/) and [A* Search](../dsa/graph-algorithms/a-star-search/): compare frontier ordering, repeated states, and path-cost assumptions.
- [Q-Learning](../machine-learning/reinforcement-learning/q-learning/) and [Deep Q-Networks](../machine-learning/reinforcement-learning/deep-q-networks/): connect value updates to sampled transitions and function approximation.
- [REINFORCE Policy Gradient](../machine-learning/reinforcement-learning/reinforce-policy-gradient/) and [Proximal Policy Optimization](../machine-learning/reinforcement-learning/proximal-policy-optimization/): study direct policy optimization and the assumptions of an evaluation experiment.

**Before moving on:** define the state, action, reward, termination rule, and evaluation protocol; separate planning guarantees from empirical learning performance. The supplied `Dynamic Policy Optimization (DPO)` label needs maintainer clarification and must not be silently interpreted as another method; see [terminology decisions](terminology-decisions.md).

## Level 8 — Advanced Artificial Intelligence

**Prerequisites:** Levels 2–3 for combinatorial reasoning, Level 7 for search and decisions, basic game theory for strategic agents, and Level 6 for learned vision models. Different branches have different requirements; classical edge detection does not require a neural network course.

Choose branches according to the structure of the problem:

- [Arc Consistency (AC-3)](../artificial-intelligence/constraint-satisfaction/arc-consistency-ac-3/) and [Forward Checking](../artificial-intelligence/constraint-satisfaction/forward-checking/): study domains, constraints, propagation, and search interaction.
- [Minimax](../artificial-intelligence/adversarial-search/minimax/): reason about adversarial objectives and game-tree assumptions before multi-agent extensions.
- [Particle Swarm Optimization](../artificial-intelligence/global-optimization/particle-swarm-optimization/): investigate stochastic optimization behavior and reproducible comparison; swarm-category navigation shares this canonical topic.
- [Mamdani Fuzzy Inference](../artificial-intelligence/fuzzy-logic/mamdani-fuzzy-inference/): distinguish graded membership and rules from probabilities.
- [Canny Edge Detection](../artificial-intelligence/computer-vision/canny-edge-detection/) and [Convolutional Neural Networks](../machine-learning/deep-learning/convolutional-neural-networks/): contrast classical image processing and learned representations before advanced detection families.

**Next study goal:** select a task, justify its representation and assumptions, compare reasonable alternatives, and design a modest reproducible experiment. Use the full index to extend into multi-agent equilibrium computation, ant-colony methods, adversarial variants, fuzzy systems, and object detection.

## How to use the roadmap

Follow the prerequisites rather than treating levels as a fixed schedule. For each available completed topic, read its intuition and contract, predict a small example's output, inspect the implementation, run its documented tests, and explain its complexity in your own words. For unimplemented topics, use the linked planning notes to understand scope and prerequisites; runnable material follows only within an approved category.

Contributors should consult the [development guide](development.md) and [progress tracker](progress.md). Implement only the eight catalog B3 canonicals, pass their internal gates and stop after the verified Phase 15 review package for owner acceptance.


## Graph Algorithms learning sequence

1. Foundations: [BFS](../dsa/graph-algorithms/breadth-first-search/), [DFS](../dsa/graph-algorithms/depth-first-search/), [Union-Find](../dsa/graph-algorithms/union-find/) and [Topological Sorting](../dsa/graph-algorithms/topological-sorting/). Trace queue layers, iterative return frames, partitions and dependency order.
2. Weighted paths: [Dijkstra](../dsa/graph-algorithms/dijkstra/), [Bellman-Ford](../dsa/graph-algorithms/bellman-ford/) and [Floyd-Warshall](../dsa/graph-algorithms/floyd-warshall/). Distinguish nonnegative greedy selection from edge-count and intermediate-vertex DP recurrences. Bellman-Ford/Floyd remain canonical Graph implementations discoverable through Dynamic Programming.
3. Minimum spanning forests: [Kruskal](../dsa/graph-algorithms/kruskal/) and [Prim](../dsa/graph-algorithms/prim/). Prove cut safety and verify connectivity, acyclicity and total cost independently of shortest paths.
4. Structure: [Tarjan SCC](../dsa/graph-algorithms/tarjan-strongly-connected-components/), [Kosaraju SCC](../dsa/graph-algorithms/kosaraju-strongly-connected-components/), [Bridges](../dsa/graph-algorithms/bridges-detection/) and [Articulation Points](../dsa/graph-algorithms/articulation-points/). Compare mutual reachability and deletion effects; retain edge IDs for multigraphs.
5. Advanced routes: [A*](../dsa/graph-algorithms/a-star-search/) and [Johnson](../dsa/graph-algorithms/johnson/). Establish admissibility/reopening and potential reweighting before trusting their results.

All fifteen have Python/C++ implementations and executable independent tests. The owner explicitly approved Phase 7 after its review. The historical Phase 5 and Phase 6 reports remain unchanged; latest approvals and actual Phase 7 commands are in the Graph checkpoint. Phase 8 Tree Algorithms is now explicitly authorized; further categories require separate owner approval.

## Tree learning sequence — Phase 8

Phase 7 is owner-approved. Study these fourteen canonical lessons in the same five validated batches recorded in [Tree checkpoints](tree-algorithms-checkpoints.md); Phase 8 owner review remains pending.

1. Traverse a copied binary arena: [inorder](../dsa/tree-algorithms/inorder-traversal/README.md), [preorder](../dsa/tree-algorithms/preorder-traversal/README.md), [postorder](../dsa/tree-algorithms/postorder-traversal/README.md), then FIFO [level order](../dsa/tree-algorithms/level-order-traversal/README.md). Compare explicit stacks with recursive definitions and retain node identity when values repeat.
2. Query one static rooted tree: [parent-walking LCA](../dsa/tree-algorithms/lowest-common-ancestor/README.md), [Binary Lifting](../dsa/tree-algorithms/binary-lifting/README.md), then the single-entry [Euler Tour](../dsa/tree-algorithms/euler-tour/README.md). Verify ancestor answers and subtree intervals independently.
3. Maintain aggregates with [Fenwick Tree](../dsa/tree-algorithms/fenwick-tree/README.md) and [Segment Tree](../dsa/tree-algorithms/segment-tree/README.md); compare identical assignments against naive sums. Study character-prefix indexing and shared-prefix deletion in [Trie](../dsa/tree-algorithms/trie/README.md).
4. Maintain a balanced binary set with [AVL](../dsa/tree-algorithms/avl-tree-rotations/README.md) and [Red-Black](../dsa/tree-algorithms/red-black-tree-operations/README.md). Inspect heights, colors, ordering and deletion repairs after every mutation.
5. Increase fanout with [B-Tree](../dsa/tree-algorithms/b-tree-operations/README.md) and [B+ Tree](../dsa/tree-algorithms/b-plus-tree-operations/README.md). Distinguish internal records from routing separators; verify occupancy, equal leaf depth and linked-leaf range scans through splitting, borrowing, merging and root contraction.

[Tree conventions](tree-conventions.md) state each API's ownership, numeric bounds and mutation contract. These topics reuse their catalog paths. Do not start another category before explicit owner approval.

## Current Phase 15 authorization

The owner approved the latest B1 audit and all previous work, authorizing only
[B3 Ensemble Methods](ensemble-methods-scope.md). Its eight canonicals retain their
catalog paths. Follow [checkpoints](ensemble-methods-checkpoints.md); new review
approval remains pending. No later ML, Deep Learning or AI category is authorized.
