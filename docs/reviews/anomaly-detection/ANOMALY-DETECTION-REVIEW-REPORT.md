# Phase24 — B12 Anomaly Detection review report

**Three existing canonicals implemented;three internal batches complete;Phase24 owner approval pending.** Owner/maintainer: **MD.Khalid Hasan**. Repository:`https://github.com/khalidhasan7343/algorithm-atlas`. MIT attribution/licensing preserved. Client session date:**2026-11-01 Asia/Dhaka**.

## 1. Phase identity

The owner explicitly approved the verified Phase23 handoff with “Approved pervious work and review done.now follow this properly.” and supplied the Phase24 master prompt;subsequent “continue” messages preserve that scope. [Approval evidence](../../anomaly-detection-evidence/approval-evidence.json) records the actual statement and accepted SHA-256 `a58f53ab107411876db7827d43ca034ae31598d6846991757286a495d8c6122e`. The accepted ZIP/checksum/JSON,CRC,required files,six B11 statuses and nine successful extraction checks were verified. Its final extraction passed4,538 tests. Current catalog records subsequent owner approval;historical report/package bytes retain handoff-time states. HEAD remains `7202b5736cb657cbc84e8b33bec63b0a5e5d9a0c` on `main`. No commit,push,tag,release,publication or Phase25 work is authorized/performed.

## 2. Category identity

B12 is **Anomaly Detection**,canonical root `machine-learning/anomaly-detection`. The [locked scope](../../anomaly-detection-scope.md),[exact mathematical/API contracts](../../anomaly-detection-conventions.md) and [checkpoint record](../../anomaly-detection-checkpoints.md) derive from the authoritative catalog. The [owner attachment](../../anomaly-detection-evidence/phase24-request.md) and [baseline catalog](../../anomaly-detection-evidence/catalog-baseline.yaml) are preserved. No current inventory discrepancy was found.

## 3. Three-algorithm inventory

Exactly Isolation Forest,One-Class SVM and Local Outlier Factor,each with its original B12-only membership. Batch1:isolation;Batch2:kernel support;Batch3:local density. No new canonical,rename,path change,shared-membership change or syllabus expansion. Inventory remains35 categories/256 memberships/235 canonicals. Implementation completion is185/235;49 remain planned and DPO remains intentionally blocked. B12 completion is3/3;zero incomplete/blocked B12 algorithms. Owner approval and full catalog completion remain separate.

## 4. Canonical paths

All three exact canonical paths,source/test pointers and implemented lessons are below. Every folder contains its own solution,executable example,meaningful tests and full25-section lesson. Shared B12 support centralizes validated contracts and metrics rather than hiding the three different detector mechanisms.

| Algorithm | Canonical path | Implementation | Tests | Oracle | Documentation | Status |
|---|---|---|---|---|---|---|
| isolation-forest | `machine-learning/anomaly-detection/isolation-forest` | [Python/NumPy](../../../machine-learning/anomaly-detection/isolation-forest/python/solution.py) | [37 passed](../../../machine-learning/anomaly-detection/isolation-forest/tests/test_python.py) | Independent;passed | [25 sections](../../../machine-learning/anomaly-detection/isolation-forest/README.md) | Complete |
| one-class-svm | `machine-learning/anomaly-detection/one-class-svm` | [Python/NumPy](../../../machine-learning/anomaly-detection/one-class-svm/python/solution.py) | [41 passed](../../../machine-learning/anomaly-detection/one-class-svm/tests/test_python.py) | Independent;passed | [25 sections](../../../machine-learning/anomaly-detection/one-class-svm/README.md) | Complete |
| local-outlier-factor | `machine-learning/anomaly-detection/local-outlier-factor` | [Python/NumPy](../../../machine-learning/anomaly-detection/local-outlier-factor/python/solution.py) | [28 passed](../../../machine-learning/anomaly-detection/local-outlier-factor/tests/test_python.py) | Independent;passed | [25 sections](../../../machine-learning/anomaly-detection/local-outlier-factor/README.md) | Complete |

