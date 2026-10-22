# searching review package

The following existing files were moved here without changing their bytes:

- `algorithm-atlas-searching-review.zip`
- `algorithm-atlas-searching-review.zip.sha256`
- `algorithm-atlas-searching-review.zip.verification.json`

ZIP size: 810606 bytes. SHA-256: `0f6e70a8b915c6cc0550f465b525b12a56a53aa5094a89401de0c614d288dbe3`. Tracking at cleanup: tracked. The [maintenance report](../../../docs/maintenance/root-cleanup/REPORT.md) records verification. These archives are historical source snapshots; their internal root paths and manifests deliberately retain the original layout.

From this directory, verify with:

```sh
shasum -a 256 -c algorithm-atlas-searching-review.zip.sha256
```

From the repository root, `python scripts/verify_root_cleanup.py` verifies all locally available expected packages, checksums, metadata and CRC. In a tracked-only checkout it can use `--tracked-only` to account explicitly for local untracked artifacts.
