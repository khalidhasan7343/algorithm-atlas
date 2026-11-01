# Phase21 — B9 Graph-Based Learning review

## 1. Phase identity

Algorithm Atlas; owner **MD.Khalid Hasan**; MIT; target repository
https://github.com/khalidhasan7343/algorithm-atlas. Client date2026-10-31 Asia/Dhaka.
Initial branch main,HEAD7202b5736cb657cbc84e8b33bec63b0a5e5d9a0c. The pre-existing B7/B8 dirty worktree
and staged reports are captured in [baseline](../../graph-learning-evidence/baseline.json).
No unrelated owner modifications were reset,rewritten or committed.

The owner explicitly stated “Approved pervious work and review done.now follow
this properly” immediately after the verified Phase20 handoff,and supplied the
Phase21 instructions. [Approval evidence](../../graph-learning-evidence/approval-evidence.json)
records Phase20 implementation review approved as9 completed+1 intentionally blocked.
Accepted ZIP SHA256 af35bca67293acb1d4ddf243397638175fc23289661fcbf789faddb995e0bf82; checksum/CRC and its
recorded actual extracted3841-test pass were verified. Those results are historical,
not new Phase21 tests. New Phase21 owner approval remains **pending**.

## 2. B9 category identity

Graph-Based Learning,canonical category machine-learning/graph-learning.
[Locked scope](../../graph-learning-scope.md) is exactly three existing canonicals
in three internal batches. Genuine NumPy/stdlib core; ML C++ optional/absent.
[Original supplied request](../../graph-learning-evidence/phase21-request.md) is preserved.
No Phase22,B10,other category or Git publication is authorized.

## 3. Three-algorithm inventory

| Batch | Canonical ID | Final local gate | Scope |
| --- | --- | --- | --- |
| 1 | pagerank | 43 passed | Personalized weighted random-surfer ranking |
| 2 | node2vec | 42 passed | Weighted undirected second-order walks and SGNS |
| 3 | graph-convolutional-networks | 43 passed | Masked multiclass tanh GCN |

Additional shared B9 contracts18 passed; total B9 **146 passed**.
[Checkpoint gates](../../graph-learning-checkpoints.md) preserve actual commands,
JUnit and example/lesson verification. Internal algorithm tests do not imply owner approval.

## 4. Canonical paths

All three retain machine-learning/graph-learning/<id>/README.md,
python/solution.py,python/example.py,tests/test_python.py. Shared support/conftest/
contracts tests remain under the B9 category. IDs,paths,owners,related topics and
original syllabus membership/order are unchanged; inventory35/256/235.

## 5. Existing versus new implementations

B9 originally had three planning READMEs and no implementations/tests. The three
cores,examples,independent tests and full lessons are new. B7 already supplied a
two-layer normalized tanh GCN **regressor**. B9 reuses its normalization utility,
preserves every B7 byte,and implements its own multiclass classifier/objective/
backpropagation. No canonical collapse or third-party complete algorithm delegation.

## 6. PageRank mathematical correctness

Rows of A encode outgoing weights. Nonzero rows become stochastic P; dangling
rows become v. The column-rank update is r'=d P.T r+(1-d)v. Nonnegative mass is
preserved; d<1 gives an exact-arithmetic L1 contraction. Personalization is an
explicit probability vector,not silently normalized arbitrary weights. Small
stationary linear systems are constructed independently with scalar loops and
np.linalg.solve; the core itself uses power iteration. Eight named stationary
oracle cases passed,including singleton,cycle,weighted,disconnected and dangling graphs.

## 7. PageRank convergence

Observed residual ρ=||d P.T r+(1-d)v-r||₁ and ρ/(1-d) are exposed. The latter is an
exact-arithmetic error bound,not interval-certified floating-point accuracy.
Near1 damping slows iteration and amplifies roundoff. Max-iteration exhaustion
returns an approximate score with converged_=False and iteration-budget status.
A dedicated one-step non-convergence test and extreme valid damping/weights pass.

## 8. PageRank dangling-node handling

