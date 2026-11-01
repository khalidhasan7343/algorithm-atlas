# Batch Gradient Descent

## 1. Algorithm Name

Batch Gradient Descent,canonical ID `batch-gradient-descent`,B10 Optimization. Implemented variant: **constant-step full-gradient descent**.

## 2. Overview

A deterministic full-objective gradient gives one vector update per iteration. Every coordinate,including an explicitly represented bias,is updated by its supplied derivative.

## 3. Problem Statement

fun(x) returns one objective scalar; gradient(x) returns its full gradient with exactly the same vector shape. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

At x the gradient points toward greatest local increase. Subtracting a sufficiently small multiple gives descent under a smoothness assumption; a large learning rate need not improve the objective. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Small smooth loss minimization,least-squares teaching exercises and inspecting every optimization step. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

x_next = x - learning_rate * gradient(x). There is no momentum,adaptive scaling,weight decay or hidden intercept exemption.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Evaluate the full objective and gradient at the copied initial vector. If its L2 gradient norm meets tolerance,return without an update. Otherwise take the stated step,evaluate the new full objective/gradient,and repeat up to max_iter. For an SPD quadratic,an independently known optimum is solve(A,b); step sizes in(0,2/lambda_max(A)) yield convergence in exact arithmetic.

## 9. Pseudocode

```text
x = copy(x0)
repeat up to max_iter:
    if norm(full_gradient(x)) <= tolerance: stop
    x = x - learning_rate * full_gradient(x)
return x,full_objective(x),status
```

## 10. Dry Run

For x=[2,-3],g=[4,-2] and learning_rate=.25,the next point is[1,-2.5]. On a diagonal quadratic,the error coordinate after k steps is(1-learning_rate*lambda_i)^k times its initial error; tests verify the complete trajectory.

## 11. Time Complexity

For D parameters,T updates,objective cost F and gradient cost G,total time is O((T+1)(F+G)+TD). No Hessian is formed or inverted. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Working optimizer state is O(D); the returned full trajectory uses O((T+1)D),objective history O(T). Caller data is not owned. No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `BatchGradientDescent(learning_rate=.1).minimize(fun,gradient,x0,max_iter=1000,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. Only an update counter t is retained; reset clears it. The parameter dimension is locked after step until reset. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/batch-gradient-descent/python/example.py
```

It minimizes half mean squared residual on six fixed observations,starts at[3,1],uses learning_rate.1 and compares with the known optimum[1,-2]. The full gradient is deterministic. Actual executed output:

```json
{"analytical": [1.0, -2.0], "converged": true, "gradient_evaluations": 141, "initial": [3.0, 1.0], "iterations": 140, "learning_rate": 0.1, "objective": 0.0, "objective_evaluations": 141, "status": "gradient-tolerance", "updates": 140, "x": [1.0, -1.99999999]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. max_iter1..10000 is required. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. Only the full supplied gradient L2 norm can establish gradient-tolerance. Exhausting max_iter yields iteration-budget and converged=False. This certifies approximate stationarity,not a global optimum on a nonconvex function.

## 18. Disadvantages and Limitations

Conditioning and learning-rate choice control progress. Large steps may increase the objective or leave the numerical domain. No line search,projection or acceleration is performed. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

Unlike SGD it uses the full gradient; unlike mini-batch GD it has no sampling or tail batch; unlike L-BFGS it has no curvature history. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Choose an SPD quadratic,solve its optimum independently,and derive its coordinate error recurrence. Verification uses Hand updates,diagonal closed-form trajectories,seeded SPD solve(A,b),independent objective finite differences and preserved B1 loss/gradient compatibility. See [tests](tests/test_python.py).

## 24. References

Bottou,[Large-Scale Machine Learning with Stochastic Gradient Descent,2010](https://leon.bottou.org/publications/pdf/compstat-2010.pdf).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
