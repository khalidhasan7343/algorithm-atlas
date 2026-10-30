# Phase 17 — locked B5 scope

Owner: **MD.Khalid Hasan**, MIT. Owner statement: “Approved pervious work and review done.now follow this properly”. Client session date: 2026-10-30 Asia/Dhaka. Phase 16 ZIP SHA256 df8bb7c03e463aed7ff6d342a3ffa77a5214b2dc1d1d25f06e632de985974e3a verified; historical pending metadata is preserved.

| Batch | Exact canonical IDs | Contract |
| --- | --- | --- |
| 1 | singular-value-decomposition; principal-component-analysis | Reduced one-sided Jacobi SVD; centered PCA reuses it |
| 2 | linear-discriminant-analysis-projection; independent-component-analysis | Fisher scatter projection; parallel tanh FastICA |
| 3 | t-sne; umap | Exact dense perplexity/KL embedding; exact fuzzy kNN UMAP with full cross-entropy |
| 4 | vanilla-autoencoders | Single hidden bottleneck tanh encoder, linear decoder, NumPy backprop |

Six canonicals live under machine-learning/unsupervised-learning/dimensionality-reduction. vanilla-autoencoders retains category B7 and path machine-learning/deep-learning/vanilla-autoencoders; B5 and B7 link to that one implementation. Other B7 algorithms remain deferred. LDA projection is supervised and distinct from the preserved B2 classifier.

No new IDs, memberships, paths or unrelated algorithms. Keep DPO blocked. No heavy frameworks, datasets, model files, dummy C++, commits/publication, Phase 18 or B6. All four batches precede one Phase 17 owner-review stop. [Checkpoints](dimensionality-reduction-checkpoints.md).
