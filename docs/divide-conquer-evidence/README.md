# Phase 4 local verification evidence

`approved-baseline.json` records the starting revision and hashes of 142 prior
Sorting, Searching, and Recursion/Backtracking files, including category navigation.
`preservation-results.json` compares them and preserves the seven A4 memberships
and all canonical identities. `catalog-baseline.yaml` preserves the hash-checked original catalog so scope verification also works from an extracted ZIP without Git metadata. Four new topics and three reuses are counted separately.

The request listed six memberships; the authoritative catalog also contains
Binary Search. It is reused at dsa/searching/binary-search, without a new folder.
`reused-tests.txt` records the executed canonical Merge/Quick/Binary suites.

Run bounded verification from the repository root:

```sh
.venv/bin/python scripts/run_divide_conquer_validation.py --stage batch1
.venv/bin/python scripts/run_divide_conquer_validation.py --stage batch2
.venv/bin/python scripts/run_divide_conquer_validation.py --stage final
CXX='clang++ -fsanitize=address,undefined -fno-sanitize-recover=all' .venv/bin/python scripts/run_divide_conquer_validation.py --stage sanitizer
.venv/bin/python scripts/verify_divide_conquer_scope.py
.venv/bin/python scripts/verify_divide_conquer_examples.py
.venv/bin/python scripts/run_divide_conquer_validation.py --stage configuration
```

Each stage saves actual commands, exit codes, elapsed time and timeout flags in
JSON and separate text transcripts. Child commands are bounded at 240 seconds;
compilation and execution use additional fixture-specific limits. Marked language
selection deselects other cases; deselection is not a failure, skip, or a pass.
No hosted GitHub Actions result is inferred from local tests.

After report and evidence are frozen, `scripts/package_divide_conquer_review.py`
builds the complete review source snapshot, checks required files, byte equality,
safe paths, CRC and extracted catalog/generated-doc configuration, then emits
SHA-256 and verification sidecars. Git metadata, environments, caches, binaries,
private files and other archives are excluded. It refuses to overwrite artifacts.

All development stops for explicit owner review after packaging. No human approval,
other-category implementation, commit, push, or publication is implied by tests.

The [Phase 4 review report](../../DIVIDE-CONQUER-REVIEW-REPORT.md) summarizes contracts, actual results and limits. `changed-files.txt` lists the source/documentation/evidence delta; archive hashes and integrity checks are in the external ZIP verification sidecar.