## 5. Existing versus new implementations

All three began with planning-only READMEs and planned documentation/Python/C++/test statuses. Three solutions,three executable examples,three canonical test modules,B12 support/conftest,shared tests,16 policy cases and three exact25-section lessons are new. Canonical tests total106;74 shared cases give180 B12 tests. ML C++ remains optional/planned and no fake C++ files were created. All prior B1–B11/DSA source/tests/lessons and historical reports/evidence/packages remain unchanged. No detector delegates to sklearn/SciPy;these libraries are independent test references only.

## 6. Isolation Forest mathematical correctness

Random no-replacement subsampling and actual randomized axis-aligned isolation trees produce corrected path lengths. Raw paper score is2**(-mean_corrected_path/c(psi)),not a distance threshold or supervised tree score. Finite harmonic sums define normalization and leaf corrections;c(0)=c(1)=0,c(2)=1. psi1 has no isolation normalization and is explicitly neutral.5 for every supported query.37 canonical tests passed,including exact/independent calculations and fixed-seed isolated-point ranking.

## 7. Isolation tree correctness

Each tree selects uniformly from currently varying features,draws a uniform observed-range split and routes x<split left. A minimal next-float repair handles rounded endpoints while guaranteeing two nonempty branches. Stop at bounded depth,singleton or all-constant node. Frozen diagnostics retain node counts,depth,split and children;sample indices verify no replacement. Default depth isceil(log2 psi);explicit0..32 is supported. Tests verify sample-count conservation,constant-feature exclusion,depth limits,adjacent/tiny float splits and meaningful repeatability. Eight selected tree tests passed.

## 8. Path-length oracle verification

Two selected path/ensemble oracle cases independently traverse manually specified nodes or fitted trees and calculate exact rational harmonic corrections. Seven harmonic cases cover0,1,2,3,4,17,256 without reusing the production correction as the expected value. The manual tree gives corrected paths2,2,3;ensemble checks average paths before exponentiation. sklearn random forests need not be bitwise-equivalent because random streams,nonconstant-feature conventions and harmonic approximations differ.

## 9. One-Class SVM mathematical correctness

The genuine RBF dual minimizes.5*alpha.T*K*alpha subjectsum(alpha)=1 and0<=alpha<=C=1/(nu*n). Uniform feasible initialization comes from a real capped-simplex projection. The learned decision is K(query,training)*alpha-rho. This is not a binary classifier,mean-distance rule,kernel-density estimator or unconstrained optimizer substitute.41 canonical tests passed,including analytical solutions,SciPy constrained optimization and correctly scaled sklearn comparisons.

## 10. Dual optimization verification

The bounded solver increases a minimum-gradient non-capped coordinate and decreases a maximum-gradient positive coordinate. Its exact bounded pair-line minimizer uses curvatureKii+Kjj-2Kij;pair mass is preserved and box/equality feasibility is checked after every update. Gradients are periodically recomputed and final certificates use a fresh gradient. Every numerical objective/feasibility history remains inspectable. max_iter1..20000 and n*max_iter<=3e6 are explicit caps. Twelve projection cases verify monotone-root Euclidean projection against exhaustive independent face minimization and invalid domains. No clip-and-renormalize shortcut is used. Ten selected dual cases passed.

## 11. KKT condition verification

For g=Kalpha,KKT requires g>=rho at zero coefficients,g<=rho at capped coefficients,and g=rho for free coefficients. Rho averages free values or uses the justified interval[max(g at cap),min(g at zero)]. At nu1 the feasible set is the uniform singleton and the finite valid endpoint rho=max(g) is used. Tests cover both finite no-free intervals and the half-infinite endpoint. Five selected KKT/rho cases passed,alongside analytical symmetric/feasibility cases. Pair gap and rho residual must meet tolerance before converged=True;budget,stagnation and certificate-not-met statuses remain distinct. Actual primal,dual and gap are reported separately;approximate KKT stopping does not claim exact optimality or unique supports.