Every zero-degree row uses v,including all-isolated graphs. The two-node hand
example at d=.5,v=[.5,.5] gives[.4,.6]. Zero damping returns v. Rank nonnegativity,
sum1,stationarity,weighted row-rescaling invariance and graph permutation are checked.
No strongly-connected-graph assumption is imposed. Directed graphs and self-loops
are accepted only by this B9 core; the other graph contracts are explicit.

## 9. Node2Vec biased-walk correctness

First steps use normalized edge weights. After t→v,weights are multiplied by
1/p for return,1 for distance1 and1/q for distance2. Only exactly symmetric
weighted zero-diagonal graphs are supported. Independent BFS-distance oracles
check transition probabilities for p=q=1,p<1,q<1 and other settings; no empirical
sampling frequency is the sole oracle. Seven named walk/window checks pass;
seeded randomized exact probabilities and transition permutation also pass.
Isolated walks stop at one token; no infinite traversal is possible.

## 10. Node2Vec Skip-Gram correctness

Separate input/context tables minimize mean[softplus(-positive dot)+sum negative
softplus(dot)]. Noise follows positive-context frequencies^0.75 and is sampled
with replacement,including possible positive/target collisions. Fixed negatives
and full-batch clipped steps are an explicitly documented educational variant.
Repeated vector indices accumulate with np.add.at. The hand scalar loss2log2 and
context gradients±.5 are checked independently. Walks or random embeddings alone
are not reported as training; tests verify real updates and objective reduction.

## 11. Node2Vec gradient verification

An independent scalar-loop loss,without production helpers,is centrally perturbed
at every input/context coordinate on a repeated-index corpus. One SGNS finite-
difference test checks12 coordinates. Stable logaddexp/tanh sigmoid avoid overflow;
extreme-logit and tiny-common-weight-scale cases pass. Fixed negatives permit a
well-defined finite-difference objective; this is not full-softmax likelihood.

## 12. Node2Vec reproducibility

Local seeded Generators govern walk shuffles,initialization and noise. No global
RNG state or caller input is mutated. Same-environment seeded walks/fits are equal;
coordinate equality across independently trained implementations is not required.
Isolated embeddings retain initial random values and have no training signal.
Three declared seeds produce the actual observations in section21; no universal
community separation or statistical superiority is inferred.

## 13. GCN normalization correctness

Exactly symmetric nonnegative weighted A must have zero input diagonal. The
self_loops flag controls a single added identity. S=D^(-1/2)(A+I)D^(-1/2),or the
no-loop variant,uses zero inverse degree on zero-degree nodes. A separate scalar
normalization oracle checks degrees,weights and isolated nodes;3 named normalization/
compatibility cases pass. S is not PageRank's row-stochastic P. Approved B7 normalization
is reused with its byte hash preserved; independent oracles avoid shared-bug agreement.

## 14. GCN forward-pass correctness

B=S X;H=tanh(B W1+b1);T=S H;Z=T W2+b2;Q=row_softmax(Z).
Hand and independent scalar/matrix calculations verify two-layer logits,own-node
self-loop behavior,isolates and real graph dependence versus S=I. The model is a
specific normalized GCN classifier,not a graph-ignoring MLP. Its tanh/bias/SGD
variant differs from the cited illustrative ReLU/dropout/optimizer setup.

## 15. GCN backpropagation correctness

The objective is mean masked cross-entropy plus l2/2*(||W1||²+||W2||²); biases are
unpenalized. Output adjoints are zero on unselected rows. Hidden adjoints include
S.T@(delta@W2.T),then tanh derivative. Independent tests verify known unselected
labels cannot leak into training. Unknown labels are-1; a nonempty boolean mask
must select known labels containing all consecutive trained classes.

## 16. GCN finite-difference gradient tests

Two tests,with l2=0 and.13,centrally perturb all W1,b1,W2,b2 blocks against an
independent forward/softmax/loss oracle. Each checks17 coordinates,34 total.
Together with SGNS there are3 named gradient tests and46 coordinate checks.
Finite differences use1e-6 steps and stated numerical tolerances on smooth,
non-saturated inputs. No failed gradient check was disabled or loosened.

