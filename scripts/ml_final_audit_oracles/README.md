# Phase26 independent ML oracles

Thirteen self-contained scripts (one per B category) recompute each implemented canonical's mathematics from closed forms, brute-force enumeration, finite differences, hand calculations or external references (NumPy/SciPy/scikit-learn, used only as references). They never import repository tests. Run `python scripts/run_ml_final_audit_oracles.py` from the repository root; results are written to `docs/ml-final-audit-evidence/oracle-results.json`.
