# Glossary

These terms support the [learning roadmap](learning-roadmap.md), [algorithm index](algorithm-index.md), and future implementation READMEs. Definitions describe concepts, not a claim that the repository already implements them.

## Algorithms and analysis

| Term | Meaning |
| --- | --- |
| Algorithm | A precisely described procedure for solving a computational task under stated assumptions. |
| Input contract | The accepted values, types, preconditions, and error behavior of an operation. For example, binary search needs an ordered search space. |
| Correctness | The property that an algorithm meets its specified result for every permitted input. Examples and tests supply evidence but do not by themselves prove correctness for all inputs. |
| Invariant | A property maintained across loop iterations or state transitions, used to explain why progress leads to a correct result. |
| Termination | The guarantee that execution eventually stops under the input contract; often justified by a decreasing finite measure. |
| Time complexity | A growth-rate description of computational work as a function of explicitly defined input parameters. |
| Auxiliary space | Additional working storage beyond the input and, depending on the stated convention, required output. Count recursion stacks explicitly. |
| Big-O, Big-Ω, Big-Θ | Asymptotic upper, lower, and tight bounds respectively; see the [complexity cheat sheet](complexity-cheatsheet.md). |
| Amortized analysis | Analysis of the total cost of a sequence of operations to obtain a per-operation bound; it does not assume random inputs. |
| Pseudo-polynomial | Polynomial in the numeric value of an input parameter, but potentially exponential in that value's encoded bit length. |
| Stable sort | A sort that preserves the relative input order of elements with equal keys. Stability depends on the concrete implementation. |
| In-place | Uses a limited amount of additional storage under an explicitly stated convention; some definitions permit a recursion stack. |
| Recursion | Solving a task by invoking the same procedure on smaller or simpler subproblems, with base cases that stop expansion. |
| Backtracking | Exploring a partial solution and undoing choices when a branch fails or after its alternatives have been considered. |
| Divide and conquer | Splitting a problem into subproblems, solving them, and combining their results. |
| Greedy choice | A locally preferred decision made according to a rule; global correctness needs justification for the particular problem. |
| Dynamic programming (DP) | Reusing results of recurring subproblems through a defined state, transition, base cases, and evaluation order. |
| Memoization / tabulation | Caching results on demand / filling a DP structure in a dependency-respecting order. |
| Pruning | Skipping a search branch when a justified condition shows it is unnecessary for the required result. |
| Canonical location | The single repository folder that owns a topic's documentation, implementations, and tests; other categories link to it. |

## Data structures and graphs

| Term | Meaning |
| --- | --- |
| Array | An indexed sequence; access and resizing costs depend on the concrete representation and language. |
| Stack / queue / deque | Collections supporting last-in-first-out / first-in-first-out / efficient operations at both ends respectively. |
| Heap | A structure maintaining an ordering relationship between parents and children, commonly used to implement a priority queue. It is distinct from the general memory-allocation heap. |
| Hash table | A structure mapping keys to storage locations through a hash function and collision handling; performance depends on those choices and load. |
| Tree | A connected acyclic undirected graph; a rooted tree also gives each non-root node a parent. |
| Balanced search tree | A search tree that maintains structural restrictions keeping its height logarithmic in the number of stored elements. |
| Trie | A tree indexed by successive parts of keys, often characters, supporting prefix-based operations. |
| Graph | A collection of vertices and edges, which may be directed, weighted, or both. |
| Adjacency list / matrix | Graph representations storing neighbors per vertex / a table indexed by vertex pairs. Representation changes memory and traversal costs. |
| Path / cycle | A sequence of connected vertices / a closed path, with precise repetition rules determined by context. |
| Reachability | Whether a path exists from one vertex to another, respecting edge directions. |
| Connected component | A maximal connected part of an undirected graph; directed graphs require distinctions such as strong connectivity. |
| Strongly connected component (SCC) | A maximal directed subgraph in which every vertex can reach every other vertex. |
| Directed acyclic graph (DAG) | A directed graph with no directed cycles. |
| Topological order | A vertex order in which every directed edge goes from an earlier vertex to a later one; exists exactly for finite DAGs. |
| Minimum spanning tree (MST) | A minimum-total-weight tree connecting all vertices in a connected weighted undirected graph. A disconnected graph instead has a spanning forest. |
| Shortest path | A path minimizing a specified cost, subject to graph and edge-weight assumptions. Reachable negative cycles can make some shortest costs undefined. |
| Disjoint Set Union (DSU) | A structure maintaining a partition into sets with representative lookup and set merging; also called Union-Find. |

## Machine learning

