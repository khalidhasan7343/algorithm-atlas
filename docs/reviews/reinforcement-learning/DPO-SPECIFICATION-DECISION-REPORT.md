# DPO specification decision report

Algorithm Atlas — Phase 20 / B8. Prepared 2026-10-31, Asia/Dhaka.
Owner and maintainer: **MD.Khalid Hasan**. [MIT License](../../../LICENSE).
**DPO specification decision — owner-approved: remain blocked (Outcome 3).**
**Phase 20 implementation review approval — pending.**

On 2026-10-31 (Asia/Dhaka), the owner explicitly approved Outcome 3.
The research, verified references and equations below are preserved. No candidate
is selected or substituted; the existing DPO ID/path and all blocked statuses remain.
This decision approves intentional blocking, not Phase 20 implementation review.

**Approved outcome: 3 — keep the entry blocked.** Verified papers exist,
but no recovered syllabus evidence identifies one as the intended algorithm.
Distributed PPO is the strongest *curricular-fit hypothesis*, not a verified
interpretation. Choosing it requires an explicit catalog correction.
The nine defined B8 algorithms are already implemented and independently packaged.

## Evidence and confidence

| Finding | Evidence | Confidence |
| --- | --- | --- |
| Original preserved label is “Dynamic Policy Optimization (DPO, terminology as written in original notes)” | [Frozen syllabus fixture](../../../tests/fixtures/required_syllabus.json), B8; byte-identical to Git commit e82ff0b (Phase-0_Done) | Verified transcription |
| Identity/path and all four statuses remain blocked | [catalog.yaml](../../../catalog.yaml), dynamic-policy-optimization; same blocked record in e82ff0b | Verified |
| No defining paper, objective or variant was supplied | [AGENTS.md](../../../AGENTS.md), [terminology record](../../terminology-decisions.md), [Phase 0 review](../../phase-0-review.md) | Verified repository evidence |
| Earlier candidate links were possibilities, not owner selection | Terminology record explicitly says none was adopted | Verified |
| No original handwritten scan/master attachment was located in repository files | Repository document/file inventory; Phase 0 report records a comparison with the attachment | Access limitation; cannot independently reconstruct the original author's intent |
| Distributed PPO fits A3C/PPO/continuous-control neighbors | Comparison below | Inference only |
| A particular candidate was intended | No corroborating citation, course page, annotation or owner selection recovered | Unestablished |

The related-algorithm links to PPO and REINFORCE are broad compatibility evidence,
not a unique identifier. Publication date, acronym resemblance and search ranking
cannot supply missing provenance. This is a bounded literature investigation,
not proof that no other use of these acronyms exists.

## Candidate identities

Primary sources were inspected for metadata and methods where accessible.
Years distinguish preprint and conference dates. No arXiv DOI is represented
as a peer-reviewed journal DOI.