## 17. Graph permutation equivariance

For node permutation Π,the normalized S transforms as Π S Π.T. Shared row-wise
layers and activations yield f(Π A Π.T,Π X)=Π f(A,X). Tests cover random graphs,
fixed parameters,trained inference and consistently permuted labels/masks during
training. This is **equivariance**,not invariance. Three named permutation cases
cover GCN,PageRank and the Node2Vec transition law; stochastic embedding coordinates
are not falsely required to be equivariant under an unchanged sampling stream.

## 18. Independent oracle results

**27 oracle-marked tests passed**; they overlap the146 B9 tests. PageRank uses a
direct stationary system; Node2Vec uses BFS transition distances and scalar SGNS;
GCN uses independent normalization/forward/loss and finite differences. Tests do
not rely solely on production helpers. NetworkX/PyG/DGL are unavailable and were
not installed,skipped-as-passed or claimed as executed references.
[Primary-source access ledger](../../graph-learning-evidence/reference-sources.json)
records verified references and inaccessible endpoints without claiming unread content.

## 19. Numerical stability

**7 numerical-marked tests passed**. Validate finite real graph/features,probability
mass,integer settings,dimensions and bounds. Stable softplus/softmax/log-sum-exp
avoid exp overflow/log0. Transitions rescale common tiny edge weights before bias.
Global gradient clipping and finite parameter caps bound updates but do not repair
poor conditioning or prove convergence. Near1 PageRank damping and tanh saturation
remain explicit limitations. Failed refits preserve previous fitted state.

## 20. Randomized tests

Fixed seeds test small directed/undirected weighted graphs,isolates,disconnected
components,transition distances and node permutations. Invalid directions,
self-loops,dimensions,nonfinite values and excessive resource budgets fail clearly.
Sixteen named seed/RNG/reproducibility cases pass; these overlap other selections.
Prospective corpus/operation guards are checked before walk allocation.

## 21. Educational examples

All3 executable examples match exact printed lesson output and hand/numerical
expectations. They show PageRank transitions/ranks,Node2Vec walks/pairs/trained
vectors,and GCN normalization/propagated features/learned predictions.
[Actual three-seed study](../../graph-learning-evidence/educational-training-results.json):

| Seed | Node2Vec loss before → after | cos(0,1) / cos(0,4) | GCN loss before → after | GCN train / unknown-node accuracy |
| --- | --- | --- | --- | --- |
| 21 | 2.77785255 → 1.77372255 | 0.998601 / 0.184606 | 0.63393832 → 0.00817123 | 1.00 / 1.00 |
| 22 | 2.77169923 → 1.72634062 | 0.997918 / 0.117469 | 1.28606574 → 0.01033920 | 1.00 / 1.00 |
| 23 | 2.77013831 → 1.79159103 | 0.985585 / 0.214838 | 0.48918478 → 0.00688819 | 1.00 / 1.00 |

These are all declared seeds on one synthetic graph; no confidence interval or
benchmark superiority is claimed. GCN class-dimension checks2,3,8 also execute
and retain their actual loss/shape/accuracy observations. Actual training times
are in JSON,not presented as comparative performance guarantees.

## 22. Documentation validation

All3 algorithm lessons have exact25 mandatory sections,specific objectives,
equations,pseudocode,dry runs,API contracts,complexity,limits,tests,references and
maintainer/MIT attribution. The generated B9 category compares ranking,embeddings
and classification,documents graph representations/numerical issues and links
examples. Generated111 managed pages check cleanly. Source-only hand-written
lessons are preserved by the generator. Local links are independently validated.

## 23. Catalog validation

Passed. Inventory remains35 categories/256 memberships/235 canonicals.
Completed166; remaining69,including one intentionally blocked DPO.
Only the3 B9 records gain completion evidence; no other canonical changes.
Current Phase20 approval is reconciled from explicit owner evidence; historical
Phase20 reports/packages retain their pending-at-generation metadata unchanged.

