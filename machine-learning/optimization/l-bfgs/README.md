# L-BFGS

## 1. Algorithm Name

L-BFGS,canonical ID `l-bfgs`,B10 Optimization. Implemented variant: **limited-memory BFGS with bounded strong-Wolfe bracket/zoom**.

## 2. Overview

Curvature is approximated by a short history of accepted parameter/gradient differences. A two-loop recursion applies an inverse-Hessian approximation without forming an inverse or evaluating a Hessian.

## 3. Problem Statement

fun(x) returns one objective scalar; gradient(x) returns its full gradient with exactly the same vector shape. Parameters are copied float64 vectors of length1..32; no flattening,broadcasting or implicit bias treatment is performed. Minimize the supplied objective; maximization requires explicit sign changes in both objective and derivative. Callbacks must be trusted,prompt,pure and valid at evaluated points. See [contracts](../../../docs/optimization-conventions.md).

## 4. Why Do We Need This Algorithm?

A gradient alone ignores local scaling. Positive-curvature secant pairs carry recent scaling information while keeping internal memory linear in the history length and parameter dimension. A line search checks both sufficient decrease and curvature. Optimization is separate from defining or statistically evaluating a predictive model; a lower training objective is not a generalization guarantee.

## 5. Real-World Applications

Small smooth unconstrained losses where recent curvature can help and exact full gradients are available. No production deployment or universal performance superiority is claimed.

## 6. Core Intuition

Store s=x_new-x,y=g_new-g,rho=1/(s.T*y). For q=g,loop newest-to-oldest: alpha=rho*s.T*q; q←q-alpha*y. Start r=gamma*q with gamma=(s_last.T*y_last)/(y_last.T*y_last),or1 without history. Loop oldest-to-newest:r←r+s*(alpha-rho*y.T*r). Search direction is-r.

## 7. Prerequisites

Vectors,derivatives,finite-sum normalization,numerical precision and stopping criteria. A gradient is not an objective value; a gradient norm establishes approximate stationarity only under a correct differentiable callback. The test-only quadratic/Rosenbrock objectives are mathematical fixtures,not new canonical algorithms.

## 8. Step-by-Step Working Process

Use at most history_size recent pairs. Accept a pair only if s.T*y>1e-20 and exceeds1e-10*||s||*||y||; otherwise count an explicit skip. A non-descent direction resets memory and uses-g. Bracket/zoom with midpoint refinement seeks f(x+alpha*p)<=f(x)+c1*alpha*g.T*p and |g_new.T*p|<=-c2*g.T*p. Positive curvature preserves an SPD inverse approximation in exact arithmetic; finite precision and a finite search budget limit guarantees.

## 9. Pseudocode

```text
pairs = empty
while full gradient norm exceeds tolerance and iteration budget remains:
    direction = -two_loop(gradient,pairs)
    resolve a bounded strong-Wolfe bracket/zoom step
    if no step is found: return non-converged line-search-failed
    form s,y; retain only usable positive-curvature pairs
    update current point and objective/gradient
```

## 10. Dry Run

Without history,H0=I and the first direction is-g. For f=.5*x.T*diag(2,4)*x-[2,-8].T*x at[3,1],g=[4,12]. Step alpha=.5 gives[1,-5],f decreases13→9,and the new directional slope144 meets c2=.9 times the initial magnitude160. s=[-2,-6],y=[-4,-24],so s.T*y=152>0. Independent dense inverse-BFGS products verify the recursion.

## 11. Time Complexity

For D parameters,m retained pairs,T accepted iterations and J line-search trials,total time is O(T*m*D+J*(D+F+G)+F+G). Only valid trial evaluations count in nfev/njev; resource-domain rejections count separately as trials. Best/average optimization iteration counts depend on the objective and settings; the configured budget is an upper bound,not a convergence theorem.

## 12. Space Complexity

Internal curvature storage O(mD); working vectors O(D). The actual returned trajectory costs O(TD),accepted Wolfe records O(T) and history O(T). This is limited internal memory,not constant total returned storage. No recursion or external dataset/model storage is required.

## 13. Python Implementation

[Source](python/solution.py) exports `LBFGS` and `inverse_hessian_product`. Use `LBFGS(history_size=5,c1=1e-4,c2=.9,max_line_search=40,initial_step=1,max_step=1e6).minimize(fun,gradient,x0,max_iter=200,tolerance=1e-8)`. The inspection helper validates supplied positive-curvature pairs. Results own x/history/trajectory; diagnostics expose gradient_norm,njev,curvature_pairs,wolfe_steps,skipped_curvature_updates,memory_resets and line_search_trials. Every call starts fresh; no step/get_state API is invented.

