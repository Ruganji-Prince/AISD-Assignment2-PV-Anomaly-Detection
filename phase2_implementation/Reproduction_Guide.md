# Preprocessing reproduction

From the repository root, use Python 3.14.7 and the existing pinned preprocessing dependency subset:

```text
python -m venv .venv
python -m pip install -r phase2_implementation/requirements.txt
python -B phase2_implementation/execute_preprocessing.py
python -B phase2_implementation/verify_submission.py
```

Activate the environment before installing: Windows `.venv\Scripts\Activate.ps1`; POSIX `source .venv/bin/activate`. The executable notebook can alternatively be opened in a compatible Jupyter frontend. The Python entry point executes its code cells without requiring Jupyter.

Execution loads the immutable raw CSV, validates schema/quality, constructs the original ordered partitions, fits preprocessing only on TRAIN, transforms held-out partitions, and recomputes descriptive TRAIN association/PCA statistics. No classifier or prediction interface is included. Output arrays remain in memory. The notebook and compact preprocessing evidence are updated; the eight existing figures are checked and displayed, not regenerated. The reference scientific values must match within documented floating-point tolerance. Source index and labels never enter predictors. No model binaries, caches or original publication manifests are required.

The [historical Phase 1 verifier](../phase1_strategy/verify_phase1.py) retains its original Phase 1-only snapshot scope; use the current preprocessing verifier for this candidate. Optional original Phase 1 audit reproduction uses `python -B phase1_strategy/reproduce_audit.py`; it downloads pinned MAT data into an isolated ignored directory and requires network access.