| ID / name | Exact paper title; authors; year | Verified primary identifier |
| --- | --- | --- |
| C1 DyPO, Dynamic Policy Optimization | **DyPO: Dynamic Policy Optimization for Multi-Turn Interactive Reasoning**. Xiao Feng, Bo Han, Zhanke Zhou, Jiaqi Fan, Jiangchao Yao, Ka Ho Li, Dahai Yu, Michael Kwok-Po Ng. **2025**, ICML workshop on Programmatic Representations for Agent Learning, not the main conference track. | [OpenReview paper PDF](https://openreview.net/pdf/3e0a9be58197962b8848e6ec3dd5de090da8bdc3.pdf). No DOI/arXiv identifier verified. |
| C2 DYPO, Dynamic Policy Optimization | **Bridging SFT and RL: Dynamic Policy Optimization for Robust Reasoning**. Taojie Zhu, Dongyang Xu, Ding Zou, Sen Zhao, Qiaobo Hao, Zhiguo Yang, Yonghong He. **2026**. | [arXiv:2604.08926v1](https://arxiv.org/abs/2604.08926v1), submitted April 10; record notes ACL 2026 Findings. |
| C3 DCPO, Dynamic Clipping Policy Optimization | **DCPO: Dynamic Clipping Policy Optimization**. Shihui Yang, Chengfeng Dou, Peidong Guo, Kai Lu, Qiang Ju, Fei Deng, Rihui Xin. **2025**. | [arXiv:2509.02333v2](https://arxiv.org/abs/2509.02333v2), September 8 version. |
| C4 DPPO, Dynamic Proximal Policy Optimization | **Dynamic proximal policy optimization: Enhancing PPO with adaptive entropy and smooth clipping**. Shiyu Sha, Yanhong Liu, Benyan Huo. **2026**, Neurocomputing 674, 132861. | [Publisher abstract and metadata](https://www.sciencedirect.com/science/article/abs/pii/S0925231226002584); [DOI:10.1016/j.neucom.2026.132861](https://doi.org/10.1016/j.neucom.2026.132861). |
| C5 DPPO, Distributed Proximal Policy Optimization | **Emergence of Locomotion Behaviours in Rich Environments**. Nicolas Heess, Dhruva TB, Srinivasan Sriram, Jay Lemmon, Josh Merel, Greg Wayne, Yuval Tassa, Tom Erez, Ziyu Wang, S. M. Ali Eslami, Martin Riedmiller, David Silver. **2017**. | [arXiv:1707.02286](https://arxiv.org/abs/1707.02286), §2 and supplementary A.1. |
| C6 DPPO, Diffusion Policy Policy Optimization | **Diffusion Policy Policy Optimization**. Allen Z. Ren, Justin Lidard, Lars L. Ankile, Anthony Simeonov, Pulkit Agrawal, Anirudha Majumdar, Benjamin Burchfiel, Hongkai Dai, Max Simchowitz. **2024 preprint / ICLR 2025**. | [arXiv:2409.00588v3](https://arxiv.org/abs/2409.00588v3); [ICLR paper](https://openreview.net/pdf?id=mEpqHvbD2h). |
| C7 DCPO, Distributional Constrained Policy Optimization | **Distributional constrained reinforcement learning for supply chain optimization**. Jaime Sabal Bermúdez, Antonio del Rio Chanona, Calvin Tsay. **2023**. | [arXiv:2302.01727](https://arxiv.org/abs/2302.01727); [DOI:10.1016/B978-0-443-15274-0.50262-6](https://doi.org/10.1016/B978-0-443-15274-0.50262-6), publisher chapter identity corroborated by [Imperial's author manuscript record](https://spiral.imperial.ac.uk/entities/publication/2705c606-5f60-4bc1-b045-00532174659a). |
| C8 DCPO, Distribution-Centric Policy Optimization | **Distribution-Centric Policy Optimization Dominates Exploration-Exploitation Trade-off**. Zhaochun Li, Chen Wang, Jionghao Bai, Shisheng Cui, Ge Lan, Zhou Zhao, Yue Wang. **2026**. | [arXiv:2601.12730v1](https://arxiv.org/abs/2601.12730v1), January 19. |

**Excluded substitutions:** [Direct Preference Optimization](https://arxiv.org/abs/2305.18290)
and [Direct Preference-based Policy Optimization without Reward Modeling](https://arxiv.org/abs/2301.12842)
are preference-learning methods with different names/specifications. Their DPO/DPPO
abbreviations do not establish Dynamic Policy Optimization. Application papers using
“dynamic policy optimization” descriptively likewise do not define a syllabus canonical.

## Objectives and update rules

For comparison, define the clipped surrogate

$$
C(r,A;l,u)=\min(rA,\operatorname{clip}(r,l,u)A),\qquad
r=\pi_\theta(a\mid s)/\pi_{\rm old}(a\mid s).
$$

[Clipped PPO](https://arxiv.org/abs/1707.06347) maximizes
\(J_{\rm clip}=E[C(r,\hat A;1-\epsilon,1+\epsilon)]\), alongside a value objective.
For maximization below, the update *direction* is \(+\nabla_\theta J\);
for a loss it is \(-\nabla_\theta L\). Writing
\(\theta^+=\theta+\eta\nabla J\) or \(\theta^+=\theta-\eta\nabla L\)
specifies that direction, not a claim that every paper uses plain SGD.
Rollout policies, reference policies, rewards and routed labels must be frozen
appropriately during differentiation.

**C1 — interactive DyPO.** Paper equation (3), written with a single index u
over generated thinking/action tokens across turns:

$$
A_i=R_i-\frac1G\sum_jR_j,\qquad
J=E\!\left[\sum_i {\bf1}\{|y_i|<L_{\max}\}
              \sum_{u\in{\rm generated}(y_i)}
              C(r_{i,u},A_i;1-\epsilon,1+\epsilon)\right].
$$

Update in the \(+\nabla J\) direction. Environment observations condition the
policy but are excluded from the generated-token loss. Group advantages omit
standard-deviation division; no reference-KL penalty is retained. Auxiliary
resampling/rejection and thinking/action formatting belong to the method.
**Versus PPO:** multi-turn LLM interaction and group-relative credit, not the
existing learned-critic MDP recipe. [Primary equation and discussion, pp.3–5](https://openreview.net/pdf/3e0a9be58197962b8848e6ec3dd5de090da8bdc3.pdf).

**C2 — robust-reasoning DYPO.** Equations (4), (14)–(16):

$$
L=E[{\bf1}_{H}\gamma L_{\rm SFT}
       +{\bf1}_{M}(\alpha L_{\rm GRPO}+(1-\alpha)L_{\rm GAL})],
$$

$$
L_{\rm SFT}=E_{\tau\sim{\cal U}(\mathrm{teachers})}[-\log\pi_\theta(\tau|q)],
\quad L_{\rm GAL}=E[-\log\sigma(\beta d)],
\quad
d=\log\frac{\pi_\theta(\tau_s|q)}{\pi_{\rm ref}(\tau_s|q)}
 -\log\frac{\pi_\theta(\tau_f|q)}{\pi_{\rm ref}(\tau_f|q)}.
$$

$$
\nabla L_{\rm GAL}
=-\beta\{1-\sigma(\beta d)\}(\nabla\log\pi_s-\nabla\log\pi_f).
$$

Update in the \(-\nabla L\) direction. H: all binary rewards zero; M: mixed
success; all-success groups contribute zero. Here gamma scales supervision,
not MDP discount. **Versus PPO:** teacher supervision, reward-based routing and
an on-policy contrastive term. Appendix (21) uses a reference-policy ratio;
a future contract must pin that convention rather than silently substituting
PPO's old-policy denominator. [Primary equations](https://arxiv.org/html/2604.08926v1).
The [author release](https://github.com/Tocci-Zhu/DYPO/blob/main/README.md) also
documents reference-free fallback behavior; paper and code versions must be pinned.

**C3 — Dynamic Clipping DCPO.** Equations (4)–(8); let q be old token probability:

$$
l(q)=\tfrac12+\tfrac12\sqrt{\max(1-4\epsilon_l/q,0)},\qquad
u(q)=\tfrac12+\tfrac12\sqrt{1+4\epsilon_h/q}.
$$

$$
a_n=(R-\mu_n)/\sigma_n,\quad a_c=(R-\mu_c)/\sigma_c,\quad
s_n=((i-1)a_n+a_c)/i,\quad s_c=(a_n+(i-1)a_c)/i.
$$

Choose \(A=s_n\) when \(|s_n|<|s_c|\), otherwise \(s_c\);
cumulative statistics are per prompt. Maximize

$$
J=\sum_j |o_j|^{-1}\sum_t C(r_{j,t},A_j;l(q_{j,t}),u(q_{j,t})).
$$

Update \(+\nabla J\), freezing old probabilities/statistics. The experiments
also impose a ratio ceiling of10. **Versus PPO:** probability-dependent bounds,
smoothed historical advantages, no KL term and no response-group averaging.
Equation (8)'s epsilon notation is shorthand for section2's dynamic bounds.
Zero-variance conventions and ceiling placement require explicit agreement before
coding. [Primary version and equations](https://arxiv.org/html/2509.02333v2).

**C4 — Dynamic Proximal DPPO: specification incomplete.** The verified abstract
describes SLEA/BWEA entropy-coefficient adaptation and a C1 smooth clipping
function based on Taylor/exponential pieces. It differs from fixed-coefficient,
hard-clipped PPO. **The exact objective, piecewise function, coefficient recurrences
and their gradients could not be verified:** publisher full-text retrieval returned
403; accessible publisher excerpts omit them. No public author manuscript was
located in this search. Inventing a smoothing function would define a different
algorithm. An accessible author/publisher manuscript and selected SLEA/BWEA variant
are prerequisites. [Publisher evidence](https://www.sciencedirect.com/science/article/abs/pii/S0925231226002584).
This is an explicit gap in the requested equation comparison, not a verified
implementation specification.

**C5 — Distributed PPO.** Algorithm1 uses the adaptive-KL PPO variant:

$$
J=\sum_t r_t\hat A_t-\lambda D_{\rm KL}(\pi_{\rm old}\|\pi_\theta),\qquad
\lambda^+=
\begin{cases}
a\lambda & D_{\rm KL}>\beta_hD_{\rm target}\\
\lambda/a & D_{\rm KL}<\beta_lD_{\rm target}\\
\lambda & \mathrm{otherwise}.
\end{cases}
$$

Workers compute gradients; a chief averages accepted gradients and synchronizes
parameters. A conceptual synchronized step is
\(\theta^+=\theta+\eta W^{-1}\sum_w g_w\).
Supplement A.1 adds excessive-KL penalty/early stopping and shared statistics.
**Versus existing B8 clipped PPO:** distributed synchronization **and adaptive
KL regularization**, not simply parallelizing its clipped objective.
[Primary §2, Algorithm1, supplement A.1](https://arxiv.org/pdf/1707.02286).

**C6 — Diffusion DPPO.** The policy's action is a denoising transition:

$$
\bar\pi_\theta(a_t^k|a_t^{k+1},s_t)
={\cal N}(a_t^k;\mu_\theta(a_t^{k+1},s_t,k+1),\sigma_{k+1}^2I),
$$

$$
r_{t,k}=\bar\pi_\theta/\bar\pi_{\rm old},\quad
\hat A_{t,k}=\gamma_{\rm denoise}^{k}(G_t^{\rm env}-\tilde V(s_t)),\quad
J=E[C(r_{t,k},\hat A_{t,k};1-\epsilon,1+\epsilon)].
$$

Update \(+\nabla J\); the critic fits environment returns. Actual environment
rewards occur after the final denoising step; internal transitions have zero
immediate reward. **Versus PPO:** a two-level denoising/environment MDP, Gaussian
transition likelihoods and denoising discounts; not an ordinary Gaussian actor.
Pretraining/selected denoising steps/noise floors matter.
[Primary equations (4.1)–(4.8)](https://arxiv.org/html/2409.00588v3).

**C7 — Distributional Constrained DCPO.** Target:
\(\max_\pi J_R(\pi)\) subject to \(J_C(\pi)\le d\) and a local KL trust region.
Distributional reward/cost heads are fitted using the paper's likelihood loss.
Confidence reshapes the constraint:

$$
\rho=\begin{cases}\beta P(Z_C>d)&J_C>d\\-\beta P(Z_C<d)&J_C\le d,\end{cases}
\quad \kappa=1+\max(\rho,-\varepsilon),\quad
\tilde J_C=\kappa J_C,\quad\tilde d=\kappa d.
$$

The paper gives
\(x^*=-H^{-1}(g-\nu^*b)/\lambda^*\), followed by backtracking;
infeasibility triggers a cost-reduction recovery direction.
**Versus PPO:** constrained natural-gradient/dual optimization and distributional
critics, not clipped-ratio ascent. Equation (4)'s minimization/sign and trust-region
normalization must be reconciled with its reward-maximization description before
implementation. [Primary §III, equations (3)–(8), Algorithm1](https://arxiv.org/pdf/2302.01727).

**C8 — Distribution-Centric DCPO.** Section3.3 combines group advantage with a
temperature-target-weighted reward term:

$$
\rho_{i,t}=\pi_{\rm old}^{T}(o_{i,t}|h)/\pi_{\rm old}(o_{i,t}|h),\quad
B_{i,t}=\hat A_i+\alpha\rho_{i,t}R_i,\quad
J=E\!\left[\frac1G\sum_i\frac1{|o_i|}\sum_t
 C(r_{i,t},B_{i,t};1-\epsilon,1+\epsilon)\right].
$$

Update \(+\nabla J\), freezing rollout-derived terms. **Versus PPO:** group-relative
LLM credit and a virtual target distribution, not adaptive clipping. The temperature
normalization is inconsistent in the displayed HTML formula; a future specification
must verify the normalized distribution and gradient stopping against pinned code.
Token-wise importance sampling alone must not be asserted to correct arbitrary
trajectory-distribution shifts. [Primary §3.2–3.3 and equation(7)](https://arxiv.org/html/2601.12730v1).

## Implementation cost and independent oracle plan

The following are **engineering estimates for a separately approved educational
scope**, not measured runtimes or reproduced paper results. No packages were
installed and no training data, weights or reference code were downloaded.

Let B be rollout tokens/transitions, P model parameters, K denoising steps,
V vocabulary size and W workers.

| Candidate | Cost/dependencies and feasibility estimate | Independent tests required before a tested status |
| --- | --- | --- |
| C1 | High integration cost: multi-turn token masks, grouped sampling/rejection; roughly O(BP). Tiny categorical NumPy environment possible only as an explicitly approved reduced scope. Full LLM reproduction needs a language-model stack, weights and interactive environments. | Enumerate a tiny dialogue tree; hand group baselines; observation-token zero gradients; length rejection/resampling; fixed-rollout finite differences. |
| C2 | High: teachers, reference probabilities, routing and contrastive pairs; up to O(G²) pairing plus model work. Tiny supplied teacher tables could avoid heavyweight dependencies but do not reproduce LLM benchmarks. | All-zero/all-one/mixed routing fixtures; enumerate teacher expectation; independent pairwise logistic gradient and finite differences; zero easy-group contribution. |
| C3 | Moderate mathematical core, high LLM integration; O(BP), cumulative state per prompt. NumPy softmax toy is plausible; [author workflow](https://github.com/lime-RL/DCPO) uses a pretrained-model/GPU stack and downloads, which current policy does not authorize. | Hand bounds at rare/common q; both advantage signs; raw-history versus online statistics; tie/zero variance/ratio-cap cases; finite differences away from kinks. |
| C4 | Unknown until exact recurrences are accessible; likely moderate PPO extension. CPU NumPy educational feasibility is an inference, not a verified reproduction path. Publisher experiments use PyBullet. | First obtain equations; then prove matching piece values/derivatives at joins, exact entropy coefficient recurrences, actor/critic gradient differences and reduction cases. |
| C5 | Moderate/high: O(BP) total compute plus O(WP) copies/aggregation per synchronization. NumPy plus standard-library concurrency is plausible; original system used TensorFlow/parameter servers. Recurrent parity would add substantial scope. | Independent KL derivatives/adaptation thresholds; hand mean-gradient global step; stale-gradient rejection; synchronization, normalization, failure/shutdown and one-worker equivalence. |
| C6 | High: about O(BKP), denoising state storage, Gaussian likelihoods and optional synthetic pretraining. NumPy tiny analogue possible; robotics/pretrained-policy reproduction needs separately approved dependencies/data. | Hand Gaussian log ratios; enumerate two-level rewards/discounts; every denoiser gradient; fixed-noise finite differences; last-step-only updates and critic targets. |
| C7 | High: reward/cost distributions, Hessian-vector or dense Fisher solve, dual/recovery/line search. A dense P-parameter solve costs O(P³); iterative cost depends on iterations. NumPy toy plus SciPy test reference is plausible. | Enumerated CMDP optimum; exact finite cost probabilities; low-dimensional quadratic/KKT oracle; feasible/infeasible recovery and line search; likelihood/actor finite differences. |
| C8 | Moderate mathematical core plus O(BV) target-distribution work if full vocabulary is materialized; high LLM integration. NumPy finite-action analogue requires approved scope. | Independently normalized temperature distribution; exact conditional importance expectation; T=1/alpha=0 reductions; group-credit calculations and frozen-target finite differences. |

All learning checks would be bounded, multi-seed and separate from mathematical
oracles. Toy convergence would not establish the papers' benchmark claims.
Any adopted version needs an approved contract covering masks, reductions, bootstrap
rules, reference/old snapshots, optimization, numerical edge cases and resource limits.
No hypothetical tests above were executed or presented as passing.

## Decision for the owner

| Outcome | Assessment |
| --- | --- |
| 1. Adopt a verified Dynamic Policy Optimization method | C1/C2 establish that this exact expansion exists, but neither is linked to the original syllabus. Selecting one would be a deliberate new interpretation with substantial LLM-specific scope. |
| 2. Correct to an explicitly named algorithm | C5 Distributed Proximal Policy Optimization is the best general-RL fit among the inspected candidates. C4 Dynamic Proximal PPO is another fit hypothesis but lacks recovered equations. Both require an explicit owner-approved correction; neither can be silently renamed DPO. |
| **3. Keep blocked — recommended** | Preserves syllabus provenance and avoids inventing intent. Revisit when the owner selects a cited, versioned specification or supplies the original defining reference. |

**Owner decision: approved — remain blocked.** The owner stated: “I explicitly approve
Outcome 3 — Keep Dynamic Policy Optimization (DPO) Blocked.” No algorithm adoption,
substitution or implementation is authorized. Any future change requires a separate
explicit owner decision. Phase 20 implementation review remains pending until the
owner reviews the regenerated final package.

The original investigation changed only this decision document. This owner-approved
finalization updates Phase 20 approval/progress records and regenerates its package;
prior packages are retained as historical evidence. Canonical ID/path, all four
blocked statuses, original syllabus fixture and nine implementations remain unchanged.
No Phase 21, commit, push or release is authorized.

Original investigation validation (historical): catalog/link validation and
generated-document check passed. The prior ZIP checksum was reverified; its recorded
extracted full suite is3841 passed. The full suite was not rerun for this report.
This document is a specification decision record, not an algorithm lesson or a new
phase completion report; development.completion_report remains unchanged.
