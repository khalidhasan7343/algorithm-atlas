# Phase18 — B6 Association Rule Learning review

## 1. Phase identity and authorization

Algorithm Atlas, owner **MD.Khalid Hasan**, target
https://github.com/khalidhasan7343/algorithm-atlas, MIT. Client session date:
2026-10-30 Asia/Dhaka; actual command timestamps remain separate execution evidence.
Starting main at HEAD c5a334e7750b55d6955edb50ed440587e00309e7. The checkout contains
accepted Phase17 staged/unstaged/untracked changes, not a clean baseline. Captured
[baseline](../../association-rule-learning-evidence/baseline.json) preserves2373
working-tree hashes, initial status and exact staged-diff digest. The existing
staged Phase17 report must remain byte-identical.

Owner statement immediately after latest Phase17 handoff: “Approved pervious work
and review done.now follow this properly”. Its accepted ZIP SHA256 is
05cd7419f8e8fc938cf050996186125736df60acc84e6a3effe8f405d761b7b4; local SHA/CRC matched
and metadata records all five extracted-source checks passed, including3310 tests.
[Approval evidence](../../association-rule-learning-evidence/approval-evidence.json)
updates current Phase17 approval while preserving historical pending-at-handoff
reports/packages. Phase18 B6 only is authorized; new owner review remains pending.

## 2. B6 category identity

Machine Learning — Unsupervised Learning — **B6 Association Rule Learning**,
canonical category machine-learning/unsupervised-learning/association-rule-learning.
Initial discovery found exactly three catalog-owned records, each with only a
planning README and no implementation/tests. [Scope lock](../../association-rule-learning-scope.md).
No duplicate canonical, ID/path/member change or unrelated algorithm was added.

## 3. Exact inventory

| Batch | ID | Mechanism | Initial canonical tests |
| --- | --- | --- | ---: |
| 1 | apriori | Prefix joins, subset pruning, horizontal counts | 14 passed |
| 2 | eclat | Vertical TIDs and explicit depth-first intersections | 13 passed |
| 3 | fp-growth | Prefix tree and weighted conditional pattern growth | 16 passed |
| 4 | Shared rules utility | Complete count maps → rules; no new canonical | 29 passed |

Catalog batch_plan lists the three canonicals exactly once, as the existing
validator requires. Batch4 is separately mandatory in checkpoints, its own actual
execution record and phase_records.18.rule_generation_status=tested; the packager
requires all four gates. It is not fabricated as a fourth algorithm or omitted.

## 4. Canonical paths

All paths are beneath machine-learning/unsupervised-learning/association-rule-learning/:
apriori/, eclat/, fp-growth/, each with README.md, python/solution.py,
python/example.py and tests/test_python.py. Shared support.py/rules.py and category
contracts/cross-miner tests remain local to B6. Earlier B5/B7 autoencoder stays one
canonical in its approved original path; other B7 topics remain deferred.

## 5. Implementation status

All three miners are implemented/tested with full25-section lessons, examples and
independent mathematical verification. Optional C++ remains planned/absent without
placeholder files. Core uses stdlib sets, frozensets, tuples, dictionaries and integer
counts; NumPy conversions/frameworks are unnecessary and no external miner is called.
The same input/threshold/output contract supports honest exact map comparisons.
fit installs state only after a complete successful bounded search; a failed refit
preserves the prior successful state. Pure functional wrappers return count maps.

## 6. Apriori correctness

Initial gate14 passed. Tests check singleton counts, frequent pairs/triples, known
levels/candidate counts, matching sorted-prefix joins and pruning when an immediate
subset is missing. The core scans only candidates surviving anti-monotonic pruning;
it does not enumerate every subset and rename that procedure Apriori. A unique join
parent pair avoids duplicate patterns. Correctness follows because every frequent
(k+1)-set has all frequent k-subsets, while a missing subset proves infrequency.
Empty/single/dense/disjoint/duplicate data, threshold boundaries and direct-count
randomized/reference comparisons passed. Core and shared contract checks verify
work/candidate/output failure returns no partial map.

