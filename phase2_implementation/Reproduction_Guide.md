# Phase 2 reproduction and evidence inspection

## Frozen environment and data

The reference environment is Python 3.14.7 on Windows 11, using NumPy 2.5.4, pandas 3.0.6, SciPy 1.18.1, scikit-learn 1.9.1, LightGBM 4.7.0 and matplotlib 3.11.2. The complete dependency lock is `stage1/requirements-stage1-lock.txt`; `requirements.txt` includes that lock. No SHAP package is necessary for native LightGBM Tree SHAP.

The original-author dataset is pinned at commit `e9ed8ad8072dcb3ffc643b0f3604219798708551`: https://github.com/clayton-h-costa/pv_fault_dataset. The associated study is https://doi.org/10.3390/s20174688. The unchanged CSV is `data/raw/pv_fault_dataset.csv`, SHA-256 `717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a`. Phase 1 source/license/provenance remain unchanged. The CSV has 1,373,798 rows and seven columns, with six predictors and nominal `f_nv`.

## Scientific specification index

| Contract | Authoritative repository-relative location |
| --- | --- |
| Raw provenance/license | `data/raw/README.md`; `phase1_strategy/primary_source_manifest.json`; `phase1_strategy/PRIMARY_SOURCE_LICENSE.txt` |
| Split intervals/blocks | `phase1_strategy/Phase1_Split_Manifest.json` |
| Training-only class counts/weights | `stage1/evidence/class_weights.json` |
| Bounded search/model selection | `stage1/evidence/experiment_configuration.json`; `stage1/evidence/validation_comparison.csv`; `stage1/evidence/stage1_selection.json` |
| Feature definitions and dependencies | `stage1/Feature_Dependencies.json`; `src/phase2_stage1/features.py` |
| Sensor configurations and fixed settings | `src/phase2_stage2/contracts.py`; `stage2/evidence/feature_availability_by_configuration.json`; `stage2/evidence/frozen_stage1_settings.json` |
| Complete final fitted-model specifications | `stage4/evidence/final_model_specifications.json` |
| Threshold selection/freeze chronology | `stage3/evidence/stage3_protocol.json`; `stage3/evidence/stage3_threshold_selection.json`; `stage3/evidence/threshold_freeze_receipt.json`; `stage3/evidence/test_access_started.json` |
| Evaluation definitions | `src/phase2_stage1/evaluation.py`; `src/phase2_stage3/common.py` |
| Corrected resource protocol/samples | `stage2/evidence/measurement_protocol.json`; `stage2/evidence/resource_benchmark_correction.json`; `stage4/evidence/resource_protocol_public.json` |
| Dropout/explanation samples and seeds | `stage2/evidence/isolated_dropout_validation.json`; `stage3/evidence/dropout_validation.json`; `stage3/evidence/explainability_metadata.json` |

Paths beginning `stage1/`, `stage2/`, `stage3/` or `stage4/` in this table are relative to `phase2_implementation/`; `src/`, `data/` and `phase1_strategy/` paths are relative to the repository root. Random seed is 42; E4 dropout channel seed is 44. Model weights/features/settings never change after selection. Block 13 selects models; block 14 selects hardware-score thresholds. Test is never used for revised tuning. Prior legacy exposure is disclosed in `stage3/Methodology_Disclosure.md`.

## Evidence-only review

After installing the frozen dependencies as described in the [Phase 2 README](README.md), execute from the repository root:

```powershell
python -B phase2_implementation/verify_submission.py
```

This portable check validates approved public-file hashes, report/table consistency, confusion-derived class metrics, same-family degradation, engineering flags, training weights, threshold chronology, selected figure populations, raw-data integrity and relative Markdown links. It does not load trusted-local pickles, regenerate predictions or claim to recompute AP from ranking scores unavailable in the public bundle. Ranking/AP results remain protected by approved evidence hashes and the recorded earlier verifier. Host-dependent timings are not expected to reproduce byte-for-byte on different hardware.

The evidence-review notebook is already executed. Its cells only read the frozen CSV/JSON evidence and calculate descriptive checks; no estimator is fitted. The notebook can be rerun using any Jupyter front end with the pinned review environment. A Jupyter front end is optional and is not part of the model dependency lock; the standard Python notebook builder executes the same evidence-only cells without requiring Jupyter.

## Independent experimental reproduction

The modular experiment entry points are `run_stage1.py`, `run_stage2.py`, and `run_stage3.py freeze` followed by `run_stage3.py test`; corresponding analysis/diagnostic modules are retained. These are historical experiment entry points, **not** evidence-review commands. No experiment was rerun during report preparation.

A completed comparison/freeze refuses silent overwrite. Full independent training requires a separate, deliberately prepared fresh workspace, the raw CSV, the same source/dependencies, the Phase 1 baseline and stage-specific prerequisite manifests. Stage 1 produces selected family model caches; Stage 2 clones those estimators, produces all 21 ablation models and freezes candidates; Stage 3 freezes block-14 thresholds before test evaluation. Stage 2 foundation hashes refer to the particular preceding local execution, so a fresh run requires fresh-run provenance for newly generated outputs rather than presenting original execution hashes as new-run hashes. Timing checkpoints and original binaries are not supplied as public prerequisites.

This package provides the algorithmic source, full parameter/feature/weight/split specifications and authoritative outputs needed to understand and independently implement the protocol. It does not claim one-command full training reproduction from the compact public evidence bundle. The complete preserved local experiment retains original prerequisite manifests and caches. Historical verifiers that depend on those local caches remain separate from the portable public submission verifier. No existing scientific result or provenance record should be deleted or edited merely to bypass an overwrite/hash guard.

## Publication boundaries

Model binaries, prediction arrays, SHAP arrays, environments, machine-path-bearing historical checkpoints and temporary previews remain local/ignored. Compact, explicitly labeled projection files retain numeric settings/resource samples without editing original provenance. Publication recommendations are recorded separately in the Stage 4 review inventory. No GitHub publication is performed by any review/build command.
