# ALGORITHM ATLAS — PHASE 22
# B10: OPTIMIZATION ALGORITHMS
## COMPLETE CODEX MASTER PROMPT
### Catalog-Driven Scope | From-Scratch Python + NumPy | Mathematical Correctness | Independent Oracles | Numerical Stability | Full Regression Audit | Review Package

---

# 0. PROJECT IDENTITY AND MISSION

Repository: `algorithm-atlas`
Owner: MD.Khalid Hasan
GitHub: `khalidhasan7343`
License: MIT

Target phase: **Phase 22**
Target category: **B10 — Optimization**

The owner reports that Phase 21 Graph-Based Learning is complete.

The previously reported B10 catalog size is 10 entries, but this must be verified against the CURRENT repository catalog.

**Do not invent the exact algorithm list.**

Read `catalog.yaml` and derive:

- Exact category name
- Exact category ID
- Exact canonical directory
- Exact algorithm names
- Exact algorithm slugs
- Exact algorithm count
- Existing implementation statuses
- Shared canonical memberships
- Explicit blockers, if any

The repository's current `catalog.yaml` and `AGENTS.md` are authoritative.

## PRIMARY OBJECTIVE

Complete every well-defined canonical algorithm belonging to B10 Optimization with:

1. Genuine educational implementations
2. Python and NumPy
3. Mathematically correct update rules
4. Correct objective-function handling
5. Robust convergence and stopping logic
6. Independent mathematical oracles
7. Numerical stability verification
8. Reproducible randomized testing
9. Comprehensive edge-case testing
10. Exact 25-section README documentation
11. Catalog and documentation integration
12. Full ML regression testing
13. Full DSA regression testing
14. C++17 and C++20 compatibility verification
15. Complete Phase 22 review report
16. Reproducible ZIP review package
17. SHA-256 checksum
18. Machine-readable JSON metadata

Do not claim completion without actual verification.

Do not commit, push, tag, release, or begin Phase 23 without explicit owner authorization.

---

# 1. OWNER APPROVAL CHECKPOINT

Before making Phase 22 implementation changes:

1. Inspect the Phase 21 Graph-Based Learning review report.
2. Verify the three B9 algorithms are complete.
3. Verify catalog and documentation checks.
4. Inspect the Phase 21 review package metadata.
5. Verify explicit owner approval for the Phase 21 completion.
6. If the approval is not recorded or cannot be established, request owner confirmation.

The owner has reported that Phase 21 is done, but do not fabricate formal approval evidence.

Once the required approval is established, proceed through all internal Phase 22 implementation batches without requesting approval after every batch.

Stop at the Phase 22 boundary.

---

# 2. MANDATORY REPOSITORY PREFLIGHT

Read and inspect:

- `AGENTS.md`
- `catalog.yaml`
- `README.md`
- `pyproject.toml`
- `conftest.py`
- `.gitignore`
- `.github/workflows/ci.yml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- Existing ML development documentation
- Existing ML dependency files
- B1–B9 implementations
- B1–B9 review reports
- Phase 21 review package metadata
- Existing optimization utilities
- Existing numerical gradient utilities
- Existing graph-learning utilities where relevant
- Catalog validation scripts
- Documentation generation scripts
- Review-package generation conventions

Capture:

- Git branch
- HEAD commit
- Working-tree status
- Existing uncommitted changes
- Python version
- NumPy version
- pytest version
- Optional SciPy availability
- Optional reference-library availability
- C++ compiler versions
- CI constraints
- Phase 21 approval status

Never overwrite unrelated owner modifications.

Never use destructive Git cleanup.

---

# 3. EXACT B10 CATALOG DISCOVERY

This step is mandatory.

Programmatically inspect `catalog.yaml`.

Find the category corresponding to:

**B10 — Optimization**

Extract its complete canonical inventory.

Create an initial scope table:

| # | Algorithm name | Canonical ID | Canonical path | Current status | Action |
|---|---|---|---|---|---|

Populate this table exclusively from the current catalog.

The historical expected count is 10.

If the current count differs:

1. Report the actual count.
2. Explain the discrepancy.
3. Follow the current authoritative catalog.
4. Do not silently add or remove entries.

For each catalog entry, inspect:

- Existing Python implementation
- Existing Python tests
- Existing README
- Existing examples
- Existing experimental scripts
- Existing optional C++
- Existing dependencies
- Existing mathematical references
- Existing canonical ownership
- Existing status fields

Distinguish:

- Complete and correct
- Implemented but defective
- Partially implemented
- Missing implementation
- Explicitly blocked
- Shared canonical implementation

Do not create duplicate canonical implementations.

Do not rename algorithms without owner approval.

---

# 4. OPTIMIZATION ALGORITHM CLASSIFICATION

Classify the actual B10 algorithms into their correct mathematical families.

Possible families include:

- First-order gradient optimization
- Stochastic gradient optimization
- Momentum-based optimization
- Adaptive gradient optimization
- Second-order optimization
- Quasi-Newton optimization
- Constrained optimization
- Derivative-free optimization
- Evolutionary optimization
- Population-based optimization
- Combinatorial optimization
- Other catalog-defined methods

These are classification possibilities, NOT an instruction to add algorithms.

Only implement algorithms actually present in the catalog.

For every discovered algorithm, identify:

1. Objective function
2. Optimization variables
3. Minimization or maximization
4. Mathematical assumptions
5. Update rule
6. Required derivatives, if any
7. Constraints, if any
8. Stochastic components, if any
9. Convergence criteria
10. Expected output
11. Theoretical limitations
12. Independent verification strategy

Do not apply gradient-based requirements to derivative-free algorithms.

Do not treat all optimizers as interchangeable.

---

# 5. IMPLEMENTATION LANGUAGE POLICY

## Machine Learning

Mandatory:

- Python
- NumPy where appropriate
- From-scratch core algorithm
- Python tests
- Mathematical verification
- Reproducible examples

Optional:

- C++
- C++ tests

Do not create placeholder C++ files.

## DSA

Preserve:

- Python mandatory
- C++ mandatory
- C++17 mandatory
- C++20 mandatory

Do not weaken track-aware validation.

## External optimization libraries

Do not delegate the essential algorithm to:

- `scipy.optimize.minimize`
- Ready-made scikit-learn optimizers
- PyTorch optimizers
- TensorFlow/Keras optimizers
- Other complete third-party optimization implementations

These may be used as independent reference oracles where justified.

Core algorithm logic must be implemented within Algorithm Atlas.

---

# 6. OPTIMIZATION API DESIGN

Follow existing repository conventions.

Where appropriate, support:

- `minimize(...)`
- `optimize(...)`
- `step(...)`
- `fit(...)`
- `predict(...)` only if relevant
- `get_state(...)` where useful

Do not force unrelated algorithms into one artificial interface.

Each algorithm should document:

- Objective function contract
- Parameter shape
- Initial parameter values
- Learning rate or step size
- Gradient function, if applicable
- Constraints, if applicable
- Maximum iterations
- Tolerance
- Random seed
- Termination status
- Final objective value
- Iteration count
- Convergence history, if supported

Validate all public inputs.

Do not silently mutate caller-owned arrays.

---

# 7. MATHEMATICAL FOUNDATIONS

For every algorithm, derive and document its exact mathematical formulation.

Depending on the algorithm, this may include:

- Gradient
- Hessian
- Jacobian
- Search direction
- Step size
- Momentum
- Adaptive moment estimates
- Curvature approximation
- Constraint projection
- Penalty function
- Population fitness
- Mutation or crossover
- Acceptance probability
- Exploration/exploitation behavior

Every formula must correspond to implemented code.

Do not copy a formula into the README if the implementation uses a different update.

Distinguish:

- Exact gradients
- Approximate gradients
- Stochastic gradients
- Subgradients
- Finite-difference estimates

Do not claim differentiability where it does not exist.

---

# 8. IMPLEMENTATION BATCH PLANNING

After discovering the exact catalog inventory, divide the B10 algorithms into logical batches.

Preferred organization:

## Batch A — Foundational Optimization

Implement catalog algorithms involving basic objective updates, if present.

## Batch B — Advanced Gradient Optimization

Implement momentum, adaptive or related methods, if present.

## Batch C — Curvature or Constrained Optimization

Implement second-order, quasi-Newton or constrained methods, if present.

## Batch D — Derivative-Free and Population-Based Optimization

Implement these only if they exist in B10.

## Batch E — Remaining Catalog Algorithms and Integration

Finish all remaining canonical B10 entries.

The exact batch count may change to match the actual catalog.

Do not add nonexistent algorithms just to fill a batch.

For every batch:

1. Inspect existing implementation.
2. Define the mathematical oracle.
3. Implement or repair the algorithm.
4. Add exact update tests.
5. Add edge-case tests.
6. Add numerical stability tests.
7. Add reproducibility tests.
8. Verify examples.
9. Write documentation.
10. Run targeted tests.
11. Record results.
12. Proceed to the next batch.

Stop only for genuine blockers or required owner decisions.

---

# 9. GRADIENT-BASED OPTIMIZATION REQUIREMENTS

Apply this section only to catalog algorithms that use gradients.

Verify:

- Correct gradient direction
- Correct learning-rate scaling
- Correct parameter update
- Correct treatment of bias parameters
- Correct state initialization
- Correct state persistence
- Correct update ordering
- Correct treatment of zero gradients
- Correct behavior with nonfinite gradients
- Correct stopping conditions

For stochastic optimizers, verify:

- Sample selection
- Batch selection
- Random-state handling
- Gradient estimation
- Update count
- Learning-rate schedule, if supported

For adaptive optimizers, verify the exact mathematical variant.

Pay particular attention to:

- Bias correction
- First-moment updates
- Second-moment updates
- Epsilon placement
- Weight decay
- Decoupled versus coupled regularization
- Step indexing

Do not claim two optimizer variants are identical when their update equations differ.

---

# 10. SECOND-ORDER AND QUASI-NEWTON REQUIREMENTS

Apply only if these methods appear in the catalog.

Verify:

- Gradient calculation
- Hessian or curvature approximation
- Search direction
- Linear-system solution
- Update rule
- Positive-definiteness assumptions
- Numerical conditioning
- Singular or indefinite curvature handling
- Step-size selection
- Convergence conditions

Do not explicitly invert a Hessian when a stable linear solve is appropriate.

Use well-conditioned small examples for exact verification.

Test ill-conditioned cases separately.

Document when the algorithm is not guaranteed to converge.

---

# 11. CONSTRAINED OPTIMIZATION REQUIREMENTS

Apply only if constrained algorithms appear in the catalog.

Define:

- Feasible set
- Equality constraints
- Inequality constraints
- Constraint violation
- Feasibility tolerance
- Objective value
- Optimality conditions
- Constraint qualification assumptions

Test:

- Feasible initialization
- Infeasible initialization
- Boundary solutions
- Active constraints
- Inactive constraints
- Constraint violation
- Invalid constraints
- Feasibility of final solution

Use analytical constrained examples where possible.

Do not claim KKT conditions guarantee global optimality without appropriate assumptions.

---

# 12. DERIVATIVE-FREE AND STOCHASTIC OPTIMIZATION

Apply only if these algorithms appear in the catalog.

Verify algorithm-specific mechanisms such as:

- Candidate generation
- Search neighborhoods
- Mutation
- Crossover
- Selection
- Acceptance criteria
- Temperature schedules
- Population updates
- Fitness evaluation
- Random sampling
- Termination

Use local random generators and fixed seeds.

Test:

- Exact deterministic transitions where possible
- Probability normalization
- Sampling distributions
- Population invariants
- Bounds preservation
- Objective evaluation counts
- Reproducibility
- Bounded execution

Do not treat an empirical improvement as proof of global optimality.

Do not fabricate convergence guarantees.

---

# 13. INDEPENDENT MATHEMATICAL ORACLES

Every algorithm must have an independent verification strategy.

Suitable oracle methods include:

- Hand-calculated one-step updates
- Analytical solutions
- Independently derived equations
- Exact solutions of small convex problems
- Finite-difference gradients
- Independent Hessian calculations
- KKT residual checks
- Exhaustive search on tiny finite domains
- Independent stochastic transition probabilities
- Optional SciPy reference solutions

Do not rely exclusively on the implementation's own helper functions.

For deterministic algorithms, compare against exact expected outputs where feasible.

For stochastic algorithms, separate:

1. Exact transition correctness
2. Statistical behavior
3. Optimization performance

Do not require bitwise equality with unrelated reference implementations.

---

# 14. ANALYTICAL BENCHMARK FUNCTIONS

Create small, reusable test-only objective functions.

Recommended examples:

## Quadratic objective

f(x) = 0.5 * x.T @ A @ x - b.T @ x

For symmetric positive-definite A:

x_star = solve(A, b)

Use this to verify suitable gradient-based methods.

## Rosenbrock function

Use as a nonlinear diagnostic objective where appropriate.

## Sphere function

f(x) = sum(x_i ** 2)

Use for basic optimization and stochastic search diagnostics.

## Constrained quadratic

Use when relevant to constrained optimizers.

## Tiny finite search space

Use exhaustive enumeration as an oracle for applicable discrete or population-based algorithms.

These are test functions, not new canonical catalog algorithms.

Do not assume every optimizer is suitable for every benchmark.

---

# 15. FINITE-DIFFERENCE GRADIENT CHECKING

For differentiable objectives, use central differences:

g_i ≈ [f(x + εe_i) - f(x - εe_i)] / (2ε)

Verify analytical gradients independently.

Where second-order derivatives are relevant, independently check Hessian calculations.

For stochastic methods:

- Fix random samples.
- Reuse the same randomness for positive and negative perturbations.
- Avoid comparing unrelated stochastic trajectories.

Use appropriate absolute and relative tolerances.

Avoid nondifferentiable points during ordinary gradient checks.

Test nondifferentiability handling separately.

Do not claim gradient checking passed without executing it.

---

# 16. CONVERGENCE AND STOPPING CONDITIONS

Every iterative algorithm must have bounded execution.

Implement appropriate stopping criteria:

- Maximum iterations
- Gradient norm
- Parameter-change tolerance
- Objective-change tolerance
- Constraint residual
- Search stagnation
- Algorithm-specific termination

Document the stopping rule precisely.

Distinguish:

- Converged
- Maximum iterations reached
- Numerical failure
- Invalid input
- Infeasible problem
- Unbounded problem, if detectable
- Unsupported objective

Do not silently report convergence when the iteration limit was reached.

Do not guarantee global convergence for nonconvex objectives.

---

# 17. NUMERICAL STABILITY

Audit:

- Division by zero
- Nonfinite gradients
- Nonfinite objectives
- Overflow
- Underflow
- Ill-conditioned matrices
- Singular Hessians
- Tiny denominators
- Invalid learning rates
- Invalid tolerances
- Invalid iteration counts
- Exploding parameter values
- Invalid probability values
- Degenerate constraints
- Empty parameter arrays
- Shape mismatches
- Unexpected broadcasting

Use stable mathematical formulations.

Do not silently suppress warnings.

Do not replace NaNs with arbitrary values without documented justification.

---

# 18. REPRODUCIBILITY

For stochastic algorithms:

- Use local NumPy random generators.
- Accept an explicit random seed where appropriate.
- Avoid unexpected global RNG mutation.
- Document seed semantics.
- Keep CI test workloads small.
- Use bounded populations, batches and iterations.

For deterministic algorithms:

- Verify repeated calls produce consistent results.
- Verify no hidden random initialization affects results.

For statistical convergence tests:

- Use multiple seeds where justified.
- Avoid brittle exact-performance thresholds.
- Report genuine limitations.

---

# 19. CORRECTNESS AND PROPERTY TESTING

Create tests for:

- Correct update equations
- Correct objective evaluation
- Correct parameter shapes
- Correct convergence status
- Correct iteration counts
- Invalid learning rates
- Invalid tolerances
- Invalid dimensions
- Nonfinite inputs
- Empty inputs
- Boundary values
- Deterministic seeds
- State initialization
- State reset
- Repeated optimization calls
- Numerical stability
- Reproducible results

Where mathematically justified, verify properties such as:

- Objective decrease under valid step-size conditions
- Feasibility preservation
- Nonnegative variance estimates
- Valid probability distributions
- Correct stationary points
- Correct analytical solutions

Do not assert monotonic objective decrease for algorithms that do not guarantee it.

---

# 20. PERFORMANCE AND COMPLEXITY

For each discovered optimizer, document:

- Per-iteration time complexity
- Memory complexity
- Gradient evaluation cost
- Hessian evaluation cost, if relevant
- Objective evaluation count
- Population size, if relevant
- Iteration complexity
- Convergence assumptions
- Practical limitations

Use actual measured data for benchmarks.

Do not invent runtime results.

Do not claim one optimizer is universally superior.

---

# 21. EDUCATIONAL EXAMPLES

Every algorithm must have a small reproducible example.

Examples should demonstrate:

- Objective definition
- Initialization
- Hyperparameters
- Optimization call
- Final parameters
- Final objective
- Iteration count
- Termination status

For appropriate algorithms, compare the result with an analytical optimum.

For stochastic methods, explain variation across seeds.

Verify every documented output by running the example.

Do not hardcode fabricated convergence results.

---

# 22. DOCUMENTATION REQUIREMENTS

Every B10 canonical algorithm must follow the exact 25-section README structure specified by `AGENTS.md`.

Do not replace or reorder required headings.

Each README should explain:

- Algorithm motivation
- Mathematical assumptions
- Optimization objective
- Update equations
- Hyperparameters
- Input/output contract
- Pseudocode
- Correctness reasoning
- Convergence behavior
- Time complexity
- Space complexity
- Numerical stability
- Worked example
- Python implementation
- Testing methodology
- Independent oracle
- Applications
- Limitations
- Related algorithms
- References

Document the exact optimizer variant implemented.

Do not claim C++ support unless it actually exists.

---

# 23. CATEGORY README

Create or update the authoritative B10 category README.

Its exact path must be derived from `catalog.yaml`.

Include:

1. Optimization overview
2. Exact catalog algorithm inventory
3. Mathematical taxonomy
4. Gradient-based versus derivative-free methods
5. Deterministic versus stochastic methods
6. First-order versus second-order methods
7. Constrained versus unconstrained optimization
8. Convergence assumptions
9. Numerical stability
10. Hyperparameter selection
11. Comparison table
12. Reproducible examples
13. Canonical algorithm links
14. Learning roadmap
15. Limitations and references

Only include categories and methods relevant to the actual B10 inventory.

---

# 24. PREVIOUS-PHASE COMPATIBILITY

Inspect existing ML implementations that use optimization.

Pay particular attention to:

- B1 Regression
- B2 Classification
- B3 Ensemble Methods
- B4 Clustering
- B5 Dimensionality Reduction
- B7 Neural Networks and Deep Learning
- B8 Reinforcement Learning
- B9 Graph-Based Learning

Identify reusable numerical utilities.

Avoid introducing circular imports.

Do not silently change previously approved optimization behavior.

If shared utilities are modified:

1. Document the change.
2. Add compatibility tests.
3. Verify existing algorithms.
4. Run relevant regressions.
5. Record any behavior changes.

Do not move canonical algorithms without catalog authorization.

---

# 25. CATALOG AND PROGRESS INTEGRATION

Update the current repository's relevant B10 records.

Potential files:

- `catalog.yaml`
- `docs/progress.md`
- `docs/learning-roadmap.md`
- `docs/algorithm-index.md`
- B10 category README
- Root README where necessary

Preserve:

- All DSA canonical algorithms
- B1–B9 implementations
- Previous owner approvals
- Existing canonical IDs
- Existing category memberships
- Existing shared canonical ownership
- Existing blocked entries

Important:

The B8 Dynamic Policy Optimization entry must remain blocked under the owner's earlier approved decision.

Do not reopen or rename DPO during Phase 22.

Do not mark Phase 22 owner-approved.

---

# 26. TESTING STRATEGY

Use multiple independent test layers.

## Layer A — Unit Tests

Verify exact mathematical updates.

## Layer B — Analytical Oracle Tests

Compare against known solutions.

## Layer C — Gradient Verification

Use finite differences where relevant.

## Layer D — Edge Cases

Test invalid inputs and numerical boundaries.

## Layer E — Randomized Tests

Use deterministic seeds.

## Layer F — Optimization Behavior

Verify meaningful progress on suitable small problems.

## Layer G — Infrastructure Tests

Verify catalog and documentation integration.

## Layer H — Full Regression Tests

Verify previous ML and DSA functionality.

Do not weaken assertions merely to make tests pass.

---

# 27. REQUIRED VALIDATION COMMANDS

Run the authoritative repository commands:

```bash
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest --require-cpp
```

Run targeted B10 tests using the exact canonical directory discovered from `catalog.yaml`.

For example, only if the directory is actually `machine-learning/optimization`:

```bash
python -m pytest machine-learning/optimization -q
```

Do not assume that example path is authoritative.

Run:

- Exact update tests
- Independent oracle tests
- Gradient tests
- Numerical stability tests
- Reproducibility tests
- Convergence tests
- Edge-case tests
- Existing optimizer compatibility tests

If the full test suite is too large:

1. Split it into bounded groups.
2. Run every feasible group.
3. Record exact commands.
4. Record exact pass/fail/skip counts.
5. Record unexecuted checks honestly.

Never claim an unexecuted test passed.

---

# 28. NEGATIVE INFRASTRUCTURE TESTS

Verify:

- ML Python-only implementations are valid.
- Missing required Python implementations are rejected.
- Missing required Python tests are rejected.
- Invalid canonical paths are rejected.
- Duplicate canonical IDs are rejected.
- Missing README sections are detected.
- Generated documentation drift is detected.
- Optional ML C++ follows repository policy.
- DSA missing C++ is rejected.
- C++17 and C++20 requirements remain enforced.
- B10 tests are included in CI discovery.
- Existing blocked catalog entries remain valid.

Do not weaken validators to hide failures.

---

# 29. FULL REGRESSION AUDIT

Run appropriate regression checks across:

- B1 Regression
- B2 Classification
- B3 Ensemble Methods
- B4 Clustering
- B5 Dimensionality Reduction
- B6 Association Rule Learning
- B7 Neural Networks and Deep Learning
- B8 Reinforcement Learning
- B9 Graph-Based Learning
- B10 Optimization
- DSA Python
- DSA C++17
- DSA C++20
- Shared ML infrastructure
- Catalog validation
- Documentation generation
- CI-equivalent checks

Pay particular attention to existing neural-network optimizer behavior.

Preserve the B8 DPO blocked status.

Do not modify unrelated approved algorithms without a demonstrated defect.

---

# 30. SECURITY AND RESOURCE LIMITS

Inspect for:

- Unbounded iterations
- Infinite loops
- Excessive allocations
- Unsafe numerical operations
- Unsafe serialization
- Arbitrary code execution
- Hidden network downloads
- Unexpected subprocess execution
- Temporary-file leakage
- Hardcoded secrets
- Unexpected global random-state mutation

Keep standard tests CPU-friendly.

Do not require GPUs.

Do not download datasets.

Do not add large pretrained model files.

---

# 31. PHASE 22 REVIEW REPORT

Create:

`docs/reviews/optimization/OPTIMIZATION-REVIEW-REPORT.md`

If `AGENTS.md` or the current category slug requires a different canonical report path, use the authoritative convention and record the exact path.

The report must include:

1. Phase identity
2. B10 category identity
3. Exact catalog inventory
4. Actual algorithm count
5. Canonical paths
6. Existing versus new implementations
7. Implementation status by algorithm
8. Mathematical objectives
9. Update-equation verification
10. Independent oracle results
11. Gradient verification, where applicable
12. Hessian verification, where applicable
13. Constraint verification, where applicable
14. Stochastic mechanism verification, where applicable
15. Numerical stability
16. Reproducibility
17. Convergence tests
18. Edge-case tests
19. Educational examples
20. Documentation validation
21. Catalog validation
22. B1–B9 regression results
23. DSA regression results
24. C++17/C++20 results
25. CI-equivalent checks
26. Shared utility compatibility
27. Files created
28. Files modified
29. Dependencies
30. Bugs discovered
31. Fixes applied
32. Known limitations
33. Unresolved blockers
34. Reproduction commands
35. Review package paths
36. Owner approval: pending

Use actual test results.

Do not fabricate counts, timings, or approval evidence.

---

# 32. PHASE 22 REVIEW PACKAGE

Use the authoritative category slug.

If the category slug is `optimization`, create:

```text
artifacts/review-packages/optimization/
├── algorithm-atlas-optimization-review.zip
├── algorithm-atlas-optimization-review.zip.sha256
└── algorithm-atlas-optimization-review.json
```

If the actual catalog slug differs, adapt the paths consistently.

Include:

- All canonical B10 implementations
- All B10 tests
- All B10 algorithm READMEs
- B10 category README
- B10 review report
- Relevant shared numerical utilities
- Relevant previous ML source and tests
- Relevant DSA source and tests
- `AGENTS.md`
- `catalog.yaml`
- `README.md`
- `pyproject.toml`
- `conftest.py`
- Dependency configuration
- Validation scripts
- Documentation generators
- CI configuration

Exclude:

- `.git`
- Virtual environments
- Python caches
- pytest caches
- Compiled binaries
- Secrets
- Large datasets
- Model checkpoints
- Previous review ZIPs
- Nested ZIPs
- Temporary files

Verify:

1. ZIP opens.
2. ZIP CRC passes.
3. Extraction paths are safe.
4. Required files exist.
5. SHA-256 matches.
6. JSON metadata matches.
7. Independent extraction succeeds.
8. Catalog validation succeeds from extracted source.
9. Documentation validation succeeds from extracted source.
10. Relevant tests execute from extracted source.

Record any unexecuted checks.

---

# 33. FINAL COMPLETION SUMMARY

Provide a complete Phase 22 summary.

| Field | Result |
|---|---|
| Phase | 22 |
| Category | B10 — Optimization |
| Catalog algorithm count | Verified actual count |
| Implemented algorithms | Actual count |
| Incomplete algorithms | Actual count |
| Blocked algorithms | Actual count |
| Implementation batches | Actual count |
| Exact update tests | Actual results |
| Independent oracle tests | Actual results |
| Gradient checks | Actual results |
| Numerical stability | Actual results |
| Reproducibility | Actual results |
| Convergence tests | Actual results |
| Edge-case tests | Actual results |
| B1–B9 regression | Actual results |
| DSA regression | Actual results |
| C++17/C++20 | Actual results |
| Catalog validation | Actual result |
| Documentation validation | Actual result |
| CI-equivalent checks | Actual result |
| B8 DPO blocked status | Preserved |
| Review report | Exact path |
| Review ZIP | Exact path |
| SHA-256 | Exact path |
| JSON metadata | Exact path |
| Owner approval | Pending |

Also provide a per-algorithm table:

| Algorithm | Canonical path | Implementation | Tests | Documentation | Oracle | Status |
|---|---|---|---|---|---|---|

List:

- All completed algorithms
- All incomplete algorithms
- All blockers
- Failed tests
- Skipped tests
- Unexecuted checks
- Numerical limitations
- Convergence limitations
- Dependency changes
- Infrastructure changes
- Reproduction commands

Do not claim full completion when mandatory work remains unfinished.

---

# 34. FINAL OWNER REVIEW GATE

After finishing the B10 Optimization implementation, validation, documentation and review package:

**STOP AND WAIT FOR EXPLICIT OWNER APPROVAL.**

Do not:

- Start Phase 23.
- Start another ML category.
- Commit or push.
- Create a release.
- Mark Phase 22 owner-approved.
- Modify B8 DPO.
- Invent additional algorithms.
- Hide failed tests.
- Fabricate verification results.

The owner must review the Phase 22 report and review ZIP before authorizing the next phase.

---

# 35. EXECUTION INSTRUCTION

Begin with:

**STEP 1 — Repository preflight and Phase 21 approval verification.**

Then:

**STEP 2 — Extract the exact B10 algorithm inventory from `catalog.yaml`.**

Show the verified inventory before implementation.

Then execute all approved Phase 22 implementation batches, mathematical audits, tests, documentation updates, and review packaging.

Do not request confirmation between internal batches unless a genuine catalog ambiguity, missing mathematical specification, or owner authorization blocker arises.

End with the full Phase 22 completion report.

**BEGIN PHASE 22 ONLY AFTER SATISFYING THE PHASE 21 APPROVAL CHECKPOINT.**