## 7. Eclat correctness

Initial gate13 passed. Stable IDs include empty rows and give duplicate transactions
distinct observation identities. Exact singleton TID sets and pair/triple intersections
are checked; randomized tests independently verify TID(A∪B)=TID(A)∩TID(B) from raw
row containment. Increasing-item equivalence classes enumerate each pattern once.
An explicit DFS stack keeps active prefix classes rather than using unbounded
recursion. It does not call Apriori. Vertical diagnostics, direct oracle counts,
independent sparse incidence, dense/sparse cases and atomic resource failure passed.

## 8. FP-Growth correctness

Initial gate16 passed. Tests verify root/parent/child insertion, root path weight,
shared prefix counts, header head/tail/next traversal without cycles, header frequency
sums and deterministic descending-frequency/ID tie order. Conditional bases retain
node multiplicities: [abc,abc,ab,ac,bc] yields c prefixes(ab,2),(a,1),(b,1), conditional
a3/b3 and ab2. Seven repeated abc rows contribute weight7 rather than one to its
conditional prefix. Original absolute minimum count is preserved across conditional
trees, not recomputed against a smaller denominator. Explicit stack frames implement
recursive pattern extension without Python recursion; no single-path shortcut claimed.
Complete patterns match raw-count oracles on known, empty, sparse, dense, repeated
and seeded databases. No Apriori delegation or candidate-generation substitute.

## 9. Support-count verification

Support counts are native positive integers. Relative support=count/N is distinct
from threshold/count. Empty rows remain in N; repeated row items count once;
repeated transactions count independently. Empty database returns{}, min_count1,
no division by zero. Nonempty itemsets only are returned; the theoretical empty
set would have countN and is intentionally omitted. Anti-monotonic counts are checked
on every nonempty immediate subset of all mined larger sets in the cross audit.

min_support is native float only in(0,1], always relative, never an absolute count.
Interpret Fraction(str(value)) exactly and compute ceil(fraction*N) using integers.
No comparison epsilon. Thus0.14 with N100 requires14, while its nextafter value above
0.14 intentionally requires15. Integer1 is rejected rather than silently changing
threshold type/meaning; pass1.0 for all transactions. Five targeted numerical tests
verify decimal support/confidence boundaries and empirical rule formulas.

## 10. Association rule verification

Shared rules.generate_rules is independent of all miners and adds no catalog entry.
For each union S, it streams every nonempty proper A and complementary B, validates
nonempty/disjoint sides, and computes support=count(S)/N,
confidence=count(S)/count(A), lift=N*count(S)/(count(A)*count(B)). Both directions
are emitted when eligible. Filtering uses decimal-exact rational cross multiplication;
metrics are floats only for presentation. Rule records are frozen and deterministically
sorted by antecedent size/IDs then consequent size/IDs.

All29 rule tests passed. The seven known frequent sets produce nine rules at
confidence0.6, six at0.75 and none above0.75; all12 directions appear at0.0.
a→b has support0.6, confidence0.75 and lift15/16; ab→c has support0.4,
confidence2/3 and lift5/6. Independent raw-row formulas and SciPy contingency
expectations verify these. Positive, independent and negative associations have
lift2,1,2/3 in controlled four-row examples. High confidence need not have high
lift; frequent patterns are not automatically interesting, and association is not
causation.

Invalid/missing subsets, zero/negative/non-integer/excess counts, invalid N and
confidence, mixed families and output/work limits fail explicitly. Count maps
must be downward closed with immediate-subset count monotonicity. This validates
necessary support properties, not general realizability by a database; mined maps
provide the intended provenance.

## 11. Cross-algorithm consistency

All three miners match the same independently computed exact map for each shared
hand-computed, exhaustive, seeded, dense/sparse and duplicate-heavy case. The
instruction's five-row bread/milk/diaper/beer/cola/eggs example is independently
checked at support0.6: four frequent singletons and four pairs; beer→diaper has
confidence1 and lift1.25. No miner is the sole expected-output oracle for another.
Duplicating a database doubles every integer count at the same relative threshold;
empty rows remain counted, and itemset presentation ordering is checked separately.
No map mismatch was found in the completed audit.

