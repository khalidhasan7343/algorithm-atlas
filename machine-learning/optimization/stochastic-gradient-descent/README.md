# Stochastic Gradient Descent

## 1. Algorithm Name

Stochastic Gradient Descent,canonical ID `stochastic-gradient-descent`,B10 Optimization. Implemented variant: **random-reshuffling single-observation SGD**.

## 2. Overview

A finite-sum loss is optimized by updating after each selected observation. One local random permutation visits every observation once per epoch; this is random reshuffling,not independent with-replacement sampling.

## 3. Problem Statement

fun(x) returns the full finite-sum mean objective; gradient(x,indices) returns the mean gradient over the selected indices. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

Cheap observation gradients replace a full-gradient update. Their order matters because each subsequent gradient is evaluated at the latest parameters. An individual zero sample gradient does not establish full-objective stationarity. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Teaching observation-level finite-sum updates and diagnosing ordering/reproducibility in small datasets. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

For f(x)=mean_i f_i(x),select one shuffled index i and set x_next=x-learning_rate*gradient_i(x). The callback receives a length-one indices array and returns a D-vector. Do not divide a per-observation gradient by the whole dataset again.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Validate the finite sample count and epoch budget. Check the full mean gradient at initialization. Each epoch generates a private seeded permutation,applies one update per observation,and then reevaluates the full objective and full mean gradient. Only that full-gradient check can stop as converged. Conditional reshuffling noise is not assumed iid or conditionally unbiased.

## 9. Pseudocode

```text
x = copy(x0); rng = local_generator(seed)
for each bounded epoch:
    for i in rng.permutation(n_samples):
        x -= learning_rate * gradient(x,[i])
    record full objective and check gradient(x,all_indices)
return x,status
```

## 10. Dry Run

With targets[-1,2,4],x0=.3 and learning_rate=.1,each sampled index i applies x←.9x+.1target_i. The independent test replays the declared permutation over two epochs and compares every point and index. For targets[0,2],the zero gradient of sample0 at x=0 must not terminate the full problem.

## 11. Time Complexity

Let U be actual sample updates,E epochs,N observations,D parameters,G1 a sample-gradient cost,GN a full-gradient cost and F the full-objective cost. Time is O(U(D+G1)+E(N+F+GN)+F+GN). Histories and full checks have real costs. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Working state O(D+N); stored trajectories O(UD),index history O(EN),objective history O(E). Prospective E*N is capped at20000. No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `StochasticGradientDescent(learning_rate=.01,random_state=0).minimize(fun,gradient,x0,n_samples=N,max_epochs=100,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. The counter t counts observation updates. Each minimize call resets optimizer state and restarts the configured local RNG; batch_history preserves the actual index order. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory,batch_history.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/stochastic-gradient-descent/python/example.py
```

It minimizes half mean squared residual on six fixed observations,starts at[3,1],uses learning_rate.1 and compares with the known optimum[1,-2]. The seed is22; mini-batches have size2 when applicable. Actual executed output:

```json
{"analytical": [1.0, -2.0], "converged": true, "gradient_evaluations": 141, "initial": [3.0, 1.0], "iterations": 20, "learning_rate": 0.1, "objective": 0.0, "objective_evaluations": 21, "status": "gradient-tolerance", "updates": 120, "x": [1.0, -2.0]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. Sample count1..256,epochs1..1000 and epochs*N<=20000 are required. Batch size must be valid and not exceed N. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. Full mean-gradient L2 norm is checked initially and at epoch boundaries. Sample-gradient norms never certify convergence. An exhausted epoch budget returns epoch-budget and converged=False.

## 18. Disadvantages and Limitations

A constant rate on noisy finite sums can cycle or stop before a useful solution. Reshuffling differs from with-replacement SGD; no Robbins–Monro theorem or monotonic objective decrease is asserted for this implementation. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

Batch GD takes one full-gradient step per iteration. Mini-batch GD averages selected groups. Here every update uses exactly one observation; n_iter counts epochs while diagnostics.n_updates counts actual updates. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Trace every selected index and the final tail; compare different fixed seeds without demanding universal improvement. Verification uses Independent exact reshuffled updates,complete index coverage,full-gradient stopping traps,interpolating analytic optima,local RNG checks and same-seed repeatability. See [tests](tests/test_python.py).

## 24. References

Bottou,[Large-Scale Machine Learning with Stochastic Gradient Descent,2010](https://leon.bottou.org/publications/pdf/compstat-2010.pdf).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
