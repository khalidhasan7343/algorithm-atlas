# Algorithm Atlas — Phase 0 External Review Report

Prepared on **2026-10-20 (Asia/Dhaka)** for **MD.Khalid Hasan**. This package contains the completed Phase 0 foundation only. **No Phase 1 algorithms have been implemented, and no changes have been committed, pushed, or published.**

Archive: `algorithm-atlas-phase-0.zip`

Extracted top-level folder: `algorithm-atlas/`

Included regular files: **312** (311 original foundation files plus this report).

## 1. Completed tasks

- Inspected and preserved the existing initialized local Git repository; no reinitialization or Git identity changes were needed.
- Created the complete DSA, machine-learning, and artificial-intelligence directory structure, including 35 syllabus categories and 235 canonical topic folders.
- Cataloged all 256 original syllabus occurrences, preserved exact category labels and order, documented canonical reuse, and retained meaningful variants separately.
- Created a professional root [README](../../../README.md) with all 21 required sections, the project identity, author attribution, setup instructions, navigation, testing guidance, and progress links.
- Added the [MIT License](../../../LICENSE), copyright **2026 MD.Khalid Hasan**, [contribution guide](../../../CONTRIBUTING.md), [Code of Conduct](../../../CODE_OF_CONDUCT.md), [security policy](../../../SECURITY.md), and persistent [phase instructions](../../../AGENTS.md).
- Added the complete index, eight-level learning roadmap, glossary, complexity reference, setup/development guides, progress tracker, terminology decisions, and foundation review materials under `docs/`.
- Defined the full 25-section future algorithm README standard, Python/C++ implementation expectations, reproducibility requirements, and honest status rules.
- Configured pytest, future per-algorithm test discovery, shared C++17/C++20 compiler fixtures, lightweight dependency requirements, and 79 infrastructure/regression checks.
- Added catalog/schema/artifact/status/link validation, an independent syllabus baseline, and a UTF-8 documentation generator with preservation safeguards and non-mutating check mode.
- Configured lightweight GitHub Actions, issue forms, a pull request template, and development/ignore settings.
- Prepared this report and a portable ZIP that preserves hidden project configuration and the complete included directory structure.

The canonical topic READMEs are explicitly labeled planning records. They describe purpose, scope, memberships, related topics, statuses, and completion requirements. They do not claim completed algorithm lessons, implementations, tests, or runnable examples. Empty implementation placeholders were not created. The C++ source under `tests/fixtures/` is a standard-library toolchain smoke check, not a syllabus algorithm.

## 2. Full directory tree

The following is the **complete archive tree**, including every included file and hidden project configuration. `.git`, `.venv`, caches, generated outputs, credentials, and the ZIP itself are excluded. Directories are reconstructed from the included files and preserved explicitly in the archive.

