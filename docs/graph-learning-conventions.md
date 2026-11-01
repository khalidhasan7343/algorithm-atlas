# B9 graph and numerical contracts

Owner MD.Khalid Hasan; MIT. Dense float64 adjacency matrices only. Node IDs are
row/column indices0..n-1,1<=n<=32. A[i,j] is the nonnegative outgoing edge weight
from i to j. Zero means no edge. Entries must be real,finite and<=1e6; boolean,
complex and string arrays are rejected. Empty/nonsquare graphs are rejected.
No implicit node insertion,direction conversion or edge-list parsing. Duplicate
edges are not representable separately: callers must explicitly sum their weights
before constructing a matrix. All inputs are copied. Traversal candidates use
ascending indices. Graphs may be disconnected and have isolated nodes.

PageRank accepts directed/undirected weighted matrices and nonnegative diagonal
weights. P is row-stochastic. Dangling rows use the same v as teleportation.
Personalization is a nonnegative length-n probability vector summing to1 within
1e-12,then normalized for roundoff. d is in[0,1),tolerance1e-14..1,max_iter1..100000.
The observed residual/(1-d) is an exact-arithmetic L1 error bound,not a certified
floating-point bound. Near1 damping amplifies roundoff and slows convergence.
A finite budget exposes converged_=False rather than claiming convergence.

Node2Vec supports exactly symmetric weighted undirected graphs with zero diagonal.
No directed distance convention or self-loop bias is guessed. First steps use
edge weights; subsequent steps multiply them by1/p,1 or1/q for distances0,1,2.
Isolated walks stop immediately. Fixed windows yield ordered target/context pairs.
SGNS uses separate input/output embeddings and mean positive loss plus summed
negative losses per pair. Noise follows positive-context counts^0.75,with replacement;
positive/target IDs may be sampled as negatives. Samples are drawn once per fit,
so the finite sampled objective is fixed across full-batch gradient steps. This
is a declared educational optimization variant,not the original production SGD.
Isolated node vectors receive no data-driven training signal. No universal
community-separation or benchmark claim. p,q in[1e-3,1e3],dimensions1..16,
walk_length1..64,num_walks1..20,window1..8,negatives1..8,epochs1..500.
Before generating pairs,require the conservative upper bound
n*num_walks*walk_length*2*window<=20000 and
that bound*epochs*(negative_samples+1)*dimensions<=20000000.
No positive pairs means fit fails. Individual walk generation is bounded by
640 walks and40960 tokens; all model-generated randomness uses a local Generator.

GCN supports exactly symmetric weighted undirected adjacency with zero input
diagonal. self_loops=True adds identity exactly once; False keeps it absent.
B7's approved normalization utility is reused byte-for-byte: isolated inverse
square-root degrees are zero without loops and1 with loops. No B7 source changes.
The B9-specific two-layer tanh classifier uses masked mean cross-entropy plus
l2/2 times squared W1/W2 norms; biases are unpenalized. Label integers are0..C-1,
C2..8; -1 means unknown. Selected training labels must contain all C classes.
An explicit train_mask must be a nonempty boolean length-n vector selecting known
labels. Known unselected labels do not affect fitting or preprocessing. Features
have1..16 columns,finite magnitudes<=1e6. Hidden width1..16,epochs1..2000,
l2 in[0,1000],learning_rate1e-6..1,global gradient clip1e-6..1000.
The tanh/bias/full-batch SGD variant has no dropout,Adam or production-library parity.
Node outputs are permutation-equivariant,not invariant. Fit does not reorder nodes.

Both learners retain initial and post-step fixed-objective history,update counts,
and explicit finite-epoch status; no universal convergence is asserted. Their
parameter blocks must remain finite with magnitude<=1e6. Failed refits preserve
old fitted state; inference requires successful fit and uses fitted dimensions/
self-loop convention. Inference results are copies. C++ optional/absent. All loops,
allocations and examples are intentionally bounded; dense storage costs n^2 even
for a sparse input graph. No network,dataset download or global RNG mutation.
