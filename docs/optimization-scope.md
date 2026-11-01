# Phase22 B10 locked scope

Owner MD.Khalid Hasan; MIT. Phase21 handoff explicitly owner-approved on2026-10-31
Asia/Dhaka. New Phase22 owner review pending. The authoritative current category is
B10 Optimization at machine-learning/optimization,with exactly10 canonicals;
the historical expected count matches. No missing algorithm specification/blocker
was found in B10. All ten began as planning READMEs without code/tests/examples.

| # | Algorithm | Canonical ID | Canonical path | Initial Python/docs/tests | Action |
| --- | --- | --- | --- | --- | --- |
| 1 | Batch Gradient Descent | batch-gradient-descent | machine-learning/optimization/batch-gradient-descent | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 2 | Stochastic Gradient Descent | stochastic-gradient-descent | machine-learning/optimization/stochastic-gradient-descent | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 3 | Mini-Batch Gradient Descent | mini-batch-gradient-descent | machine-learning/optimization/mini-batch-gradient-descent | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 4 | Momentum | momentum | machine-learning/optimization/momentum | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 5 | RMSProp | rmsprop | machine-learning/optimization/rmsprop | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 6 | Adam | adam | machine-learning/optimization/adam | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 7 | AdamW | adamw | machine-learning/optimization/adamw | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 8 | L-BFGS | l-bfgs | machine-learning/optimization/l-bfgs | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 9 | Genetic Algorithms | genetic-algorithms | machine-learning/optimization/genetic-algorithms | planned/planned/planned | Implement missing source/tests/example/full lesson |
| 10 | Simulated Annealing | simulated-annealing | machine-learning/optimization/simulated-annealing | planned/planned/planned | Implement missing source/tests/example/full lesson |

Four internal batches: (1) batch/SGD/mini-batch;(2) momentum/RMSProp/Adam/AdamW;
(3) L-BFGS;(4) genetic algorithms/simulated annealing. No unused batch is invented.
Proceed automatically after passing mathematical/tests/example/25-section gates.

Seven first-order methods minimize differentiable vector objectives; SGD and
mini-batch use explicit finite-sum sample gradients. L-BFGS is an unconstrained
limited-memory quasi-Newton method,not Newton or L-BFGS-B. GA and SA operate on
bounded binary strings with explicit fitness/variation/temperature mechanisms;
they require no derivatives. These are declared educational variants,not library
parity claims. There is no general constrained optimizer in this catalog; binary
representation feasibility is not a KKT solver. Exact variants are in
[contracts](optimization-conventions.md).

GA and SA retain one B10 canonical each serving their existing C3/C4 memberships.
Do not implement other AI topics,particle swarm,Newton,or other noncatalog methods.
Preserve all prior B1–B9/DSA source/tests/lessons,reports,evidence,archives and staged
work. Existing learner optimizers are not replaced by these new routines.
Inventory stays35/256/235. DPO remains intentionally blocked with its owner-approved
Outcome3 decision,ID,path,four statuses and research unchanged. Python/NumPy core;
ML C++ optional/absent; DSA retains actual Python/C++17/C++20. No heavyweight
framework,dataset/weights download or unsafe serialization. Deliver the tracked
report and verified ZIP/checksum/JSON,then STOP. No Phase23,commit,push,tag or release.
