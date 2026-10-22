# Phase 3 local verification evidence

`approved-baseline.json` records the starting Git revision and SHA-256 hashes of
87 approved Sorting/Searching source, test, and individual lesson files.
Category navigation is generated separately. Final verification compares these
bytes again; metadata edits do not authorize changes to approved algorithms.

Run bounded gates from the repository root:

```sh
.venv/bin/python scripts/run_backtracking_validation.py --stage batch1
.venv/bin/python scripts/run_backtracking_validation.py --stage batch2
.venv/bin/python scripts/run_backtracking_validation.py --stage batch3
.venv/bin/python scripts/run_backtracking_validation.py --stage final
.venv/bin/python scripts/verify_backtracking_scope.py
.venv/bin/python scripts/verify_backtracking_examples.py
.venv/bin/python scripts/run_backtracking_validation.py --stage configuration
CXX='clang++ -fsanitize=address,undefined -fno-sanitize-recover=all' .venv/bin/python scripts/run_backtracking_validation.py --stage sanitizer
```

Each stage writes JSON command/exit/elapsed/timeout records and individual text
transcripts. A failed stage stops before dependent work. Stage logs describe the
snapshot at that checkpoint; final logs describe the completed category.
`initial-missing-historical-reports.txt` retains the initial failed link check,
whose stale references were corrected without fabricating the missing reports.

Local passes are not hosted GitHub Actions results. Only the locally executed
interpreter, compiler, platform, and language standards are covered. No remote
workflow, commit, push, publication, or Phase 3 human approval is claimed.

The final [review report](../reviews/recursion-backtracking/RECURSION-BACKTRACKING-REVIEW-REPORT.md) summarizes actual results and limitations. `changed-files.txt` lists the source/evidence delta. ZIP file hashes, counts, CRC and extracted validation results are in the external `.zip.verification.json` sidecar; checksum verification uses the `.zip.sha256` sidecar.

## Renewed verification after historical-report recovery

`revalidation/final-results.json` and `revalidation/sanitizer-results.json` contain the fresh runs. `revalidation/configuration-results.json` records the final configuration gate. `revalidation/requirements-audit.md` maps the requested correctness requirements to the inspected contracts and independent tests. `revalidation/deliverables.json` checks every required lesson section and source/test path. All three restored originals are included in the refreshed package; their recovery hashes are in `revalidation/recovered-reports.json`. The initial missing-report transcript is retained only as historical evidence.
