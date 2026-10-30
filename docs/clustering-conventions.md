# Phase 16 — Clustering API and numerical contracts

Owner **MD.Khalid Hasan** · [MIT](../LICENSE). [Scope](clustering-scope.md) and
[actual stage gates](clustering-checkpoints.md) determine completion. This document
records the implemented interfaces; completion is recorded only after actual code,
tests, exact lessons and examples pass. Current Phase 16 owner
review approval remains pending. Prior implementations/evidence are preserved.

## Arrays, state and randomness

Numeric X is dense real (n,p), finite and magnitude<=10^12, excluding boolean,
complex, string and object arrays. Fitting is nonempty, normally n<=512,p<=32;
hierarchy methods use n<=128, HDBSCAN/spectral n<=256. Prediction, where meaningful,
permits 0..4096 rows with fitted p. Ambiguous 1D input is rejected, never reshaped.
Models consume no target y or sample weights. Caller arrays/global RNG state are
unchanged. Random seeds are native integers 0..2^32-1 and use local default_rng.
Cross-version bitwise RNG/eigensolver identity is not promised. Fits build local
state and publish only after success; a failed refit preserves the previous model.

All models provide fit(X) and fit_predict(X). Only K-Means, Mean Shift and GMM
provide meaningful new-row prediction. GMM probabilities are component
responsibilities, not supervised class probabilities. Hierarchies, DBSCAN,
HDBSCAN and spectral clustering are transductive and expose their fitted labels,
not an invented nearest-centroid classifier. Cluster IDs have no class semantics;
use label-permutation-invariant comparisons. Exact tied distances can depend on
row-derived ordering. Numerical/oracle/reference selections overlap.

## Stage 1 — centroid and merging procedures

KMeans: n_clusters=8 (1..min(n,64)), init='k-means++' or 'random' or an explicit
(K,p) center matrix; n_init=10 (1..16), max_iter=300 (1..1000), random_state=0.
Explicit centers require n_init=1. There must be at least K distinct observed rows.
Lloyd fitting uses a single uniform translation/scale and strict assignment fixed
points; it has no tolerance-based partial-convergence return. Empty clusters are
repaired by moving the first farthest eligible row from a nonsingleton group.
No converged initialization raises ConvergenceError. Physical inertia can underflow
to zero while normalized inertia is positive; that never controls convergence.
Transform returns original-unit Euclidean center distances and score their negative
squared sum. Offset/scaled-center storage avoids rounding a small centroid shift
away around a large common offset. No global optimum is claimed.

AgglomerativeClustering: n_clusters=2 (1..n), linkage='ward', or single/complete/
average. Dense Euclidean distance and full n-1 merges, including after the requested
cut. Ward height=sqrt(2*nA*nB/(nA+nB))*||meanA-meanB||; this avoids squaring tiny
heights before split comparisons. Equal costs use (height,left_ID,right_ID).
Labels are ordered by each cut group's smallest original row index. Singletons
and zero-distance duplicates are supported. Greedy hierarchies are not global
partition optima; naive construction is deliberately bounded to 128 observations.

## Stages 2 and 3 — division, density and modes

DivisiveClustering(n_clusters=2): native K 1..n with n<=128,p<=32. Full DIANA
hierarchy; largest-diameter group, greatest average-distance seed, positive
splinter moves with a 32*eps*diameter resolution guard. No bisecting K-Means.
DBSCAN(eps=.5,min_samples=5): real eps (0,10^12], native support 1..512, self
included. Core-only queue expansion, first-reached ambiguous border, -1 noise;
min_samples>n means all noise. Neither transductive method invents new-row prediction.

HDBSCAN(min_cluster_size=5,min_samples=None): n 2..256,p<=32, minimum size 2..n,
self-inclusive support 1..n, default size. Exact mutual-reachability/Prim MST/
condensation/EOM, Euclidean alpha=1, root always excluded. Condensed lambda is
max_pairwise_distance/height; this common positive scaling preserves finite EOM
selection and membership ratios, and handles uniform tiny units. Finite relative
density above 10^300 is rejected. Zero-height edges have infinite density; equal
infinite endpoints have zero lifetime, other infinite departures have infinite
persistence, EOM infinity ties favor an eligible parent. Selected-cluster membership
strength is exit/max-exit, with inf/inf=1 and finite/inf=0. These are strengths, not
class posteriors. All-noise is valid when no nonroot branch qualifies. Full lesson
lists retained MST, hierarchy, condensed and stability diagnostics. No out-of-sample
prediction, GLOSH, leaf/epsilon selector or arbitrary metric is implemented.

MeanShift(bandwidth=1,max_iter=300,tol=1e-3,cluster_all=True): finite positive bandwidth
<=10^12, native max_iter 1..1000, tol in (0,1] relative to bandwidth, native bool.
Every-row flat-kernel seeds; any unfinished seed fails. Modes are suppressed in
descending support/descending coordinate order; nearest retained mode predicts
new rows, optionally -1 beyond fitted bandwidth. No automatic bandwidth/Gaussian
kernel/bin-seeding/weights. Candidate, support and iteration diagnostics are stored.

## Stage 4 — probabilistic mixture and graph spectrum

GaussianMixture(n_components=1,reg_covar=1e-6,tol=1e-6,max_iter=300,n_init=1,
means_init=None,random_state=0): native K 1..min(n,32), regularization [10^-12,10^12],
positive likelihood tolerance<=1, max_iter 1..1000, starts 1..8, local seed. Explicit
(K,p) initial means require one start. Full-covariance EM with anchored weighted
means, regularized population covariances and Cholesky log densities. Responsibilities
normalize shifted exponentials directly. Counts<=machine_epsilon*n are collapsed;
no successful initialization raises ConvergenceError. Unresolved covariance
eigen-directions require rescaling/greater regularization. Identical components
are valid and may share hard labels. score_samples is log density, score is its
nonempty mean; AIC/BIC use K*p+K*p*(p+1)/2+K-1 parameters. Regularization does not
promise unconditional monotonic unregularized likelihood or global optimality.

SpectralClustering(n_clusters=8,affinity='rbf',gamma=1,n_init=10,random_state=0):
K 1..min(n,64), positive gamma<=10^12, starts 1..16. Feature mode n<=256,p<=32;
precomputed affinity is (n,n), 2<=n<=256, numeric finite values in [0,10^12], zero
diagonal and 10^-12 symmetry tolerance, explicitly averaged within tolerance.
Isolated vertices and K below component count fail. The top normalized-affinity
eigenvectors are row normalized (Ng-Jordan-Weiss) then partitioned by canonical
K-Means. Eigenvectors can differ by sign/rotation; projector/partition comparisons
are appropriate. Normalized cut is a diagnostic, not a global-optimality proof.
No out-of-sample prediction or generic transform is invented.

## Evaluation, references and review

Use centroid distortion, silhouette/coverage, label-invariant agreement and density
likelihood as appropriate. Noise handling must be explicit. Transductive labels
are not a held-out classifier score. Fit preprocessing only on permitted training
data; actual benchmarks keep construction, seeds, data sizes and timing separate
from correctness. Nonconvex fits are local solutions. Reference alignments must
match distance, initialization, regularization, self-neighbor and stopping rules.
No external clustering implementation is called by core code; sklearn/SciPy are
independent development references only. No network dataset/download is needed.
Hosted CI is distinct from actual local/extracted checks.
