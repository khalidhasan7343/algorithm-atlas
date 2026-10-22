# Searching execution evidence

These are actual local Phase 2 results, not hosted GitHub Actions results.
The owner approved Sorting before authorizing this Searching-only phase.

- [Batch 1](batch1-results.json): Linear, Binary, Jump; catalog, generated docs,
  and full suite. This gate passed before Batch 2 implementation began.
- [Batch 2](batch2-results.json): Interpolation, Exponential, Ternary, catalog,
  and generated docs.
- [Final grouped runs](final-results.json): Python, C++17, C++20, infrastructure,
  full suite, catalog, and generated docs.
- [Sanitizers](sanitizer-results.json): all Searching C++20 cases with ASan/UBSan
  and recovery disabled.
- [Environment](environment.json): versions, compiler, platform, seed, and baseline.
- [Inventory](inventory.json): source/test/lesson hashes and preserved Sorting files.
- [README examples](readme-examples.json): exact commands, outputs, and exit codes.
- [Files changed](files-changed.txt): complete repository-relative path list.

Each gate also retains a separate `.txt` transcript per command. The runner uses
the actual current interpreter but displays it as portable `python` in logs;
the observed runs used `.venv/bin/python`. Every child gate has a 180-second
timeout, compilation 60 seconds, new API executions 30 seconds, and CLI/helper
executions 10 seconds. `deselected` is intentional marker/standard selection and
must not be counted as a pass or a skip.

```sh
.venv/bin/python scripts/run_searching_validation.py --stage batch1
.venv/bin/python scripts/run_searching_validation.py --stage batch2
.venv/bin/python scripts/run_searching_validation.py --stage final
CXX='clang++ -fsanitize=address,undefined -fno-omit-frame-pointer -fno-sanitize-recover=all' .venv/bin/python scripts/run_searching_validation.py --stage sanitizer
.venv/bin/python scripts/run_searching_validation.py --stage configuration
```

Commands replace their corresponding logs when rerun. Compilation and execution
must both succeed. The batch runner stops on failure or timeout and never advances
a failed gate. The saved [checkpoint](../searching-checkpoints.md) and
[review report](../reviews/searching/SEARCHING-REVIEW-REPORT.md) explain results and limitations.
