# String Algorithms review package

Phase 9 contains nine canonical A7 String Algorithms. Owner: **MD.Khalid Hasan**;
MIT license. **Owner approval: pending.** See the
[review report](../../../docs/reviews/string-algorithms/STRING-ALGORITHMS-REVIEW-REPORT.md)
and [sequential evidence](../../../docs/string-algorithms-checkpoints.md).

Review files:

- `algorithm-atlas-string-algorithms-review.zip`
- `algorithm-atlas-string-algorithms-review.zip.sha256`
- `algorithm-atlas-string-algorithms-review.json`

From this directory verify with:

```sh
shasum -a 256 -c algorithm-atlas-string-algorithms-review.zip.sha256
```

The source-only ZIP includes the updated source, tests, catalog, documentation,
current execution evidence and historical review reports. It excludes .git,
virtual environments, caches, binaries, secrets, all nested ZIPs and unnecessary
review-package JSON/checksum sidecars. Historical packages remain unchanged in
the working repository; their omission from this new ZIP is intentional.

The external JSON records the archive digest, CRC, safe paths, required files,
per-file hashes, extracted-source checks and actual language/regression results.
It cannot be included inside its own archive without a circular hash.

Reproduce from the repository root:

```sh
.venv/bin/python scripts/package_string_algorithms_review.py
```

Creation refuses to overwrite an existing archive. The packager includes
tracked and unignored new source files, so a commit is not required. Hosted
GitHub Actions was not triggered or verified. Stop for explicit Phase 9 owner
review; no next category, commit, push or publication is authorized.