## 24. B1–B8 regression results

Fresh explicit gates **281/398/253/206/162/162/221/141 passed**,respectively.
B5's162 includes17 shared vanilla cases also present in B7. The full unique-case
matrix records B5-folder145 and B7 including vanilla221; those shared17 are not
added twice. All B1–B8 source/test/lesson bytes remain unchanged.

## 25. DSA regression results

Fresh full required-C++ suite **3,999 passed**,zero failures/errors/skips;
443.944 seconds including runner overhead,started
2026-10-31T20:17:52.628388+06:00. DSA unique cases **1687**: Python/shared1149
plus the two actual compiler standards below. [JUnit-derived full matrix](../../graph-learning-evidence/test-matrix.json).
All DSA source/tests/lessons and compiler fixtures remain byte-identical.

## 26. C++17/C++20 results

Actual DSA C++17 **269 passed**,C++20 **269 passed**,including compilation and
execution under available Apple Clang. Compiler infrastructure checks also pass.
Optional absent ML C++ is not counted as either a required-language pass or skip.

## 27. CI-equivalent checks

Full local3999 tests,B9146 and all infrastructure359 pass. Unchanged root pytest
discovery and CI --require-cpp include the new tests. Catalog/generated/example/
scope checks pass. The configured Python3.11–3.14 hosted matrix was **not executed
or verified**; only actual local Python3.14.2/macOS/Clang results are claimed.
[Final command records](../../graph-learning-evidence/final-results.json) and
[configuration records](../../graph-learning-evidence/configuration-results.json).

## 28. Shared B7 GNN compatibility

Fresh B7 GNN **8 passed**; full B7 **221 passed**. B9's shared-normalization and
generic matrix-forward compatibility case also passes,alongside independent
oracles. No B7 generic utility or other approved code was modified. Both canonical
IDs and their distinct regression/classification contracts are preserved.

## 29. Files created

Three solution/example/test sets; B9 support/conftest/shared contracts; B9 policy
tests; scope/conventions/checkpoints/evidence; verification/evaluation/runner/package
scripts;this review report and package directory.
[Baseline-relative inventory](../../graph-learning-evidence/changed-files.json)
distinguishes all new Phase21 work from pre-existing B7/B8 changes. No datasets,
model weights,generated binaries,environment,secrets or temporary authoring helpers
are added to the repository snapshot.

## 30. Files modified

Three B9 planning lessons,current development/approval metadata,root/current guides,
roadmap,generated navigation/progress/category pages and review/package indexes.
Generator gains B9 material and metadata-aware Phase20/DPO approval text.
Validator,track policy,CI and root compiler fixtures remain unchanged.
[Preservation proof](../../graph-learning-evidence/preservation-results.json)
verifies **2897 protected prior files**,including
all approved B1–B8/DSA source/tests/lessons and genuine historical artifacts.
The pre-existing staged index is preserved except registering this new completed
report,as required by AGENTS.md. Final package creation requires it tracked and
unignored; the proof/sidecar record the actual tracking gate. No commit or push.

## 31. Dependencies

No installation/upgrade. Existing Python3.14.2,NumPy2.5.4,pytest9.1.1,PyYAML6.0.3,
SciPy1.18.1,scikit-learn1.8.0 and Apple Clang. B9 uses NumPy/stdlib/local source
only. Prior ML suites retain their existing dependencies. No NetworkX,Pytorch,
PyG,DGL,GPU,external dataset,pretrained embeddings or downloaded weights.
No unexpectedly global random-state mutation or unsafe serialization/network path.

## 32. Bugs discovered

B9-001: initial GCN development1 failed,42 passed because unfitted predict accessed
classes_ before validation. B9-002: initial infrastructure1 failed,11 passed due
to a missing optional metadata assumption in the generator. Additional scalar/
evidence/helper audit findings are recorded honestly in
[development findings](../../graph-learning-evidence/development-findings.json).
Original numbered failed and corrected command/JUnit/output files remain present.

## 33. Fixes applied