## 12. Kernel correctness

RBF-only kernel exp(-gamma*||x-z||²),with gammaNone=1/d or explicit1e-12..1e12. The unchanged approved B1 SVR blocked direct-difference helper avoids catastrophic norm-expansion cancellation. Three selected kernel cases check hand Gram entries,symmetry,unit diagonal and PSD eigenvalue tolerance;shared compatibility tests verify large-offset distances/kernel values independently. Tail underflow to0 and subresolution distances rounding toward kernel1 are declared float64 behavior. No arbitrary custom kernel or unsupported linear/polynomial option is claimed.

## 13. LOF mathematical correctness

Genuine Euclidean LOF forms k-distances,tie-inclusive other-row neighborhoods,neighbor-based reachability,mean reachability and local density ratios. It is not average neighbor distance or global density. The score is mean(lrd_neighbor/lrd_self),equivalently mean(mean_reach_self/mean_reach_neighbor).28 canonical tests passed. Values below1 are possible and values above1 are not automatically anomalies. Original-paper distinct-point assumptions and the declared duplicate extension are separated in [the source ledger](../../anomaly-detection-evidence/reference-sources.json).

## 14. Neighborhood verification

Exclude only the identical row index;duplicate rows remain legitimate neighbors. Every distance<=the kth other-row distance is included,so cardinality can exceed k. Six selected neighbor cases passed. The independent four-point witness[-11,-10,0,10],k1 gives center neighbors-10 and10 and LOF5.5;fixed-k truncation could give a different result. Tests verify exact pair distances,k-distances,full member sets,small datasets and permutation/translation/scale behavior under the stated numerical assumptions.

## 15. Reachability density verification

Reachability uses the neighbor k-distance,max(kdist_neighbor,distance),not the point's own radius. Thirteen selected density/numerical cases passed. Scaled log means and log-mean-exp ratios preserve tiny-scale behavior even when a displayed ordinary lrd overflows. Exact-zero flags distinguish structural zeros from representation overflow. Our duplicate convention is the uniform mean-reach+epsilon limit:zero-reach duplicate piles have LOF1;positive reach with a zero-reach neighbor has genuine+infinity. Finite but unrepresentable LOF raises NumericalError. No arbitrary density epsilon,extreme finite placeholder or uncontrolled infinity/infinity NaN is used.

## 16. Score orientation verification

All predictors use+1 inlier/-1 outlier;decision>=0 includes the boundary as an inlier. IF raw anomaly is the positive paper score and score_samples is negative. SVM score_samples is kernel normalityg,raw anomaly=-g and decision=g-rho;only roundoff-sized boundary differences become zero. LOF raw anomaly is its ratio and score_samples is its negative. Shared tests verify conversions,labels and evaluation orientation. Thirty-one selected score/calibration cases passed,overlapping other selections. Raw values are not calibrated probabilities.

## 17. Threshold verification

IF auto threshold.5 and LOF auto1.5 are explicit heuristics layered on the mathematical raw scores. Numeric contamination selects a training-score linear quantile at1-fraction,position(n-1)*q. Exact endpoints and ties are tested independently. Positive weight on an infinite upper endpoint yields+infinity;finite score versus infinite threshold gives decision+infinity,infinite/infinite boundary gives0,and infinite score versus finite threshold gives-infinity. This controls the extended cases without NaNs or fake finite raw values. SVM threshold=-rho follows the dual certificate rather than a quantile.

## 18. Contamination handling

IF/LOF accept auto or a finite fraction in(0,.5]. Strictly larger raw scores are outliers and boundary ties remain inliers;therefore the model does not force a requested count. Tests cover tiny positive fractions,.1,.5,identical scores and infinite-score boundaries. Query predictions do not recalibrate training thresholds. SVM nu affects its dual cap/support model and is not silently replaced with a contamination label quota. Contamination assumptions do not establish the true anomaly rate.

## 19. Outlier versus novelty semantics