## 12. Independent brute-force oracle

Test-only tests/oracles.py enumerates nonempty subsets of at most8 distinct items,
counts direct containment in original transactions and applies the relative rational
threshold. It calls no core candidate join, TID, tree or threshold helper. A second
raw-row rule oracle recomputes antecedent/consequent/union counts independently.

All **51 oracle-marked tests passed**. The exhaustive tests visit all495 transaction
multisets of size0..4 drawn from eight possible three-item transactions, at support
0.25,0.5,1.0: **4455 exact miner-map comparisons**, not4455 pytest cases. Additional
reference checks use sklearn MultiLabelBinarizer/SciPy sparse incidence counts and
SciPy expected contingency frequencies for lift. All **7 reference-marked tests
passed**. No whole-miner third-party package was installed or falsely claimed run.
[Primary source retrieval](../../association-rule-learning-evidence/reference-sources.json)
records author papers/index and a direct Zaki PDF retrieval timeout; its bibliographic
entry is verified, not falsely claimed read in full. No external code/prose copied.

## 13. Randomized tests

All **18 named randomized tests passed /144 deselected**. Apriori seeds18001..18003,
Eclat18011..18013, FP-Growth18021..18023, rules18031..18034 and cross-miner
18041..18045. Shared densities0.15,0.5,0.85,0.35,0.7 cover sparse/dense regimes,
with repeated and empty rows included. Sparse reference comparisons also use18046.
Randomness generates deterministic test data only; core algorithms use no RNG.
Oracle/numerical/reference/randomized subsets overlap and are not added to the
full test total. Exhaustive loop comparisons and benchmark observations are
reported separately rather than inflating pytest counts.

## 14. Input validation

Outer data must be bounded list/tuple. Each row is list/tuple/set/frozenset with
homogeneous native int64 integers or nonempty native strings<=128 characters.
Reject bool,float,None,mixed families, empty/oversized string IDs, arbitrary/unhashable
objects, mappings, bare strings and generator inputs. N<=4096,U<=32, raw entries
per row<=128,total<=65536. Normalize to immutable sets, retaining empty rows.
max_patterns1..50000(default10000) bounds output and intermediate collections;
max_work1..5000000(default1000000) bounds explicitly charged operations. Excessive
32-item dense candidate/output spaces are tested to raise MiningLimitError without
partial state or recursion failure. Rule caps are validated separately.

## 15. Determinism and mutation checks

Explicit natural item sorting, frequency/ID tie order and final size/lexicographic
mapping order avoid dependence on hash iteration. Repeated transactions and input
row reversal yield identical maps. Input lists/sets remain unchanged after fit;
modifying caller inputs later does not alter fitted counts. Prior successful state
survives failed refits or mutated invalid parameters. All three CLIs are byte-equal
under PYTHONHASHSEED0,7,123, including rule outputs. Rule ordering is independent
of support-map insertion order; immutable sides/records prevent mutable-key bugs.
The core neither mutates nor uses global random state.

## 16. Complexity and performance review

Apriori: singleton scan O(N+M); level joins up to O(Lk²*k), subset checks up to
O(k²*Ck) and horizontal support scans O(N*k*Ck), summed over levels. Eclat: vertical
build O(N+M), then sum of expected O(min(|TA|,|TB|)) integer-set intersections over
explored extensions. FP-Growth: frequency/ordered insertion O(M log U), then
output/data-sensitive conditional tree/path work. All have exponential worst-case
frequent output; rules can approach3^U-2^(U+1)+1 directed disjoint assignments in a
fully frequent universe. Work/memory budgets do not change completeness: exceeding
a bound fails instead of claiming truncated success. Explicit stacks bound depth
by U<=32; tree/index/intermediate state and output have distinct memory costs.