## 14. C++ Implementation

C++ is optional for this ML canonical and absent. No placeholder source or tests exist. DSA still requires actual Python,C++17 and C++20 execution.

## 15. Input and Output Examples

[Executable example](python/example.py),from repository root:

```sh
.venv/bin/python machine-learning/optimization/l-bfgs/python/example.py
```

It minimizes the two-dimensional Rosenbrock function from[-1.2,1],using history_size5 and max_iter200. The independent analytical optimum is[1,1] with objective0. Line-search evaluation counts are actual executed callback counts. The full gradient is deterministic. Actual executed output:

```json
{"analytical": [1.0, 1.0], "converged": true, "gradient_evaluations": 66, "gradient_norm": 3.9e-09, "history_size": 5, "initial": [-1.2, 1.0], "iterations": 36, "objective": 0.0, "objective_evaluations": 66, "status": "gradient-tolerance", "x": [1.0, 1.0]}
```

## 16. Edge Cases

Parameters/gradients/objectives follow the shared finite numerical bounds. history_size1..20,max_line_search1..80,max_iter1..2000,and max_iter*max_line_search<=20000 are required. Wolfe settings require0<c1<c2<1; initial_step1e-8..max_step,max_step<=1e6,tolerance1e-12..1. Reject invalid vectors/pairs/callbacks. Trials outside parameter magnitudes<=1e6 are explicitly rejected/backtracked without fabricating a callback objective. An exhausted zoom interval or step ceiling returns line-search-failed. Initial stationary points need no update.

## 17. Advantages

Explicit mathematics,independent hand/analytical checks,bounded loops,owned state and inspectable histories make this variant useful for learning and auditing. A full-gradient norm within tolerance returns gradient-tolerance. Iteration exhaustion returns iteration-budget. Unresolved Armijo/strong-curvature search returns line-search-failed at the last accepted finite point. Neither budget condition claims convergence,infeasibility or unboundedness.

## 18. Disadvantages and Limitations

This is unconstrained L-BFGS,not L-BFGS-B or exact Newton. Bad scaling,nonconvex curvature,a small search ceiling or an exhausted trial budget may prevent a step. Positive secant curvature does not prove global optimality. No arbitrary constraint or callback-domain repair is performed. Callback runtime cannot be bounded by an iteration counter; callbacks must return promptly. Numerical bounds are educational resource/domain limits,not a general constrained optimization solver.

## 19. When to Use It

Use it when the stated callback/representation and update rule match the intended mathematical experiment. Check units,scaling,objective normalization and stopping evidence before interpreting the result.

## 20. When Not to Use It

Do not use this smooth-gradient routine for arbitrary nondifferentiable/discrete objectives,unknown derivatives or constrained feasibility. Consider the separately specified GA/SA canonicals for supported discrete search. No automatic finite-difference gradient or solver delegation is hidden in the core.

## 21. Comparison With Related Algorithms

Batch GD uses an identity scale on every step. Adam rescales gradient moments without secant curvature. L-BFGS uses positive-curvature pairs and a strong-Wolfe search,without an explicit Hessian. Related canonical paths stay unchanged; previous learners retain their original optimizer behavior.

## 22. Interview Questions

Why store s and y rather than a dense inverse? The two-loop action saves internal memory. Why require positive curvature? It preserves positive definiteness of the inverse update under the stated conditions. Why use strong Wolfe rather than only objective decrease? It controls directional curvature. Does line-search failure prove unboundedness? No.

## 23. Practice Problems

Build a dense inverse-BFGS oracle from valid secant pairs and compare its matrix-vector action. Recompute every accepted Wolfe condition from actual iterates/gradients. Diagnose Rosenbrock with a small max_step ceiling: an early valley direction needs alpha256,so the former arbitrary ceiling64 was insufficient. The default ceiling is now1e6 while evaluations/parameters remain bounded. Check singular quadratics without calling an inverse; never weaken a convergence assertion to hide a search defect.

## 24. References

Liu and Nocedal,[On the limited memory BFGS method for large scale optimization,1989](https://doi.org/10.1007/BF01589116); Bottou,Curtis and Nocedal,[Optimization Methods for Large-Scale Machine Learning,2018](https://arxiv.org/abs/1606.04838).

[Project scope](../../../docs/optimization-scope.md),[numerical contracts](../../../docs/optimization-conventions.md) and independent tests specify this exact educational variant; no unread source or published benchmark reproduction is claimed.

## 25. Author Attribution

Algorithm Atlas is maintained by **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [MIT License](../../../LICENSE); [contribution policy](../../../CONTRIBUTING.md). Preserve source attribution and canonical ownership.
