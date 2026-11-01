# Momentum

## 1. Algorithm Name

Momentum,canonical ID `momentum`,B10 Optimization. Implemented variant: **heavy-ball velocity accumulation without Nesterov**.

## 2. Overview

A velocity carries prior gradients into the next direction. This implementation accumulates beta*v+g,not an EMA with(1-beta) on the gradient.

## 3. Problem Statement

fun(x) returns one objective scalar; gradient(x) returns its full gradient with exactly the same vector shape. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

On a long narrow quadratic bowl,velocity can carry useful directional persistence; it can also overshoot. Objective increases are compatible with momentum and are not hidden by the driver. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Teaching and auditing small differentiable training objectives,with the stated state/regularization convention. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

v_next=beta*v+g; x_next=x-learning_rate*v_next. Initialize v=0. The update uses the NEW velocity. beta is in[0,1); no Nesterov lookahead,decay or extra gradient scaling.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Evaluate the full objective/gradient,then update velocity and parameters together transactionally. A supplied zero gradient does not imply zero movement when velocity is nonzero. On an SPD quadratic,each eigenmode has characteristic roots of r²-(1+beta-learning_rate*lambda)r+beta; stable choices require the roots inside the unit disk. No nonconvex global theorem is asserted.

## 9. Pseudocode

```text
velocity = zeros(D)
for each full-gradient update:
    velocity = beta * velocity + gradient
    x = x - learning_rate * velocity
check full gradient norm or budget
```

## 10. Dry Run

For beta=.8,learning_rate=.1,x=[1,-2],g1=[2,-4],v1=[2,-4] and x1=[.8,-1.6]. With g2=[-1,3],v2=[.6,-.2] and x2=[.74,-1.58]. A following zero gradient still gives v3=[.48,-.16] and x3=[.692,-1.564].

## 11. Time Complexity

For D parameters,T updates,full objective cost F and gradient cost G,total time is O((T+1)(F+G)+TD). Each state update is linear in D; no Hessian is evaluated. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Owned working moment/velocity state is O(D); the returned trajectory costs O((T+1)D) and objective history O(T). No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exposes `Momentum(learning_rate=.1,beta=.9).minimize(fun,gradient,x0,max_iter=1000,tolerance=1e-8)`. Stateful `step(x,g)` returns new parameters; `get_state()` returns a deep copy and `reset()` clears state. State contains velocity and counter t; initial velocity is zero. reset removes accumulated velocity and dimension lock. A failed step or minimize call leaves the previous committed state intact. Result fields are x,fun,n_iter,nfev,status,converged,history and diagnostics. Diagnostics include n_updates,njev,gradient_norm,state,trajectory.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/momentum/python/example.py
```

It minimizes f(x)=.5*x.T*diag(2,4)*x-[2,-8].T*x,starts at[3,1],and compares with the unregularized task optimum[1,-2]. The executable shows the actual learning rate and termination status; its budget is1000 iterations. AdamW intentionally decays only the first coordinate. The full gradient is deterministic. Actual executed output:

```json
{"converged": true, "gradient_norm": 4.3e-09, "initial": [3.0, 1.0], "iterations": 180, "learning_rate": 0.1, "objective": -9.0, "objective_evaluations": 181, "status": "gradient-tolerance", "task_optimum": [1.0, -2.0], "updates": 180, "x": [1.0, -2.0]}
```

## 16. Edge Cases

Reject empty/nonscalar-shaped parameter vectors,nonfinite data,broadcast gradients,invalid rates/tolerances and invalid budgets. max_iter1..10000 is required. Learning_rate1e-8..10,tolerance1e-12..1. Parameter magnitudes are capped at1e6,gradient components at1e12 and objective magnitude at1e100. Invalid arguments raise ValueError; nonfinite/out-of-domain callback arithmetic or updates raise NumericalError. No NaN replacement is performed.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. The driver stops at a full-gradient L2 tolerance or iteration budget. A zero-gradient step and a driver returning a stationary point have different semantics: a direct step still applies existing inertia.

## 18. Disadvantages and Limitations

Velocity can oscillate or amplify poor rate choices. Monotonic objective decrease is not guaranteed. The implemented recurrence is not Nesterov momentum or an EMA-gradient variant. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

At beta0 it reduces to batch GD. RMSProp rescales a current gradient instead of carrying a velocity; Adam has separately scaled first and second moments. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Explain the exact update and state order. Which norm is checked,and when? Does an exhausted budget imply convergence? No. Does zero sampled gradient imply zero full gradient? No. Which coordinates represent a bias,and who defines their derivatives? The caller.

## 23. Practice Problems

Reproduce the dry run,then vary a valid rate and observe both objective and termination status. Check a quadratic gradient with central differences. Choose an SPD quadratic,solve its optimum independently,and derive its coordinate error recurrence. Verification uses Independent two-step hand velocity updates,zero-gradient inertia,beta0 equivalence to plain GD,SPD analytic optima and shared transactional/numerical/state tests. See [tests](tests/test_python.py).

## 24. References

Polyak,[Some methods of speeding up the convergence of iteration methods,1964](https://www.mathnet.ru/php/archive.phtml?jrnid=zvmmf&option_lang=eng&paperid=7713&wshow=paper).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