[Executed benchmark](../../association-rule-learning-evidence/benchmark.json)
uses seeds18060..18062, N96,U8, support0.25, sparse/dense/shared-prefix regimes.
Each of nine fits matches an independent direct-count oracle. Result counts are
0,244,16 respectively for every miner. Times are actual single-run observations
with canonical imports excluded; they are not repeated estimates or a universal
speed ranking. Work units are conservative algorithm-specific counts, not comparable
CPU instructions. The original import-inclusive observation is retained as
benchmark-attempt1.json and its measurement correction is documented. Benchmarks
are separate from CI correctness discovery.

## 17. Documentation verification

Three complete lessons have exactly25 required numbered headings in order, with
algorithm-specific intuition/mechanism/proof/pseudocode, defined time/space variables,
worked counts and rules, validation strategies, edge/resource/numerical contracts,
selection tradeoffs, primary references and owner/MIT attribution. Section14 honestly
states optional C++ absent. Category navigation includes support/confidence/lift,
strategy comparison, data representation, commands, common mistakes and links.
Hand-written lessons are not overwritten by generation;136 managed pages check cleanly.

All **3 examples +3 equivalent CLIs +3 invalid CLIs +3 rule CLIs passed**.
[Inputs](../../association-rule-learning-evidence/example-inputs.json) and
[actual outputs](../../association-rule-learning-evidence/examples-results.json)
retain exact executed counts/rules. The verifier independently checks support/count/
confidence/lift from raw rows and exact fractions. Invalid CLIs exit2, stderr only.

## 18. Catalog validation

Catalog/link and generated documentation checks passed. Inventory remains
**35 categories /256 memberships /235 canonicals**, now **141 complete /94 remaining**
(93 planned,1 blocked DPO). Only three B6 statuses/notes and development approval/
checkpoint metadata change. IDs, canonical paths, memberships and out-of-scope
algorithm records remain identical. B6 owner approval stays pending.

All existing language/validator rules remain unchanged relative to the accepted
Phase17 working-tree baseline: B6 Python-only valid, DSA C++ mandatory, partial
optional C++ rejected, missing Python/tests, duplicate IDs, unsafe paths, missing
sections and generated drift rejected. [Negative-test mapping](../../association-rule-learning-evidence/negative-validation-matrix.json)
binds actual fixture tests to final execution. No production validator, track
policy, pytest settings, CI workflow or dependency manifest change was necessary.

## 19. B1–B5 regression

Baseline explicit gates passed **B1 281 /B2 398 /B3 253 /B4 206 /B5 162**.
Final explicit B1/B2/B3/B4/B5 gates also passed281/398/253/206/162;
the same groups are included in the final **3,472 passed** full run.
[Actual final evidence](../../association-rule-learning-evidence/final-results.json)
is new execution, not inference from old reports. B5 includes the one shared B7 autoencoder. All approved canonical
source/tests/lessons and previous reports/evidence/packages remain byte-identical.
No prior implementation defect was demonstrated, so none was rewritten. Current
Phase17 approval does not rewrite its historical pending-at-handoff artifacts.

## 20. DSA regression

Actual local full suite: **3,472 passed**, zero failures/errors/skips,
435.029 seconds. [JUnit-derived matrix](../../association-rule-learning-evidence/test-matrix.json):
B1 281, B2 398, B3 253,
B4 206, B5 162, B6 162,
DSA 1687 and infrastructure 323.
DSA Python/shared-oracle cases: **1149 passed**.
[Actual transcript](../../association-rule-learning-evidence/full-suite-attempt1.txt)
and [command records](../../association-rule-learning-evidence/final-results.json)
preserve interpreter, timestamp, environment, timeout, duration and exit status.
No existing DSA source/test/lesson or compiler fixture was altered.

## 21. C++17/C++20

Actual DSA compilation/execution: **269 C++17 passed** and
**269 C++20 passed**, included in the final required-C++ full run.
Available Apple Clang21 executed both standards through unchanged fixtures;
infrastructure compiler checks also passed. Absent optional ML C++ is not counted
as an execution pass or a skipped algorithm check.

