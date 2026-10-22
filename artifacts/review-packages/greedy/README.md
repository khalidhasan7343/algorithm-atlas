# greedy review package

The following existing files were moved here without changing their bytes:

- `algorithm-atlas-greedy-review.zip`
- `algorithm-atlas-greedy-review.zip.sha256`
- `algorithm-atlas-greedy-review.zip.verification.json`

ZIP size: 1338178 bytes. SHA-256: `32ef9b748ebe2ba0be7a664af75d21f4f5d81d6af5396f92517b2bd32b625f7c`. Tracking at cleanup: tracked. The [maintenance report](../../../docs/maintenance/root-cleanup/REPORT.md) records verification. These archives are historical source snapshots; their internal root paths and manifests deliberately retain the original layout.

From this directory, verify with:

```sh
shasum -a 256 -c algorithm-atlas-greedy-review.zip.sha256
```

From the repository root, `python scripts/verify_root_cleanup.py` verifies all locally available expected packages, checksums, metadata and CRC. In a tracked-only checkout it can use `--tracked-only` to account explicitly for local untracked artifacts.