```text
algorithm-atlas/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── algorithm_proposal.yml
│   │   ├── bug_report.yml
│   │   ├── config.yml
│   │   └── documentation.yml
│   ├── workflows/
│   │   └── ci.yml
│   └── pull_request_template.md
├── artificial-intelligence/
│   ├── adversarial-search/
│   │   ├── alpha-beta-pruning/
│   │   │   └── README.md
│   │   ├── expectimax/
│   │   │   └── README.md
│   │   ├── minimax/
│   │   │   └── README.md
│   │   └── README.md
│   ├── computer-vision/
│   │   ├── canny-edge-detection/
│   │   │   └── README.md
│   │   ├── r-cnn-object-detection/
│   │   │   └── README.md
│   │   ├── sift/
│   │   │   └── README.md
│   │   ├── sobel-edge-detection/
│   │   │   └── README.md
│   │   ├── surf/
│   │   │   └── README.md
│   │   ├── viola-jones-face-detection/
│   │   │   └── README.md
│   │   ├── yolo-object-detection/
│   │   │   └── README.md
│   │   └── README.md
│   ├── constraint-satisfaction/
│   │   ├── arc-consistency-ac-3/
│   │   │   └── README.md
│   │   ├── backtracking-search/
│   │   │   └── README.md
│   │   ├── constraint-propagation/
│   │   │   └── README.md
│   │   ├── forward-checking/
│   │   │   └── README.md
│   │   ├── min-conflicts/
│   │   │   └── README.md
│   │   └── README.md
│   ├── fuzzy-logic/
│   │   ├── mamdani-fuzzy-inference/
│   │   │   └── README.md
│   │   ├── sugeno-fuzzy-inference/
│   │   │   └── README.md
│   │   └── README.md
│   ├── global-optimization/
│   │   ├── ant-colony-optimization/
│   │   │   └── README.md
│   │   ├── branch-and-bound/
│   │   │   └── README.md
│   │   ├── exhaustive-search/
│   │   │   └── README.md
│   │   ├── particle-swarm-optimization/
│   │   │   └── README.md
│   │   └── README.md
│   ├── informed-search/
│   │   ├── beam-search/
│   │   │   └── README.md
│   │   ├── greedy-best-first-search/
│   │   │   └── README.md
│   │   ├── iterative-deepening-a-star/
│   │   │   └── README.md
│   │   ├── recursive-best-first-search/
│   │   │   └── README.md
│   │   ├── simplified-memory-bounded-a-star/
│   │   │   └── README.md
│   │   └── README.md
│   ├── local-search/
│   │   ├── local-beam-search/
│   │   │   └── README.md
│   │   ├── random-restart-hill-climbing/
│   │   │   └── README.md
│   │   ├── simple-hill-climbing/
│   │   │   └── README.md
│   │   ├── steepest-ascent-hill-climbing/
│   │   │   └── README.md
│   │   ├── stochastic-hill-climbing/
│   │   │   └── README.md
│   │   ├── tabu-search/
│   │   │   └── README.md
│   │   └── README.md
│   ├── multi-agent-systems/
│   │   ├── auction-algorithms/
│   │   │   └── README.md
│   │   ├── nash-equilibrium-computation/
│   │   │   └── README.md
│   │   └── README.md
│   ├── swarm-intelligence/
│   │   └── README.md
│   ├── uninformed-search/
│   │   ├── bidirectional-search/
│   │   │   └── README.md
│   │   ├── depth-limited-search/
│   │   │   └── README.md
│   │   ├── iterative-deepening-dfs/
│   │   │   └── README.md
│   │   ├── uniform-cost-search/
│   │   │   └── README.md
│   │   └── README.md
│   └── README.md
├── docs/
│   ├── algorithm-index.md
│   ├── complexity-cheatsheet.md
│   ├── development.md
│   ├── getting-started.md
│   ├── glossary.md
│   ├── learning-roadmap.md
│   ├── phase-0-files.md
│   ├── phase-0-review.md
│   ├── progress.md
│   └── terminology-decisions.md
├── dsa/
│   ├── bit-manipulation/
│   │   ├── brian-kernighan-set-bit-counting/
│   │   │   └── README.md
│   │   ├── subset-generation-bitmasking/
│   │   │   └── README.md
│   │   ├── two-non-repeating-elements/
│   │   │   └── README.md
│   │   ├── xor-unique-elements/
│   │   │   └── README.md
│   │   └── README.md
│   ├── divide-and-conquer/
│   │   ├── closest-pair-of-points/
│   │   │   └── README.md
│   │   ├── karatsuba-multiplication/
│   │   │   └── README.md
│   │   ├── maximum-subarray-divide-and-conquer/
│   │   │   └── README.md
│   │   ├── strassen-matrix-multiplication/
│   │   │   └── README.md
│   │   └── README.md
│   ├── dynamic-programming/
│   │   ├── coin-change/
│   │   │   └── README.md
│   │   ├── edit-distance/
│   │   │   └── README.md
│   │   ├── fibonacci/
│   │   │   └── README.md
│   │   ├── kadane/
│   │   │   └── README.md
│   │   ├── longest-common-subsequence/
│   │   │   └── README.md
│   │   ├── longest-increasing-subsequence/
│   │   │   └── README.md
│   │   ├── matrix-chain-multiplication/
│   │   │   └── README.md
│   │   ├── palindrome-partitioning/
│   │   │   └── README.md
│   │   ├── rod-cutting/
│   │   │   └── README.md
│   │   ├── subset-sum/
│   │   │   └── README.md
│   │   ├── zero-one-knapsack/
│   │   │   └── README.md
│   │   └── README.md
│   ├── graph-algorithms/
│   │   ├── a-star-search/
│   │   │   └── README.md
│   │   ├── articulation-points/
│   │   │   └── README.md
│   │   ├── bellman-ford/
│   │   │   └── README.md
│   │   ├── breadth-first-search/
│   │   │   └── README.md
│   │   ├── bridges-detection/
│   │   │   └── README.md
│   │   ├── depth-first-search/
│   │   │   └── README.md
│   │   ├── dijkstra/
│   │   │   └── README.md
│   │   ├── floyd-warshall/
│   │   │   └── README.md
│   │   ├── johnson/
│   │   │   └── README.md
│   │   ├── kosaraju-strongly-connected-components/
│   │   │   └── README.md
│   │   ├── kruskal/
│   │   │   └── README.md
│   │   ├── prim/
│   │   │   └── README.md
│   │   ├── tarjan-strongly-connected-components/
│   │   │   └── README.md
│   │   ├── topological-sorting/
│   │   │   └── README.md
│   │   ├── union-find/
│   │   │   └── README.md
│   │   └── README.md
│   ├── greedy/
│   │   ├── activity-selection/
│   │   │   └── README.md
│   │   ├── fractional-knapsack/
│   │   │   └── README.md
│   │   ├── huffman-coding/
│   │   │   └── README.md
│   │   ├── job-sequencing-with-deadlines/
│   │   │   └── README.md
│   │   └── README.md
│   ├── number-theory/
│   │   ├── euclidean-algorithm/
│   │   │   └── README.md
│   │   ├── extended-euclidean-algorithm/
│   │   │   └── README.md
│   │   ├── fast-exponentiation/
│   │   │   └── README.md
│   │   ├── least-common-multiple/
│   │   │   └── README.md
│   │   ├── modular-exponentiation/
│   │   │   └── README.md
│   │   ├── prime-factorization/
│   │   │   └── README.md
│   │   ├── sieve-of-eratosthenes/
│   │   │   └── README.md
│   │   └── README.md
│   ├── recursion-and-backtracking/
│   │   ├── combinations/
│   │   │   └── README.md
│   │   ├── graph-coloring/
│   │   │   └── README.md
│   │   ├── hamiltonian-path/
│   │   │   └── README.md
│   │   ├── n-queens/
│   │   │   └── README.md
│   │   ├── permutations/
│   │   │   └── README.md
│   │   ├── power-set-generation/
│   │   │   └── README.md
│   │   ├── rat-in-a-maze/
│   │   │   └── README.md
│   │   ├── subset-sum-backtracking/
│   │   │   └── README.md
│   │   ├── sudoku-solver/
│   │   │   └── README.md
│   │   └── README.md
│   ├── searching/
│   │   ├── binary-search/
│   │   │   └── README.md
│   │   ├── exponential-search/
│   │   │   └── README.md
│   │   ├── interpolation-search/
│   │   │   └── README.md
│   │   ├── jump-search/
│   │   │   └── README.md
│   │   ├── linear-search/
│   │   │   └── README.md
│   │   ├── ternary-search/
│   │   │   └── README.md
│   │   └── README.md
│   ├── sorting/
│   │   ├── bubble-sort/
│   │   │   └── README.md
│   │   ├── bucket-sort/
│   │   │   └── README.md
│   │   ├── counting-sort/
│   │   │   └── README.md
│   │   ├── heap-sort/
│   │   │   └── README.md
│   │   ├── insertion-sort/
│   │   │   └── README.md
│   │   ├── merge-sort/
│   │   │   └── README.md
│   │   ├── quick-sort/
│   │   │   └── README.md
│   │   ├── radix-sort/
│   │   │   └── README.md
│   │   ├── selection-sort/
│   │   │   └── README.md
│   │   ├── shell-sort/
│   │   │   └── README.md
│   │   ├── tim-sort/
│   │   │   └── README.md
│   │   └── README.md
│   ├── string-algorithms/
│   │   ├── aho-corasick/
│   │   │   └── README.md
│   │   ├── boyer-moore/
│   │   │   └── README.md
│   │   ├── knuth-morris-pratt/
│   │   │   └── README.md
│   │   ├── manacher/
│   │   │   └── README.md
│   │   ├── naive-pattern-matching/
│   │   │   └── README.md
│   │   ├── rabin-karp/
│   │   │   └── README.md
│   │   ├── suffix-array/
│   │   │   └── README.md
│   │   ├── suffix-tree/
│   │   │   └── README.md
│   │   ├── z-algorithm/
│   │   │   └── README.md
│   │   └── README.md
│   ├── tree-algorithms/
│   │   ├── avl-tree-rotations/
│   │   │   └── README.md
│   │   ├── b-plus-tree-operations/
│   │   │   └── README.md
│   │   ├── b-tree-operations/
│   │   │   └── README.md
│   │   ├── binary-lifting/
│   │   │   └── README.md
│   │   ├── euler-tour/
│   │   │   └── README.md
│   │   ├── fenwick-tree/
│   │   │   └── README.md
│   │   ├── inorder-traversal/
│   │   │   └── README.md
│   │   ├── level-order-traversal/
│   │   │   └── README.md
│   │   ├── lowest-common-ancestor/
│   │   │   └── README.md
│   │   ├── postorder-traversal/
│   │   │   └── README.md
│   │   ├── preorder-traversal/
│   │   │   └── README.md
│   │   ├── red-black-tree-operations/
│   │   │   └── README.md
│   │   ├── segment-tree/
│   │   │   └── README.md
│   │   ├── trie/
│   │   │   └── README.md
│   │   └── README.md
│   ├── two-pointers-and-sliding-window/
│   │   ├── longest-substring-without-repeating-characters/
│   │   │   └── README.md
│   │   ├── sliding-window-maximum/
│   │   │   └── README.md
│   │   ├── two-sum-sorted-array/
│   │   │   └── README.md
│   │   └── README.md
│   └── README.md
├── machine-learning/
│   ├── anomaly-detection/
│   │   ├── isolation-forest/
│   │   │   └── README.md
│   │   ├── local-outlier-factor/
│   │   │   └── README.md
│   │   ├── one-class-svm/
│   │   │   └── README.md
│   │   └── README.md
│   ├── deep-learning/
│   │   ├── convolutional-neural-networks/
│   │   │   └── README.md
│   │   ├── denoising-autoencoders/
│   │   │   └── README.md
│   │   ├── diffusion-models/
│   │   │   └── README.md
│   │   ├── gated-recurrent-units/
│   │   │   └── README.md
│   │   ├── generative-adversarial-networks/
│   │   │   └── README.md
│   │   ├── graph-neural-networks/
│   │   │   └── README.md
│   │   ├── long-short-term-memory/
│   │   │   └── README.md
│   │   ├── multilayer-perceptron/
│   │   │   └── README.md
│   │   ├── recurrent-neural-networks/
│   │   │   └── README.md
│   │   ├── residual-networks/
│   │   │   └── README.md
│   │   ├── sparse-autoencoders/
│   │   │   └── README.md
│   │   ├── transformers/
│   │   │   └── README.md
│   │   ├── vanilla-autoencoders/
│   │   │   └── README.md
│   │   ├── variational-autoencoders/
│   │   │   └── README.md
│   │   └── README.md
│   ├── ensemble-methods/
│   │   ├── adaboost/
│   │   │   └── README.md
│   │   ├── bagging/
│   │   │   └── README.md
│   │   ├── catboost/
│   │   │   └── README.md
│   │   ├── gradient-boosting-machine/
│   │   │   └── README.md
│   │   ├── random-forest/
│   │   │   └── README.md
│   │   ├── stacking/
│   │   │   └── README.md
│   │   ├── voting-classifiers/
│   │   │   └── README.md
│   │   ├── xgboost/
│   │   │   └── README.md
│   │   └── README.md
│   ├── graph-learning/
│   │   ├── graph-convolutional-networks/
│   │   │   └── README.md
│   │   ├── node2vec/
│   │   │   └── README.md
│   │   ├── pagerank/
│   │   │   └── README.md
│   │   └── README.md
│   ├── natural-language-processing/
│   │   ├── bag-of-words/
│   │   │   └── README.md
│   │   ├── bert/
│   │   │   └── README.md
│   │   ├── conditional-random-fields/
│   │   │   └── README.md
│   │   ├── cyk-parsing/
│   │   │   └── README.md
│   │   ├── glove/
│   │   │   └── README.md
│   │   ├── gpt/
│   │   │   └── README.md
│   │   ├── hidden-markov-models-pos-tagging/
│   │   │   └── README.md
│   │   ├── n-gram-language-models/
│   │   │   └── README.md
│   │   ├── named-entity-recognition/
│   │   │   └── README.md
│   │   ├── tf-idf/
│   │   │   └── README.md
│   │   ├── word2vec/
│   │   │   └── README.md
│   │   └── README.md
│   ├── optimization/
│   │   ├── adam/
│   │   │   └── README.md
│   │   ├── adamw/
│   │   │   └── README.md
│   │   ├── batch-gradient-descent/
│   │   │   └── README.md
│   │   ├── genetic-algorithms/
│   │   │   └── README.md
│   │   ├── l-bfgs/
│   │   │   └── README.md
│   │   ├── mini-batch-gradient-descent/
│   │   │   └── README.md
│   │   ├── momentum/
│   │   │   └── README.md
│   │   ├── rmsprop/
│   │   │   └── README.md
│   │   ├── simulated-annealing/
│   │   │   └── README.md
│   │   ├── stochastic-gradient-descent/
│   │   │   └── README.md
│   │   └── README.md
│   ├── reinforcement-learning/
│   │   ├── advantage-actor-critic/
│   │   │   └── README.md
│   │   ├── asynchronous-advantage-actor-critic/
│   │   │   └── README.md
│   │   ├── deep-deterministic-policy-gradient/
│   │   │   └── README.md
│   │   ├── deep-q-networks/
│   │   │   └── README.md
│   │   ├── dynamic-policy-optimization/
│   │   │   └── README.md
│   │   ├── monte-carlo-tree-search/
│   │   │   └── README.md
│   │   ├── proximal-policy-optimization/
│   │   │   └── README.md
│   │   ├── q-learning/
│   │   │   └── README.md
│   │   ├── reinforce-policy-gradient/
│   │   │   └── README.md
│   │   ├── sarsa/
│   │   │   └── README.md
│   │   └── README.md
│   ├── supervised-learning/
│   │   ├── classification/
│   │   │   ├── bernoulli-naive-bayes/
│   │   │   │   └── README.md
│   │   │   ├── c4-5-decision-trees/
│   │   │   │   └── README.md
│   │   │   ├── cart-decision-trees/
│   │   │   │   └── README.md
│   │   │   ├── gaussian-naive-bayes/
│   │   │   │   └── README.md
│   │   │   ├── id3-decision-trees/
│   │   │   │   └── README.md
│   │   │   ├── k-nearest-neighbors/
│   │   │   │   └── README.md
│   │   │   ├── linear-discriminant-analysis/
│   │   │   │   └── README.md
│   │   │   ├── logistic-regression/
│   │   │   │   └── README.md
│   │   │   ├── multinomial-naive-bayes/
│   │   │   │   └── README.md
│   │   │   ├── quadratic-discriminant-analysis/
│   │   │   │   └── README.md
│   │   │   ├── support-vector-machines/
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   ├── regression/
│   │   │   ├── decision-tree-regression/
│   │   │   │   └── README.md
│   │   │   ├── elastic-net/
│   │   │   │   └── README.md
│   │   │   ├── lasso-regression/
│   │   │   │   └── README.md
│   │   │   ├── linear-regression/
│   │   │   │   └── README.md
│   │   │   ├── polynomial-regression/
│   │   │   │   └── README.md
│   │   │   ├── ridge-regression/
│   │   │   │   └── README.md
│   │   │   ├── support-vector-regression/
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   └── README.md
│   ├── time-series/
│   │   ├── arima/
│   │   │   └── README.md
│   │   ├── exponential-smoothing/
│   │   │   └── README.md
│   │   ├── hidden-markov-models/
│   │   │   └── README.md
│   │   ├── holt-winters/
│   │   │   └── README.md
│   │   ├── prophet/
│   │   │   └── README.md
│   │   ├── sarima/
│   │   │   └── README.md
│   │   └── README.md
│   ├── unsupervised-learning/
│   │   ├── association-rule-learning/
│   │   │   ├── apriori/
│   │   │   │   └── README.md
│   │   │   ├── eclat/
│   │   │   │   └── README.md
│   │   │   ├── fp-growth/
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   ├── clustering/
│   │   │   ├── agglomerative-hierarchical-clustering/
│   │   │   │   └── README.md
│   │   │   ├── dbscan/
│   │   │   │   └── README.md
│   │   │   ├── divisive-hierarchical-clustering/
│   │   │   │   └── README.md
│   │   │   ├── gaussian-mixture-models/
│   │   │   │   └── README.md
│   │   │   ├── hdbscan/
│   │   │   │   └── README.md
│   │   │   ├── k-means/
│   │   │   │   └── README.md
│   │   │   ├── mean-shift/
│   │   │   │   └── README.md
│   │   │   ├── spectral-clustering/
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   ├── dimensionality-reduction/
│   │   │   ├── independent-component-analysis/
│   │   │   │   └── README.md
│   │   │   ├── linear-discriminant-analysis-projection/
│   │   │   │   └── README.md
│   │   │   ├── principal-component-analysis/
│   │   │   │   └── README.md
│   │   │   ├── singular-value-decomposition/
│   │   │   │   └── README.md
│   │   │   ├── t-sne/
│   │   │   │   └── README.md
│   │   │   ├── umap/
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   └── README.md
│   └── README.md
├── scripts/
│   ├── generate_catalog_docs.py
│   └── validate_catalog.py
├── tests/
│   ├── fixtures/
│   │   ├── required_syllabus.json
│   │   └── toolchain_smoke.cpp
│   ├── test_cpp_toolchain.py
│   ├── test_generate_catalog_docs.py
│   └── test_validate_catalog.py
├── .editorconfig
├── .gitattributes
├── .gitignore
├── AGENTS.md
├── catalog.yaml
├── CODE_OF_CONDUCT.md
├── conftest.py
├── CONTRIBUTING.md
├── LICENSE
├── docs/reviews/phase-0/PHASE-0-REPORT.md
├── pyproject.toml
├── README.md
├── requirements-dev.txt
└── SECURITY.md
```

