# Tree Algorithms review package

Phase 8 contains all fourteen canonical Tree Algorithms. Owner: **MD.Khalid Hasan**; MIT license. Approval is pending. See the [Tree review report](../../../docs/reviews/tree-algorithms/TREE-ALGORITHMS-REVIEW-REPORT.md) and [execution checkpoint](../../../docs/tree-algorithms-checkpoints.md).

Review files:

- `algorithm-atlas-tree-algorithms-review.zip`
- `algorithm-atlas-tree-algorithms-review.zip.sha256`
- `algorithm-atlas-tree-algorithms-review.json`

Verify the checksum from this directory:

```sh
shasum -a 256 -c algorithm-atlas-tree-algorithms-review.zip.sha256
```

The JSON records actual test results, archive CRC, per-file hashes, extracted validation and approval status. The ZIP contains complete source, documentation, tests and historical reports. Old ZIPs and associated package sidecars, including its own ZIP/checksum/JSON, are excluded to avoid nesting and circular hashes. Source-only extraction checks explicitly account for omitted historical package files while checking every included protected source/evidence byte.

Reproduce creation from the repository root after reviewing/staging the source snapshot:

```sh
.venv/bin/python scripts/package_tree_algorithms_review.py
```

The script refuses to overwrite an existing archive. Local validation does not establish a hosted GitHub Actions result. No next category, commit, push or publication is authorized by this handoff.
