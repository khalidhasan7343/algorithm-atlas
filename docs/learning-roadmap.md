# Learning Roadmap

Progress from foundational problem solving to specialized AI topics. These levels describe a study order, not repository development phases: learning a later level does not authorize implementation outside the approved development phase.

**Phase 0 status:** algorithm links below lead to canonical planning folders. Implementations, worked examples, and algorithm tests will be added only after the relevant phase is approved. Use the [complete index](algorithm-index.md) for every syllabus item and the [progress tracker](progress.md) for actual completion status. Repeated topics share their canonical location.

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
- [N-Queens](../dsa/recursion-and-backtracking/n-queens/): study partial solutions, constraints, and undoing choices.
- [Inorder Traversal](../dsa/tree-algorithms/inorder-traversal/) and [Breadth-First Search](../dsa/graph-algorithms/breadth-first-search/): compare traversal order and visited-state tracking.
- [Activity Selection](../dsa/greedy/activity-selection/), [0/1 Knapsack](../dsa/dynamic-programming/zero-one-knapsack/), and [Longest Common Subsequence](../dsa/dynamic-programming/longest-common-subsequence/): distinguish a provable greedy choice from a dynamic-programming state and recurrence.

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

Follow the prerequisites rather than treating levels as a fixed schedule. For each available completed topic, read its intuition and contract, predict a small example's output, inspect the implementation, run its documented tests, and explain its complexity in your own words. During Phase 0, use the linked planning notes to understand scope and prerequisites; runnable algorithm material is intentionally deferred.

Contributors should consult the [development guide](development.md) and the current [progress tracker](progress.md). Implementation begins only after the maintainer's explicit phase approval, starting with `Phase 0 Approved. Start Phase 1.`