## 3. Files created

| File group | Included files |
| --- | ---: |
| `Root project files` | 14 |
| `.github` | 6 |
| `docs` | 10 |
| `scripts` | 2 |
| `tests` | 5 |
| `dsa` | 110 |
| `machine-learning` | 116 |
| `artificial-intelligence` | 49 |
| **Total** | **312** |

The original Phase 0 deliverables are individually linked in [the complete 311-file foundation inventory](../../phase-0-files.md). This package adds **`docs/reviews/phase-0/PHASE-0-REPORT.md`**, producing **312 included files**. The full tree above lists every included path. `algorithm-atlas-phase-0.zip` is the external handoff artifact and is not recursively included inside itself.

Root files include `.editorconfig`, `.gitattributes`, `.gitignore`, `AGENTS.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `LICENSE`, `docs/reviews/phase-0/PHASE-0-REPORT.md`, `README.md`, `SECURITY.md`, `catalog.yaml`, `conftest.py`, `pyproject.toml`, and `requirements-dev.txt`.

The earlier [Phase 0 review](../../phase-0-review.md) and foundation inventory remain historical records of the original 311-file handoff. Their original Markdown/link counts predate the addition of this packaging report. The package-specific results below describe the current snapshot.

## 4. Catalog coverage summary

| Domain | Categories | Original syllabus occurrences | Canonical topics owned |
| --- | ---: | ---: | ---: |
| Data Structures and Algorithms | 12 | 105 | 97 |
| Machine Learning | 13 | 101 | 100 |
| Artificial Intelligence | 10 | 50 | 38 |
| **Total** | **35** | **256** | **235** |

| Progress measure | Count |
| --- | ---: |
| Reused syllabus memberships beyond canonical ownership | 21 |
| Planned canonical topics | 234 |
| Blocked canonical topics | 1 |
| Completed algorithms | 0 |
| Remaining canonical topics, including blocked | 235 |

All original category occurrences are preserved in [catalog.yaml](../../../catalog.yaml), the [algorithm index](../../algorithm-index.md), and the independent [syllabus baseline](../../../tests/fixtures/required_syllabus.json). Repeated algorithms point to one canonical folder. Distinct variants, including LDA classification/projection, general/POS HMMs, and backtracking/DP Subset Sum, remain separate. Canonicalization decisions are documented in the index and catalog notes.

| Category | Name | Original occurrences |
| --- | --- | ---: |
| A1 | Sorting | 11 |
| A2 | Searching | 6 |
| A3 | Recursion and Backtracking | 9 |
| A4 | Divide and Conquer | 7 |
| A5 | Graph Algorithms | 15 |
| A6 | Tree Algorithms | 14 |
| A7 | String Algorithms | 9 |
| A8 | Bit Manipulation | 4 |
| A9 | Mathematical and Number Theory | 7 |
| A10 | Two Pointers and Sliding Window | 3 |
| A11 | Greedy Algorithms | 7 |
| A12 | Dynamic Programming | 13 |
| B1 | Supervised Learning — Regression | 7 |
| B2 | Supervised Learning — Classification | 11 |
| B3 | Ensemble Methods | 8 |
| B4 | Unsupervised Learning — Clustering | 8 |
| B5 | Dimensionality Reduction | 7 |
| B6 | Association Rule Learning | 3 |
| B7 | Neural Networks and Deep Learning | 14 |
| B8 | Reinforcement Learning | 10 |
| B9 | Graph-Based Learning | 3 |
| B10 | Optimization | 10 |
| B11 | Time Series | 6 |
| B12 | Anomaly Detection | 3 |
| B13 | Natural Language Processing | 11 |
| C1 | Uninformed Search | 6 |
| C2 | Informed Search | 6 |
| C3 | Local Search | 8 |
| C4 | Global Search and Optimization | 7 |
| C5 | Adversarial Search | 3 |
| C6 | Constraint Satisfaction Problems | 5 |
| C7 | Multi-Agent Systems and Game Theory | 3 |
| C8 | Fuzzy Logic | 2 |
| C9 | Swarm Intelligence | 2 |
| C10 | Computer Vision | 8 |

## 5. Validation and CI results

Local review environment: Python **3.14.2**, pytest **9.1.1**, PyYAML **6.0.3**, macOS/arm64, and **Apple Clang 21.0.0** invoked as `g++`. The local `.venv` supplies development dependencies and is intentionally absent from the archive.

Fresh checks performed while preparing the handoff:

| Check | Actual result |
| --- | --- |
| Catalog completeness, schema, canonical folders, artifacts/statuses, and local documentation links | **Passed:** 35 categories, 256 syllabus entries, 235 canonical topics, 292 Markdown files, and 3,204 relative links; zero errors. |
| Generated catalog documentation | **Passed:** 277 pages checked; zero changes required. |
| Full infrastructure suite, requiring a C++ compiler | **79 passed, 0 failed, 0 skipped**, including real C++17 and C++20 compilation and execution. |
| Phase boundary | **Passed:** no Python/C++ algorithm source files under `dsa/`, `machine-learning/`, or `artificial-intelligence/`; all algorithm work remains planned or blocked. |
| Archive content policy | Exported from the project deliverable list, preserving `.github` and root dotfiles while excluding local/private/generated artifacts. No symlinks are exported. |
| ZIP integrity and completeness | **Passed:** 312 regular files and 283 directory entries; no duplicate, unsafe, or symlink entries; CRC checks and byte-for-byte source comparison passed. |
| Credential/artifact inspection | **Passed:** no prohibited paths, generated binaries, credential filenames, or recognizable secret patterns detected among exported files. |
| Extracted-copy validation | **Passed:** catalog/link validation and generated-document check passed; **79 tests passed, 0 failed, 0 skipped** from a temporary extraction without bundled `.git` or `.venv`. The installed local development interpreter supplied dependencies. |

[GitHub Actions](../../../.github/workflows/ci.yml) is configured for Python **3.11, 3.12, 3.13, and 3.14** on Ubuntu, running the validator, generated-doc check, and full lightweight pytest suite with a required C++ compiler. Both C++17 and C++20 are selected by default. The workflow supports push, pull-request, and manual triggers, uses read-only repository permissions, and disables checkout credential persistence.

**Hosted CI has not run.** Local validation is not a GitHub Actions pass, and compatibility across the entire hosted matrix is not claimed. No GitHub push or publication was performed to produce this archive.

To reproduce after extraction, from `algorithm-atlas/`, with Python 3.11+ and a C++17/C++20 compiler available:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Windows activation and compiler details are in [getting started](../../getting-started.md). Default checks use small fixtures and do not download datasets or model weights. Reproduction requires installing the declared development dependencies; the ZIP does not bundle a virtual environment or third-party packages.

## 6. Known issues or incomplete requirements

- **No incomplete Phase 0 requirement is known.** Algorithm implementations, full per-algorithm lessons, examples, and algorithm tests are intentionally deferred to their approved phases.
- **Dynamic Policy Optimization (DPO) remains blocked.** The intended reference or precise definition must be clarified by the maintainer before that later lesson is implemented. The exact requested topic is preserved; it has not been substituted with Direct Preference Optimization. See [terminology decisions](../../terminology-decisions.md).
- **Hosted CI remains unexecuted.** This is a validation limit of the local handoff; running remote CI or publishing requires separate authorization.
- **Phase transition prose requires maintenance later.** Once Phase 1 is explicitly approved, update the generator's Phase 0 prose and progress/agent instructions along with the catalog state. No such transition is made in this package.
- **Validation scope:** static catalog/link checks cannot establish the correctness of unimplemented algorithms, prove historical test claims, or guarantee external URL availability. Credential filename and recognizable token-pattern checks are heuristic; no detected secrets are included.

The archive excludes `.git`, all virtual environments, Python/test/tool caches, editor/OS metadata, build directories, compiled binaries, model weights, datasets, credential files, and recognized secret-bearing content. Source fixtures, documentation, license/attribution, scripts, tests, and configurations are retained.

**Development remains stopped at Phase 0.** Phase 1 may begin only after the user's explicit instruction:

> Phase 0 Approved. Start Phase 1.

Preparing this ZIP does not authorize algorithm implementation, commits, pushes, or publication. Review and approval remain mandatory between development phases.
