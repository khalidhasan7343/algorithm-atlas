# Locked catalog scope — Phases 11 and 12

Before implementation, the current catalog was verified to contain 35 categories,
256 original memberships and 235 canonicals. These ten entries are all planned
at authorization. No canonical is owned by another category; related links below
are conceptual references, not duplicate memberships. The owner explicitly approved
completed Phase 10 on 2026-10-24 (Asia/Dhaka), superseding the attachment’s stale
approval precondition. Phase 9 remains owner-approved. Phases 11 and 12 are
jointly authorized for implementation, with independent pending owner approvals.

| Category | ID | Phase | Display name | Canonical ID | Canonical directory | Starting tests | Related references |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| Mathematical and Number Theory | A9 | 11 | Sieve of Eratosthenes | `sieve-of-eratosthenes` | `dsa/number-theory/sieve-of-eratosthenes/` | planned | euclidean-algorithm, least-common-multiple; memberships: A9 |
| Mathematical and Number Theory | A9 | 11 | GCD using Euclidean Algorithm | `euclidean-algorithm` | `dsa/number-theory/euclidean-algorithm/` | planned | sieve-of-eratosthenes, least-common-multiple; memberships: A9 |
| Mathematical and Number Theory | A9 | 11 | LCM | `least-common-multiple` | `dsa/number-theory/least-common-multiple/` | planned | sieve-of-eratosthenes, euclidean-algorithm; memberships: A9 |
| Mathematical and Number Theory | A9 | 11 | Modular Exponentiation | `modular-exponentiation` | `dsa/number-theory/modular-exponentiation/` | planned | sieve-of-eratosthenes, euclidean-algorithm; memberships: A9 |
| Mathematical and Number Theory | A9 | 11 | Fast Exponentiation | `fast-exponentiation` | `dsa/number-theory/fast-exponentiation/` | planned | sieve-of-eratosthenes, euclidean-algorithm; memberships: A9 |
| Mathematical and Number Theory | A9 | 11 | Extended Euclidean Algorithm | `extended-euclidean-algorithm` | `dsa/number-theory/extended-euclidean-algorithm/` | planned | sieve-of-eratosthenes, euclidean-algorithm; memberships: A9 |
| Mathematical and Number Theory | A9 | 11 | Prime Factorization | `prime-factorization` | `dsa/number-theory/prime-factorization/` | planned | sieve-of-eratosthenes, euclidean-algorithm; memberships: A9 |
| Two Pointers and Sliding Window | A10 | 12 | Two Sum in Sorted Array | `two-sum-sorted-array` | `dsa/two-pointers-and-sliding-window/two-sum-sorted-array/` | planned | sliding-window-maximum, longest-substring-without-repeating-characters; memberships: A10 |
| Two Pointers and Sliding Window | A10 | 12 | Sliding Window Maximum | `sliding-window-maximum` | `dsa/two-pointers-and-sliding-window/sliding-window-maximum/` | planned | two-sum-sorted-array, longest-substring-without-repeating-characters; memberships: A10 |
| Two Pointers and Sliding Window | A10 | 12 | Longest Substring Without Repeating Characters | `longest-substring-without-repeating-characters` | `dsa/two-pointers-and-sliding-window/longest-substring-without-repeating-characters/` | planned | two-sum-sorted-array, sliding-window-maximum; memberships: A10 |

Stage A: Sieve, GCD, LCM. Stage B: Modular/Fast Exponentiation, Extended Euclid,
Prime Factorization. Stage C: Two Sum. Stage D: Sliding Maximum and Longest
Distinct Substring. Complete every lesson/test/gate before advancing. Stage B
must finish all Number Theory targeted tests before Stage C.

See [Number Theory checkpoints](number-theory-checkpoints.md) and
[Window checkpoints](two-pointers-sliding-window-checkpoints.md). No Phase 13,
commit, push or publication is authorized. No third combined ZIP is requested.
