# B10 objective,variant and numerical contracts

Owner MD.Khalid Hasan; MIT. The ten catalog canonicals are separate educational
methods,not aliases for one external library optimizer. All optimize **minima**.
There is no general constrained solver,Newton method or particle-swarm method in
B10; none is added. GA/SA retain shared C3/C4 memberships under B10 ownership.

## Continuous vectors and callbacks

Parameters are copied float64 vectors of length1..32,magnitude<=1e6. A supplied
gradient must have the identical vector shape,finite components of magnitude
<=1e12. No flattening,shape broadcasting,automatic bias exemption or implicit
regularization. Objective callbacks return one finite real scalar of magnitude
<=1e100,not a vector,bool or a0D array. Callbacks receive read-only owned copies;
they must be trusted,prompt,pure and defined at evaluated points. Iterations/
evaluations are bounded; arbitrary callback wall time is not sandboxed.
Invalid arguments/types/shapes raise ValueError; nonfinite/out-of-domain callback
arithmetic and updates raise NumericalError. No NaN replacement or warning
suppression is used. Underflow remains ordinary float64 behavior; zero adaptive
second moments are protected by a strictly positive epsilon. A scaled L2 norm
avoids squaring tiny/huge values when checking gradient tolerance.

Full-gradient methods accept minimize(fun,gradient,x0,max_iter=1000,
tolerance=1e-8); fun(x) returns f and gradient(x) returns its exact full derivative.
The core does not estimate derivatives automatically. Learning rates1e-8..10,
tolerance1e-12..1,max_iter1..10000. Correct derivatives and smoothness assumptions
are the caller's responsibility. Nondifferentiable/nonconvex objectives do not
receive a global convergence guarantee.

## Exact first-order variants

| Canonical | Update and owned state |
| --- | --- |
| Batch GD | x←x-ηg using full gradient; counter only |
| SGD | Same vector update,one observation from a random permutation per epoch |
| Mini-batch GD | Same update using the **mean** gradient of the actual selected batch |
| Momentum | v←βv+g; x←x-ηv; zero initial v; no Nesterov and no(1-β) factor |
| RMSProp | v←βv+(1-β)g²; x←x-ηg/(sqrt(v)+epsilon); uncentered,no bias correction |
| Adam | m←β1m+(1-β1)g;v←β2v+(1-β2)g²;zero initial moments;bias-correct by1-β^t,then x←x-η*m_hat/(sqrt(v_hat)+epsilon) |
| AdamW | Adam moments use **raw** gradients; subtract η*weight_decay*mask*x_old separately; no coupled L2 term in moments |

Beta values are in[0,1); epsilon1e-12..1 sits **outside** the square root.
Bias correction uses a stable equivalent -expm1(t*log(beta)),with beta0 handled
exactly. Step indexing begins at1. AdamW reuses the Adam canonical update;
weight_decay in[0,1],η*weight_decay<=1,and an optional boolean length-D decay mask
make the chosen bounded shrinkage variant explicit. All coordinates decay by
default; exclude a represented bias using the mask. No AMSGrad,centered RMSProp,
Nesterov,scheduler or undocumented weight decay is claimed.

step(x,g) advances transactional optimizer state only after a valid finite update.
get_state returns a deep copy; reset clears dimension and state. Dimension changes
require reset for step. Every minimize run starts fresh state; repeated stochastic
runs restart the configured local Generator. Failed minimize calls preserve the
previous committed optimizer state. Results own x/history/diagnostic arrays.

Full methods normally stop only at the supplied full-gradient L2 tolerance.
This means approximate stationarity,not proof of a global optimum. AdamW with
nonzero active decay disables raw-task-gradient convergence stopping: its decoupled
regularization is not generally a fixed L2-regularized objective. Such runs expose
raw task loss/norm but return iteration-budget,converged=False. Zero-decay AdamW or an all-False mask
uses Adam's gradient stopping. Zero gradient can still move momentum/moment state
or decay weights in an explicitly requested step.