| Term | Meaning |
| --- | --- |
| Feature / target | An input representation / the quantity a supervised model aims to predict. |
| Parameter / hyperparameter | A value fitted from data / a configuration choice such as regularization strength or learning rate. |
| Training, validation, test split | Data roles for fitting, choosing models or settings, and evaluating a chosen approach on held-out data. Respect grouping and time order where relevant. |
| Data leakage | Information that would not be available at prediction time entering training or model selection, making evaluation overly optimistic. |
| Supervised learning | Learning from examples paired with target values or labels. Regression predicts quantities; classification predicts categories or their scores/probabilities. |
| Unsupervised learning | Finding structure in data without supervised target labels, such as clusters or a lower-dimensional representation. |
| Loss / metric | The objective optimized during fitting / a measure used to evaluate behavior. They may differ. |
| Gradient | The vector of partial derivatives of a scalar objective with respect to its parameters. |
| Learning rate | A step-size setting used by many iterative optimization methods. |
| Batch / epoch | A subset processed in one training step / one pass through a finite training dataset, under the stated sampling convention. |
| Regularization | A constraint, penalty, or other mechanism intended to control model behavior and improve generalization. |
| Overfitting / underfitting | Fitting incidental training details with poor generalization / failing to capture relevant structure under the chosen evaluation setting. |
| Generalization | Performance on relevant unseen data drawn from the intended setting. |
| Bias-variance tradeoff | A framework for discussing systematic error and sensitivity to training samples; its exact decomposition depends on the loss and assumptions. |
| Normalization / standardization | Rescaling data under a defined rule / commonly centering by a training mean and scaling by a training standard deviation. Fit preprocessing only on permitted training data. |
| Cross-validation | Evaluating a model-selection procedure across multiple training and validation partitions; the partition strategy must fit the data structure. |
| Ensemble | A combination of several models; bagging, boosting, stacking, and voting use different training or aggregation mechanisms. |
| Embedding | A learned or constructed vector representation of an object such as a word, token, node, or image. |
| Backpropagation | Efficient application of the chain rule through a computational graph to compute gradients. |
| Attention | A mechanism for combining representations using context-dependent weights. A specific attention design determines its computational cost. |
| Inference | Using a fitted model to produce outputs; in probabilistic contexts, it can also mean reasoning about latent variables or distributions. |
| Reproducibility | Providing code, data assumptions, seeds, dependencies, and instructions sufficient to repeat a stated experiment within documented limitations. |

## AI, search, and reinforcement learning

| Term | Meaning |
| --- | --- |
| State / action / transition | A problem configuration / an available choice / the rule or distribution describing its resulting state. |
| State space | The configurations relevant to a search or decision problem, together with their transitions. |
| Frontier | Discovered search nodes awaiting expansion; ordering the frontier distinguishes many search methods. |
| Branching factor | The number of successors per state or a stated bound/average on it; define which interpretation is used. |
| Heuristic | An estimate used to guide search or optimization. A heuristic may have useful guarantees only under additional properties. |
| Admissible heuristic | A shortest-path cost estimate that never overestimates the true remaining cost under the problem's cost convention. |
| Consistent heuristic | An estimate satisfying the edge-wise triangle inequality with step costs; it supports useful graph-search properties under appropriate assumptions. |
| Complete / optimal search | Guaranteed to find a solution when one exists / guaranteed to return a best solution, under stated conditions. |
| Constraint satisfaction problem (CSP) | Variables, their domains, and constraints that must be satisfied jointly. |
| Arc consistency | A condition in which each value of a variable has supporting values in a neighboring variable's domain for the relevant binary constraint. |
| Adversarial search | Planning in a setting where another agent's choices affect the outcome, often represented by a game tree. |
| Nash equilibrium | A strategy profile where no player can improve its payoff by changing only its own strategy. It need not maximize collective benefit. |
| Fuzzy membership | A degree of membership in a fuzzy set, commonly in `[0, 1]`; it is not automatically a probability. |
| Swarm intelligence | Methods inspired by distributed interactions among simple agents, such as particle or ant-based optimization. |
| Policy | A rule or distribution selecting actions given the information available to an agent. |
| Reward / return | Immediate feedback / a defined accumulation of rewards, often discounted over time. |
| Value / action-value function | Expected return from a state / from a state-action pair under specified policy and environment assumptions. |
| Exploration / exploitation | Gathering information through actions / selecting actions using currently estimated benefits. |
| On-policy / off-policy | Learning about the policy generating the data / learning about a different target policy. |
| Model-based / model-free RL | Learning or using environment transition/reward dynamics for decisions / learning without an explicit dynamics model in the stated method. |
| DPO ambiguity | The supplied syllabus names **Dynamic Policy Optimization**. Its intended reference is unresolved; do not assume it means the separately named Direct Preference Optimization. |

## Repository evidence and status

A **planned** topic has not begun implementation. **In-progress** marks unfinished work. **Implemented** means the corresponding artifact exists with the stated behavior. **Tested** requires genuine passing checks. **Reviewed** requires an actual review. **Blocked** records a specific obstacle and the resolution needed. These statuses apply to separate documentation, language, and test fields in the [catalog](../catalog.yaml); a folder's existence alone proves none of those deliverables complete.

An **approval checkpoint** is the maintainer review required between development phases. Phase 0 ends before algorithm implementation, and Phase 1 starts only after the explicit instruction `Phase 0 Approved. Start Phase 1.` See the [development guide](development.md) for the complete workflow.