IF and SVM expose new-query score/decision/prediction interfaces with fitted feature validation and owned outputs. LOF here is explicitly training-set outlier detection;its no-argument methods return training scores and passing any query X raises ValueError. It does not concatenate unseen points into the reference set and pretend the model is unchanged. Evaluations distinguish held-out novelty(IF/SVM) from training-set detection(LOF);their metrics are not presented as directly interchangeable.

## 20. Independent oracle results

45 oracle-marked tests passed. Independent expectations include rational harmonic sums,manual trees,independent traversal,exhaustive small capped-simplex face minimization,analytical dual optima,independent KKT/primal-dual formulas,SciPy SLSQP,explicit scalar Euclidean/neighbor/reachability/LOF calculations and tied-score metrics. Library references align assumptions:IF ranking rather than identical random trees;normalized SVM decisions divide LIBSVM scaling bynu*n;LOF comparisons require unique kth distances and ordinary scales because sklearn uses fixed-k neighbors and a1e-10 stabilizer. Nonunique support sets are not required to match.

## 21. Numerical stability

Thirteen numerical selections passed. Finite input/shape/domain validation,nonempty random splits,exact small-count normalization,large-offset stable kernels,RBF tail underflow,PSD tolerance,per-step dual feasibility,no-free rho,tiny-scale log densities,structural infinite LOF and explicit finite-score overflow errors are covered. Positive density overflow is exposed by dedicated flags/log diagnostics rather than silently hidden. Computation bounds prevent excessive tree recursion/Gram/pairwise allocation. No NaNs are imputed or invalid numerics silently replaced with convenient values.

## 22. Reproducibility

Seven selected reproducibility/permutation cases passed. IF uses a private configured NumPy generator restarted on fit;SVM/LOF are deterministic for fixed data/tolerances. An autouse global RNG guard remains strict for production. The only corrected harness issue was an external sklearn SVM wrapper consuming a seed;only that external reference call saves/restores the global state. Fixed seeds,thread caps and hash seed are in actual command metadata. Exact IF invariance under arbitrary row/feature permutations is not claimed;random sampling/axis partitions can change.

## 23. Synthetic anomaly tests

25 selected synthetic/reference cases passed. Tests include Gaussian/uniform-style inputs,different local densities,isolated points,duplicates,constant columns,high dimensions and numerical extremes. [The executed study](../../anomaly-detection-evidence/educational-training-results.json) retains all36 method/case/seed records:three seeds,four declared generators,three methods. Training includes60 inliers+6 far anomalies;IF/SVM evaluate independent30+4 queries,while LOF evaluates its training set. The far six-point anomaly cluster can be locally dense:LOF recall is0 in these declared study cases. That observed masking limitation is retained rather than cherry-picked or disguised as algorithm correctness. No universal ranking/accuracy/superiority claim.

## 24. Evaluation metrics

Independent sklearn metric comparisons agree for tied scores. Positive evaluation class is anomaly label-1;confusion rows/columns are inlier then anomaly. Precision/recall are None for their zero denominators;F1 uses2TP/(2TP+FP+FN),orNone for its zero denominator. ROC-AUC gives half credit to ties and is None on a single class. Average precision is a tied-group step integral,not trapezoidal PR-AUC;no-positive sets returnNone. Controlled positive-infinite raw scores are explicitly rankable. Empty/mismatched/nonfinite/invalid labels fail. Evaluation labels never enter unsupervised fitting objectives.

## 25. Edge-case tests

92 selected edge cases passed:empty/malformed/nonfinite/boolean/object/high-magnitude features;dimension/resource bounds;unfitted calls;duplicates/identical/singleton data;constant columns;invalid hyperparameters;projection feasibility;nu endpoints;no-free rho;maximum iteration exits;unsupported LOF novelty;infinite-density ties and failed-refit atomicity. Shared tests exercise every detector input/ownership contract,not only one implementation. Sixteen negative infrastructure cases reject missing required artifacts,invalid IDs/duplicate paths,missing sections,documentation drift,partial optional C++ and missing mandatory DSA/unrelated-AI C++;they also verify CI discovery and retained blocked DPO policy.