## 22. CI-equivalent checks

Targeted B6 **162 passed**, with numerical5/oracle51/reference7/randomized18
passing overlapping subsets. Infrastructure **323 passed**. Catalog and generated
checks passed. Final local required-C++ suite **3,472 passed**, zero failures/errors/skips.
The actual exported ZIP is independently extracted/tested; actual post-creation
command outputs/return codes are recorded in external package JSON before delivery. Existing CI discovers tests recursively beneath
machine-learning without a custom import hook or config change. Hosted GitHub
Actions and other OS/Python/compiler matrices were **not run or verified**.
No workflow configuration is presented as hosted execution evidence.

## 23. Files created

Three Python solution/example/test sets; B6 support/conftest/rules, direct test
oracles and contract/cross-miner/rule tests; separate benchmark; phase scope,
contracts/checkpoints/execution evidence; validation/scope/example/package scripts;
this report and new artifact folder. [Changed-file inventory](../../association-rule-learning-evidence/changed-files.json)
compares the actual captured working-tree baseline, preserving its prior uncommitted
accepted Phase17 changes. No dataset/model/binary/temporary environment bundled.

## 24. Files modified

Three B6 planning READMEs, relevant catalog development/status/notes, current guides,
root README/roadmap/getting-started/glossary, generator/progress/index/category
navigation and review/package indexes. B1–B5 and DSA implementations/tests/lessons,
previous reports/evidence/packages, existing validator/track policy/requirements/
CI/conftest/pytest configuration are unchanged. [Preservation proof](../../association-rule-learning-evidence/preservation-results.json)
checks2321 protected existing files and preserves exact pre-existing staged diff
bytes while allowing only this new report to be staged. No destructive Git cleanup,
identity change, commit, push, tag, release or publication.

## 25. Dependencies

No installation, upgrade or new dependency. Existing Python3.14.2, NumPy2.5.4,
pytest9.1.1, sklearn1.8.0, SciPy1.18.1, PyYAML6.0.3 and Apple Clang21 toolchain.
Core B6 uses stdlib combinatorial data structures; NumPy/sklearn/SciPy are independent
test references only. The existing full-ML dev setup suffices, and DSA-only setup
remains unchanged. No heavy framework, hidden network call, downloaded dataset,
model checkpoint, pickle loader or credential.

## 26. Bugs discovered

[Findings](../../association-rule-learning-evidence/development-findings.json):
B6-001, a missing list bracket in a new invalid-input test caused collection to
stop with one SyntaxError in B6-attempt1. B6-002, initial benchmark timings included
first-import cost in the sparse regime. No confirmed mining/count/conditional
weight/rule formula defect or cross-algorithm mismatch was found. No prior approved
implementation required repair. Initial failed/output evidence is preserved.

## 27. Fixes applied

Corrected the test parametrization bracket without removing/changing expectations;
subsequent162-test run passed. Preloaded canonical classes outside benchmark timing
and reran the same seeded datasets; initial observation remains benchmark-attempt1.
Public max_rules validation now names the correct parameter in errors; valid
semantics did not change. No test weakening, skip filter, ignored failure or
fabricated passing outcome. Source/candidate/TID/tree/conditional/rule mechanisms
remain genuinely independent and are directly audited.

## 28. Known limitations

Bounded in-memory native-item binary transaction databases only. No arbitrary
hashable objects/mixed identifiers, weights, missing values, generator/streaming
input or absolute-support API. Decimal float threshold semantics are explicit,
including nextafter boundary differences; counts remain exact integers. Search,
intermediate state and output can be exponential; budgets are conservative work/
collection guards, not strict CPU/byte limits. Explicit limit errors mean a search
was not completed; no partial result is mislabeled successful.

