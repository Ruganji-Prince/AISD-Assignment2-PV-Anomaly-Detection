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

## IEEE reflection report

The current reflection report is [Assignment3_Phase2.pdf](reports/Assignment3_Phase2.pdf). The [LaTeX source](reports/Assignment3_Phase2.tex), [unmodified IEEEtran class](reports/IEEEtran.cls), [class README/license information](reports/IEEEtran_README.txt) and [template provenance](reports/IEEE_Template_Provenance.json) are included. It uses the official conference class with a two-column body, not a simulated page layout.

The notebook also writes measured per-stage partition dimensions, TRAIN distribution/outlier diagnostics, scaling summaries, PCA eigenvalues and an empirical-audit record under `phase2_implementation/compliance/`. Existing Phase 1 scientific files and reference preprocessing values remain unchanged. The 300-DPI diagnostic images reside in root `figures/`; they are checked rather than regenerated.

To regenerate only the report, install a standard Tectonic LaTeX compiler on PATH, then run from the root:

```text
python -B phase2_implementation/reports/build_report.py
```

Alternatively pass `--compiler` with the installed Tectonic executable path. The command regenerates the IEEE source and reflection table from compact preprocessing CSV/JSON, compiles in a temporary directory, and updates the PDF plus report verification metadata. It does not execute the notebook, fit preprocessing, regenerate figures or access downstream work. Initial compilation may download standard TeX packages/fonts; later builds can reuse the compiler cache. PDF timestamps/identifiers may vary between builds; source content, numerical evidence and figure bytes are the reproducibility targets.

Canvas submission requires the PDF named `Assignment3_Phase2.pdf` and the live repository URL. No submission action is performed by these commands.