## 26. Educational examples

All three real examples execute locally without network access and match captured lesson outputs. IF prints training coordinates,actual random root splits,scores,cutoff and labels. SVM prints kernel/nu,genuine optimizer status,coefficients/support,rho,KKT/feasibility diagnostics and unseen-query decisions. LOF prints training points,exact neighborhoods,k-distances,reachability densities,ratios and labels. [Example evidence](../../anomaly-detection-evidence/examples-results.json) records actual commands/outputs;no fabricated hardcoded score replaces computation.

## 27. Documentation validation

Three exact25-section implemented lessons give75 required B12 sections. Each includes assumptions,mechanisms,mathematics,pseudocode,correctness/dry runs,complexity,numerics,actual examples,source/test pointers,limitations and references. The category overview explicitly covers all15 requested topics:unsupervised scope,outlier/novelty,isolation/kernel/density methods,score orientation,thresholds,contamination,comparison,numerics,complexity,examples,evaluation and canonical links. Generator manages92 remaining index/planning pages without overwriting authored lessons. Catalog currently scans426 Markdown files;exact final link counts and zero-drift output are in [configuration evidence](../../anomaly-detection-evidence/configuration-results.json).

## 28. Catalog validation

`validate_catalog.py` and `generate_catalog_docs.py --check` pass. Schema/project/categories/IDs/paths/order/memberships remain unchanged. Only B12 completion fields/notes and authorized current development/checkpoint metadata changed. Phase23 records actual owner approval/accepted digest. Phase24 is awaiting-review,completed batches1–3,active batch null,owner approval pending. All B12 documentation is implemented,Python/tests tested,C++ planned(optional). DPO retains its ID/path,four blocked statuses,owner-approved remain-blocked decision and research. The global catalog remains185/235 complete.

## 29. B1–B11 regression results

Fresh targeted prior-category runs all passed:

| Category | Passed | Failed/errors | Skipped |
|---|---|---|---|
| B1 | 281 | 0 | 0 |
| B2 | 398 | 0 | 0 |
| B3 | 253 | 0 | 0 |
| B4 | 206 | 0 | 0 |
| B5 | 162 | 0 | 0 |
| B6 | 162 | 0 | 0 |
| B7 | 221 | 0 | 0 |
| B8 | 141 | 0 | 0 |
| B9 | 146 | 0 | 0 |
| B10 | 259 | 0 | 0 |
| B11 | 250 | 0 | 0 |

B5's162 includes145 folder cases and17 shared vanilla-autoencoder cases also included under B7. These targeted runs overlap and must not be summed as a unique total. The full matrix counts that canonical once. Approved distance/kernel/optimizer/forecasting sources remain byte-identical.

## 30. DSA regression results

The fresh full local suite passed **4,734 unique tests**,including **1,687 DSA cases**:1,149 Python/shared plus538 actual C++ cases. Final failures/errors/skips are0. [The full matrix](../../anomaly-detection-evidence/test-matrix.json) and [raw final command metadata](../../anomaly-detection-evidence/final-results.json) retain exact groups,timings,stdout and JUnit evidence. Prior DSA bodies/tests are unchanged.

## 31. C++17/C++20 results

**269 C++17 and269 C++20 cases passed** with the available Apple Clang toolchain and `--require-cpp`;no missing-compiler skip was accepted. Root compiler policy,workflow and DSA source/test bytes remain unchanged. B12 has no mandatory C++ and none was fabricated. Other platforms/compilers were not executed.

## 32. CI-equivalent checks

Catalog/generated checks,180 B12 tests,16 new policy cases,all B1–B11 targets,independent mathematical selections and the C++-required full suite passed. Unique full groups are405 infrastructure+1,687 DSA+2,642 ML=4,734. Selected audits overlap:

| Selection | Passed | Failed/errors | Skipped |
|---|---|---|---|
| isolation-trees | 8 | 0 | 0 |
| path-oracles | 2 | 0 | 0 |
| harmonic | 7 | 0 | 0 |
| kernel | 3 | 0 | 0 |
| dual | 10 | 0 | 0 |
| projection | 12 | 0 | 0 |
| kkt | 5 | 0 | 0 |
| lof-neighbors | 6 | 0 | 0 |
| density | 13 | 0 | 0 |
| scores | 31 | 0 | 0 |
| numerical | 13 | 0 | 0 |
| reproducibility | 7 | 0 | 0 |
| edge-cases | 92 | 0 | 0 |
| synthetic | 25 | 0 | 0 |
| oracle | 45 | 0 | 0 |

The unchanged workflow discovers all three B12 modules. Hosted GitHub Actions was not executed/verified. Post-freeze source extraction executes catalog/generator/scope/examples,B12,B11,B10,B9,shared GNN and the full C++-required suite. The external package JSON records those actual post-freeze checks;this immutable report does not invent future extraction results.

## 33. Shared utility compatibility

Reuse unchanged B4/B2 feature validation/stable distances and the B1 SVR blocked direct-difference RBF helper. Compatibility tests compare these computations with independent hand distances/kernels at large offsets. Signed-zero-sum SVR/B2 projections are not a capped simplex,and unconstrained B10 L-BFGS is not used to fake a constrained dual. Supervised CART is not used for isolation trees. New threshold/metric/projection/density logic has dedicated tests. Preservation audit protects3,465 pre-existing files,including all prior algorithm/test/lesson/report/package/dependency/CI bytes outside explicitly authorized live navigation. [Preservation evidence](../../anomaly-detection-evidence/preservation-results.json) records the proof.

## 34. Files created

Three canonical solutions,examples and test modules;B12 support/conftest;shared contracts/metrics tests;16-case policy tests;scope/contracts/checkpoints;this report;evidence;and five command/evaluation/verification/packaging scripts are new. [The baseline-relative inventory](../../anomaly-detection-evidence/changed-files.json) lists every created path and all evidence. Review ZIP/checksum/JSON are generated after source freeze and listed separately in section42/the external manifest.

## 35. Files modified

Three planning lessons became completed lessons. Authorized catalog/development metadata,AGENTS/CONTRIBUTING/development policies,live README/progress/roadmap/index/review/category navigation and the documentation generator were updated. No prior detector/ML/DSA source,test,lesson or historical report was overwritten. Validator,track policy,root conftest,dependencies and hosted workflow remain baseline-identical. Existing staged work is preserved;only this complete report is added to meet tracked/unignored requirements. Changed-file inventory compares the already-dirty phase-start snapshot rather than misattributing all HEAD differences to this phase.

## 36. Dependencies

No dependency installation or manifest changes. Runtime uses Python,NumPy,stdlib and unchanged local approved helpers. sklearn1.8.0 and SciPy1.18.1 are existing independent test references only,not core model delegates. Baseline records Python3.14.2,NumPy2.5.4,pytest9.1.1 and Apple Clang21. No external dataset,model weights,GPU,framework download,unsafe serialization or network runtime service. Extraction reuses the known installed interpreter/dependencies and does not bundle a virtual environment.

## 37. Bugs discovered

The first SVM development run passed all41 test bodies but raised **3 teardown errors** because the sklearn/LIBSVM reference wrapper consumed a legacy global NumPy seed. The strict production RNG guard exposed this harness side effect. Raw `batch2-development-01` output/JUnit and [findings](../../anomaly-detection-evidence/development-findings.json) preserve the failed attempt. No prior algorithm defect or production detector defect was required to be changed;edge-case conventions were specified and tested explicitly rather than hidden.

## 38. Fixes applied

Save/restore global RNG only around the external sklearn SVM call;leave production calls outside that protected scope and keep the guard unchanged. Mathematical oracle tolerances,feasibility/KKT assertions,reference comparisons and validators were not weakened. Corrected `batch2-development-02` and batch2 gate each passed41 cases with zero errors/skips. Integrated180-case B12 and full4,734-case regression pass. No unexecuted or failed check is relabeled as successful.

