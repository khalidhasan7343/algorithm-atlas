# RMSProp

## 1. Algorithm Name

RMSProp,canonical ID `rmsprop`,B10 Optimization. Implemented variant: **uncentered RMSProp without bias correction; epsilon outside sqrt**.

## 2. Overview

A running squared-gradient average supplies coordinate-wise denominators. The current raw gradient remains the numerator; there is no first-moment velocity.

## 3. Problem Statement

fun(x) returns one objective scalar; gradient(x) returns its full gradient with exactly the same vector shape. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

Coordinates with recently large gradient magnitudes receive smaller scaled updates. Early second-moment values start at zero and are NOT bias-corrected,so the first scale differs from Adam. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Teaching and auditing small differentiable training objectives,with the stated state/regularization convention. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

v_next=beta*v+(1-beta)*g²; x_next=x-learning_rate*g/(sqrt(v_next)+epsilon). Operations are coordinate-wise. Initialize v=0; beta in[0,1); epsilon1e-12..1 is outside the square root.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Validate the raw gradient and state dimensions,form its squared EMA,then divide by sqrt(v)+epsilon and update. State commits only for a finite valid result. Zero gradients leave parameters unchanged but decay a nonzero squared average. A tiny/zero denominator is stabilized explicitly,not repaired by substituting arbitrary values.

## 9. Pseudocode

```text
squared_average = zeros(D)
for each update:
    squared_average = beta * squared_average + (1-beta) * gradient²
    x -= learning_rate * gradient / (sqrt(squared_average) + epsilon)
check full gradient or budget
```

## 10. Dry Run

With beta=.9 and first gradient[2,-4],the initial squared average becomes[.4,1.6]. A second gradient[-1,3] makes it[.46,2.34]. Divide each current gradient by sqrt(that coordinate)+epsilon. There is no division by1-beta^t; the tests independently calculate both steps.

## 11. Time Complexity

For D parameters,T updates,full objective cost F and gradient cost G,total time is O((T+1)(F+G)+TD). Each state update is linear in D; no Hessian is evaluated. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Owned working moment/velocity state is O(D); the returned trajectory costs O((T+1)D) and objective history O(T). No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `RMSProp(learning_rate=.01,beta=.9,epsilon=1e-8).minimize(fun,gradient,x0,max_iter=1000,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. State contains squared_average and t. Squared averages are initially zero and remain nonnegative under valid beta and finite gradients. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/rmsprop/python/example.py
```

It minimizes f(x)=.5*x.T*diag(2,4)*x-[2,-8].T*x,starts at[3,1],and compares with the unregularized task optimum[1,-2]. The executable shows the actual learning rate and termination status; its budget is1000 iterations. AdamW intentionally decays only the first coordinate. The full gradient is deterministic. Actual executed output:

```json
{"converged": true, "gradient_norm": 2.7e-09, "initial": [3.0, 1.0], "iterations": 362, "learning_rate": 0.01, "objective": -9.0, "objective_evaluations": 363, "status": "gradient-tolerance", "task_optimum": [1.0, -2.0], "updates": 362, "x": [1.0, -2.0]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. max_iter1..10000 is required. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. A full-gradient norm may establish gradient-tolerance; otherwise budget exhaustion remains non-converged. Fixed-rate adaptation can oscillate near a stationary point,so a lower objective alone is not a convergence certificate.

## 18. Disadvantages and Limitations

Uncentered,uncorrected RMSProp is only one declared variant. Centered estimates,momentum,weight decay and inside-sqrt epsilon implementations are different. Fixed rates may prevent convergence; scaling/epsilon affect behavior. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

Unlike Adam it has no first moment or bias correction. Unlike Momentum it divides the current gradient by a learned coordinate scale. Epsilon placement is part of the specification. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Choose an SPD quadratic,solve its optimum independently,and derive its coordinate error recurrence. Verification uses Scalar-loop EMA/update oracles,explicit epsilon placement,beta0 current-square identity,zero/tiny gradients and shared state/numerical checks. See [tests](tests/test_python.py).

## 24. References

Hinton,[Neural Networks for Machine Learning,lecture6e,2012](https://www.cs.toronto.edu/~hinton/coursera/lecture6/lec6.pdf); the precise stabilizer convention here is explicitly documented.

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