Basic Apriori, set-based Eclat and FP-Growth only: no diffsets/bitmaps, closed/maximal
patterns, single-path shortcut, incremental/parallel/distributed mining or production
throughput guarantee. Mutable FP-tree diagnostics are inspectable internals, not an
incremental-update API. Rule maps validate necessary closure/count properties, not
general realizability; use mined maps. No leverage/conviction/lift-filter feature
is claimed. Association is empirical, not causation; single benchmarks establish
no universal performance ranking. No whole-miner third-party comparison or hosted
CI/platform/version matrix execution is claimed.

## 29. Unresolved blockers and unexecuted checks

No unresolved B6 implementation blocker. All final local mandatory checks passed. Actual extracted-ZIP outcomes are recorded in external JSON before delivery. Hosted GitHub Actions and other platform/version/compiler
matrices remain unexecuted/unverified. The direct Eclat author-PDF fetch timed out;
its metadata/code link was verified through the author index and this does not
replace an algorithm test. Existing DPO terminology ambiguity stays blocked and
unchanged outside B6. New Phase18 owner approval is pending; no next category.

## 30. Reproduction commands

From repository root with requirements-ml-test.txt and C++17/C++20 compiler:

```sh
python scripts/validate_catalog.py
python scripts/generate_catalog_docs.py --check
python -m pytest machine-learning/unsupervised-learning/association-rule-learning -q
python -m pytest machine-learning/unsupervised-learning/association-rule-learning -m oracle -q
python -m pytest machine-learning/unsupervised-learning/association-rule-learning -m numerical -q
python -m pytest machine-learning/unsupervised-learning/association-rule-learning -m reference -q
python -m pytest machine-learning/unsupervised-learning/association-rule-learning -k randomized -q
python -m pytest machine-learning/supervised-learning/regression -q
python -m pytest machine-learning/supervised-learning/classification -q
python -m pytest machine-learning/ensemble-methods -q
python -m pytest machine-learning/unsupervised-learning/clustering -q
python -m pytest machine-learning/unsupervised-learning/dimensionality-reduction machine-learning/deep-learning/vanilla-autoencoders -q
python -m pytest --require-cpp
python scripts/verify_association_rule_learning_scope.py --check-only
python scripts/verify_association_rule_learning_examples.py --check-only --rules
python machine-learning/unsupervised-learning/association-rule-learning/experiments/benchmark.py
```

In a source export add scope --source-only because .git and historical binary
archives/sidecars are intentionally absent. Old phase validators target their
frozen milestone; the current verifier checks preservation against the new baseline.
The runner records numbered attempts, actual command/interpreter, timestamp,
timeout, environment, duration, exit code and output. No automatic installer.

## 31. Review package details

Directory artifacts/review-packages/association-rule-learning/ contains
algorithm-atlas-association-rule-learning-review.zip,
algorithm-atlas-association-rule-learning-review.zip.sha256 and
algorithm-atlas-association-rule-learning-review.json. Report:
docs/reviews/association-rule-learning/ASSOCIATION-RULE-LEARNING-REVIEW-REPORT.md.

The no-overwrite packager includes the updated repository source/tests/docs and
required reports, relevant prior ML/DSA, catalog/configuration and new evidence.
It excludes .git, environments/caches, binaries, secrets/models/large data and
nested historical ZIP/checksum/JSON sidecars. Previous artifact bytes are untouched.
It checks safe unique regular paths, required files, UTF8/credential patterns, CRC,
SHA256/per-file manifest and source-byte consistency. The **actual ZIP** is extracted
to an independent temporary directory and catalog/generated/scope/example/full
--require-cpp checks execute with the existing external installed interpreter and
no inherited PYTHONPATH. Actual post-freeze outputs/statuses go in external JSON,
avoiding recursive hashes or rewriting a frozen archive. Source/hash consistency
is rechecked after execution. No unexecuted check is claimed passed.

## 32. Owner approval status

**Latest Phase17 and earlier work approved. New Phase18 B6 review: pending.**
STOP after verified report/ZIP/checksum/JSON delivery for explicit owner review.
No Phase19/B7/other category, commit, push, tag, release or publication.