## 39. Known limitations

Educational bounds:n<=256,d<=32,query<=1024,feature magnitude<=1e12;IF<=128 trees,subsample<=256,depth<=32;SVM nu>=1e-4,RBF-only,max_iter<=20000,n*iterations<=3e6;LOF k<=n-1 and dense n² storage. No implicit imputation/scaling or custom kernels. IF axis/randomization choices and exact harmonic correction differ from libraries. Approximate SVM KKT stopping is not exact optimality;nonunique supports and nu1 boundaries require careful comparison. LOF is training-only,tie-inclusive and uses a declared duplicate-limit extension;infinite raw scores/thresholds are controlled,while finite unrepresentable ratios fail explicitly. Dense anomaly clusters may be locally normal,as retained study results show. No calibrated anomaly probabilities,universal ranking/accuracy,true contamination rate or performance superiority. Single-platform local execution is not hosted CI evidence.

## 40. Unresolved blockers

No B12 implementation/specification blocker remains. All3 canonicals are implemented,tested and documented;new Phase24 owner review remains pending. **B8 Dynamic Policy Optimization remains owner-approved: remain blocked** with unchanged canonical identity,path,four statuses,research and decision;no substitute or implementation is authorized. Overall catalog completion is185/235. No Phase25/other category or publication authorization is inferred from implementation/test success.

## 41. Exact reproduction commands

From repository root with the existing local virtual environment:

```sh
.venv/bin/python scripts/validate_catalog.py
.venv/bin/python scripts/generate_catalog_docs.py --check
.venv/bin/python scripts/verify_anomaly_detection_scope.py --require-tracked --check-only
.venv/bin/python scripts/verify_anomaly_detection_examples.py --check-only
.venv/bin/python -m pytest machine-learning/anomaly-detection -q
.venv/bin/python -m pytest tests/test_b12_language_and_scope_policy.py -q
.venv/bin/python -m pytest machine-learning/anomaly-detection -m oracle -q
.venv/bin/python -m pytest machine-learning/anomaly-detection -m numerical -q
.venv/bin/python -m pytest --require-cpp -q
```

Exact selected `-k` commands,timestamps,environment,output and JUnit are retained in final-results.json/raw evidence. An extracted source tree intentionally omits Git;use `verify_anomaly_detection_scope.py --source-only --check-only` and an installed interpreter there. Evaluation intentionally rewrites only its generated study JSON when rerun;use captured results during frozen-source verification. Packaging refuses to overwrite genuine artifacts;rebuilding requires a separately authorized fresh output location rather than deleting historical evidence.

## 42. Review package paths

ZIP:`artifacts/review-packages/anomaly-detection/algorithm-atlas-anomaly-detection-review.zip`;checksum:`artifacts/review-packages/anomaly-detection/algorithm-atlas-anomaly-detection-review.zip.sha256`;JSON:`artifacts/review-packages/anomaly-detection/algorithm-atlas-anomaly-detection-review.json`. [Package notes](../../../artifacts/review-packages/anomaly-detection/README.md). Updated source,required reports,tests,docs,configuration and evidence are included. Git,environments,caches,binaries,secrets,large data/weights,temporary files and nested historical archives/sidecars are excluded. Genuine old packages remain unchanged outside the source export;historical reports/execution evidence remain included. External metadata records the exact frozen file hashes,required-file checks,CRC/path/credential/checksum/manifest proof and actual extraction executions after freeze. This report does not claim a future export result or embed a self-referential ZIP digest.

## 43. Owner approval: pending

**Phase24 owner approval is pending.** Three B12 implementations and three internal gates are complete. Deliver the verified report/package and stop for MD.Khalid Hasan's review. Do not begin Phase25,another category,commit,push,tag,release,publish or change DPO without explicit owner authorization.
