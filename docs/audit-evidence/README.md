# Final Sorting audit evidence

These are local execution records from 2026-10-21, not hosted CI results.
Run the commands from the repository root using the project's Python environment.
The runner normalizes its interpreter name to `python` in logs; the actual run
used `.venv/bin/python`. Each child command has a 120-second outer timeout.

```sh
.venv/bin/python scripts/run_sorting_verification.py --stage individual --output docs/audit-evidence --timeout 120
.venv/bin/python scripts/run_sorting_verification.py --stage groups --output docs/audit-evidence --timeout 120
CXX='clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all' .venv/bin/python scripts/run_sorting_verification.py --stage sanitizer --output docs/audit-evidence --timeout 120
```

The `individual` stage ran the original suites before adding independent tests.
The `groups` stage includes the new tests. Re-running these commands replaces
their corresponding evidence files with the newly observed results. The final
report preserves the outcomes observed for this review snapshot.

- [Original individual suite results](individual-results.json): 11 separately logged runs.
- [Grouped results](groups-results.json): Python, C++17, C++20, infrastructure, full suite, catalog, and generated docs.
- [Sanitizer results](sanitizer-results.json): selected C++20 tests; requires the stated compiler flags.
- [Environment](environment.json): interpreter, dependencies, compiler, architecture, and baseline commit.
- [Source inventory](source-audit.json): all 22 implementation SHA-256 hashes and numbered lesson section counts.

Each result has a corresponding plain-text transcript. `deselected` means a
test was intentionally outside that command's marker or language-standard
selection; it does not mean a skipped or passed test. Counts describe pytest
cases. Exhaustive vectors checked inside a single case are reported separately.

The inventory confirms that all implementation files match the baseline commit.
Source review additionally checked that the actual lesson code performs each
algorithm directly. Tim Sort calls its own `_TimSorter.sort()` method; this is
not delegation to Python's built-in list sorting.

See [the final audit report](../reviews/sorting/SORTING-FINAL-AUDIT-REPORT.md) for findings,
limitations, full commands, and the mandatory human-review checkpoint.
