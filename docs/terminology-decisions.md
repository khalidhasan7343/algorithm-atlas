# Terminology and canonicalization decisions

This record keeps syllabus interpretation visible. Catalog names preserve the original roadmap; a scope note or canonical link does not silently remove a syllabus item.

## Dynamic Policy Optimization — decision required

The reinforcement-learning syllabus says **"Dynamic Policy Optimization (DPO, terminology as written in original notes)"**. Its intended source is not supplied. The topic remains `blocked` until the maintainer identifies the intended paper, course, or mathematical definition. This blocks that future lesson, not the Phase 0 foundation.

A terminology check on **2026-10-20** found multiple research uses of the name:

| Candidate | Primary source | Distinction |
| --- | --- | --- |
| DyPO for multi-turn interactive reasoning | Feng et al., [DyPO: Dynamic Policy Optimization for Multi-Turn Interactive Reasoning](https://openreview.net/pdf/3e0a9be58197962b8848e6ec3dd5de090da8bdc3.pdf) | Extends GRPO for interaction with dynamic environments. |
| DYPO for robust reasoning | Zhu et al., [Bridging SFT and RL: Dynamic Policy Optimization for Robust Reasoning](https://arxiv.org/abs/2604.08926) | Combines supervised and reinforcement-learning objectives with dynamic gating. |
| Direct Preference Optimization | Rafailov et al., [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) | A separately named preference-learning method commonly abbreviated DPO. |

These sources establish that the phrase alone does not uniquely identify the intended lesson. They do not establish which method the handwritten notes meant. No candidate has been adopted, and Direct Preference Optimization has not replaced the requested topic.

**Maintainer decision needed:** provide the intended reference or confirm a specific method before this topic's implementation phase.

## Canonical folders and meaningful variants

The catalog preserves every category occurrence while storing each unique algorithm once. Merge Sort and Quick Sort therefore appear in sorting and divide-and-conquer navigation, and BFS/DFS appear in DSA graphs and AI search navigation. Similar reuse applies to repeated shortest-path, spanning-tree, optimization, and neural-network topics.

Names alone are insufficient for deciding identity. Preserve separate folders for meaningful variants, such as backtracking versus dynamic-programming Subset Sum, HMM POS tagging versus a general HMM, and LDA classification versus its supervised dimensionality-reduction formulation. Cross-link their records and document shared prerequisites. Synonyms such as exhaustive search and brute-force search can share a canonical folder when the scope note explains the equivalence.

See [catalog.yaml](../catalog.yaml) for per-record scope notes and the [complete index](algorithm-index.md) for every original category label.