GCN predict now calls validated predict_proba before accessing fitted classes.
Generator only renders the approved DPO block with actual approval/report metadata.
Original failing tests are unchanged; corrected GCN43/infrastructure12 pass.
Unrepresentable scalar inputs raise documented ValueError. Runner sequence numbers
avoid existing JSON/TXT/XML evidence files. No old algorithm or test was rewritten,
no validator weakened,and no test threshold changed to conceal failure.
[Negative policy matrix](../../graph-learning-evidence/negative-validation-matrix.json).

## 34. Known limitations

Dense1..32-node educational graphs,not arbitrary web/network scale. Node2Vec and
GCN only support undirected zero-diagonal inputs. Fixed SGNS negatives/full-batch
steps may overfit one sample; isolated embeddings are untrained. Tanh GCN lacks
dropout/Adam/sparse acceleration and need not improve arbitrary tasks. Neither
learner claims general convergence; fixed budgets are exposed. PageRank numerical
bounds amplify roundoff near damping1. Training metrics on one tiny synthetic
graph do not prove generalization. No general performance superiority,heavy-library
reference run,hosted CI or other OS/Python/compiler-matrix result is claimed.

## 35. Unresolved blockers

No incomplete B9 algorithm or known failing final local test. B8 DPO remains
intentionally blocked with its canonical ID,path,four statuses,planning lesson,
research report and approved Outcome3 decision unchanged. B8 remains9 completed+
1 blocked,not10/10. No replacement or implementation is authorized.
Future DPO specification/correction needs separate explicit owner approval.
Phase21 owner review is still pending.

## 36. Reproduction commands

From repository root with existing requirements-ml-test.txt dependencies and a
C++17/C++20 compiler; use the local .venv when available:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest machine-learning/graph-learning -q
python -m pytest machine-learning/graph-learning -m oracle -q
python -m pytest machine-learning/graph-learning -m numerical -q
python -m pytest machine-learning/graph-learning -k finite_difference -q
python -m pytest machine-learning/graph-learning -k permutation -q
python -m pytest machine-learning/deep-learning/graph-neural-networks -q
python -m pytest tests/test_b9_language_and_scope_policy.py -q
python -m pytest --require-cpp
python scripts/verify_graph_learning_examples.py --check-only
python scripts/verify_graph_learning_scope.py --check-only
python scripts/evaluate_graph_learning.py
```

Exact bounded selectors,interpreters,seeds,commands,outputs,JUnit,dates and timings
are retained. Exported scope checking adds --source-only because .git and old
archives/sidecars are excluded. Prior phase-specific scope scripts target their
frozen snapshots and are not substituted for the current Phase21 gate.

## 37. Review package paths

Report: docs/reviews/graph-learning/GRAPH-LEARNING-REVIEW-REPORT.md.
[Package directory](../../../artifacts/review-packages/graph-learning/README.md):
algorithm-atlas-graph-learning-review.zip,
algorithm-atlas-graph-learning-review.zip.sha256,
algorithm-atlas-graph-learning-review.json.

The no-overwrite snapshot contains updated source,required reports,instructions,
B9/shared B7/earlier ML/DSA code/tests,catalog,dependencies,validators,generator and CI.
It excludes .git,environments,caches,binaries,secrets,datasets,weights and nested
historical archives/sidecars. CRC,safe unique regular paths,required files,UTF8/
credential scan,per-file manifest,SHA256 and JSON consistency are checked.
The actual ZIP extraction runs catalog/generated/scope/examples,B9,B7 GNN and full
required-C++ tests using existing external dependencies and empty PYTHONPATH.
Actual return codes/output are saved in external JSON after freeze; extraction
success is claimed only when that sidecar reports passed. Packaged source is not
rewritten recursively to embed its own final hash or later extraction outputs.

## 38. Owner approval

**Phase20 owner-approved. Phase21 owner approval pending.** All three defined B9
algorithms and internal batches are complete; full local mandatory checks passed.
Deliver the final verified report/ZIP/checksum/JSON,then STOP for owner review.
No Phase22,B10,other category,commit,push,tag,release,publication or Git identity change.