## Finite-sum sampling

SGD/mini-batch callbacks are gradient(x,indices),returning the selected **mean**.
fun(x) is the full mean objective. Each epoch samples one permutation without
replacement and partitions it,including a smaller tail. This is random reshuffling,
not iid with-replacement SGD; conditional gradient unbiasedness is not assumed.
Sample count1..256,max_epochs1..1000,epochs*N<=20000. Mini-batch size1..N.
The full mean gradient is checked before training and at each epoch end; an
individual zero sample/batch gradient cannot certify convergence. Objective history
is per epoch; trajectory/batch_history and state counter are per update.
Full checks and sample-gradient evaluations are counted separately in diagnostics.

## Limited-memory quasi-Newton

L-BFGS is unconstrained,uses a two-loop inverse-Hessian action and at most a small
number of positive-curvature(s,y) pairs. No Hessian or inverse is formed in the
core. History size1..20,line-search trials1..80,iterations1..2000 and
iterations*max_line_search<=20000 are bounded. Default max_step1e6 is an explicit
search ceiling; initial_step1e-8..max_step. A bounded bracket/zoom line search must satisfy Armijo and strong curvature
conditions. Non-descent directions reset memory/use steepest descent; weak or
nonpositive curvature pairs are skipped explicitly. Failure to resolve a line
search is a non-converged status,not a stationary-point claim. It is not L-BFGS-B,
not an infeasibility/unboundedness detector,and not an exact Newton solver.

## Binary search variants

GA and SA accept finite real objective values on binary integer/bool vectors of
length1..32. They need no gradient or Hessian. Returned best-so-far values do not
certify global optimality unless a separate finite oracle establishes it.
A caller-provided target_value produces target-reached when met; this is an
explicit requested threshold,not an automatically proved global optimum.

GA uses tournament selection for minimization,uniform crossover,independent
bit-flip mutation and at least one elite. Ties use a deterministic convention.
Population2..64,bits1..32,generations1..1000,tournament2..P,elites1..P-1;
require P+(P-elites)*max_generations<=20000 before allocation/evaluation.
Crossover/mutation probabilities are in[0,1]. Population size,dimensions,generations and total fitness evaluations are bounded.
All candidates remain binary. Elitism guarantees nonincreasing **best** fitness,
not monotonic average population fitness. Stagnation is reported as non-convergence.

SA flips one uniformly sampled bit. Worsening moves use the Metropolis rule
min(1,exp(-delta/T)); the actual decision uses log(U)<-delta/T to avoid exponent
underflow. Equal/improving moves are accepted without an extra uniform draw.
Initial temperature1e-8..1e6,cooling.001..1,floor1e-12..initial_temperature,
max_iter1..10000. Temperature cools geometrically; compare log-temperature against an explicit floor
before exponentiation. Return the best point and expose the last chain state,
accepted flags and temperature history. Current chain fitness may worsen; only
retained best fitness is monotonic. Finite cooling/budgets do not imply a global
annealing convergence theorem.

## Results and compatibility

OptimizationResult contains x,fun,n_iter,nfev,status,converged,history,diagnostics.
For sampled methods n_iter counts epochs; diagnostics.n_updates counts batches.
Derivative-free diagnostics do not fabricate gradient norms. Iteration/generation/
epoch/line-search/floor/stagnation budgets are distinguished from convergence.
Only finite parameter domains are supported; invalid callbacks are not silently
repaired. Returned histories have explicit storage costs,not constant total memory.

All previous learner optimizers remain byte-for-byte unchanged. B10 adds routines
for inspection/use; it does not silently reroute B1–B9 training. No SciPy optimizer,
PyTorch,network download,pickle or external ready-made optimizer is used in core.
SciPy may be an isolated test oracle using the existing environment. C++ optional/
absent for ML; existing DSA Python/C++17/C++20 policy remains mandatory. DPO remains
owner-approved: remain blocked. No Phase23 or Git publication is authorized.
