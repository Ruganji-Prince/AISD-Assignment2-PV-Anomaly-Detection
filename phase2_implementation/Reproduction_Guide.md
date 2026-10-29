# Phase 2 reproducibility: preprocessing, evidence review and full modelling

## Environment and immutable data

Use Python 3.14.7 and the frozen [dependency lock](stage1/requirements-stage1-lock.txt), included by [requirements.txt](requirements.txt). The reference versions include NumPy 2.5.4, pandas 3.0.6, SciPy 1.18.1, scikit-learn 1.9.1, LightGBM 4.7.0 and matplotlib 3.11.2. No separate SHAP dependency is needed for native LightGBM Tree SHAP.

Data source: https://github.com/clayton-h-costa/pv_fault_dataset at commit `e9ed8ad8072dcb3ffc643b0f3604219798708551`; associated study https://doi.org/10.3390/s20174688. Expected location from the repository root: `data/raw/pv_fault_dataset.csv`. SHA-256: `717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a`. The raw 1,373,798×7 export and original license/provenance are unchanged.

From the repository root:

```powershell
python -m venv .cache/phase2-review-env
.cache\phase2-review-env\Scripts\Activate.ps1
python -m pip install -r phase2_implementation/requirements.txt
```

On POSIX systems, use `source .cache/phase2-review-env/bin/activate`.

## 1. Executable preprocessing — no classifier training

```powershell
python -B phase2_implementation/execute_preprocessing.py
```

Alternatively open [Phase2_Preprocessing_Implementation.ipynb](notebooks/Phase2_Preprocessing_Implementation.ipynb) in a Jupyter front end using the same environment and execute top-to-bottom. The Python entry point executes the same cells without requiring Jupyter. Learned medians/scalers/PCA fit only on TRAIN; validation/test receive transforms only. No classifier is fitted and no probability/test prediction is generated.

The notebook imports the original Stage 2 preprocessing through `src.phase2_stage2.models.build_preprocessor`. This factory is an extraction of the original steps, also used by the existing AblationModel constructor; it is not a second cleaning/feature policy. Optional local fitted-preprocessor comparisons only transform TRAIN probes and are skipped when model caches are absent. Public execution does not require model binaries.

Expected outputs:

| Location | Output |
| --- | --- |
| `phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb` | Executed preprocessing notebook, 13 code cells |
| `phase2_implementation/preprocessing_diagnostics/` | Eight 300-DPI diagnostic PNGs |
| `phase2_implementation/compliance/Preprocessing_Evidence.json` | Raw audit, frozen split, training-only fit ledger, matrix shapes, MI/PCA/scaling diagnostics |
| `phase2_implementation/compliance/Diagnostic_Inventory.json` | Figure captions, populations, dimensions and hashes |
| `phase2_implementation/compliance/Notebook_Execution.json` | Execution/error status and notebook hash |

TRAIN [0,1006129), VALIDATION [1056990,1173967), TEST [1227337,1373798) remain fixed. The selected LR F6/RF E4/LightGBM E4 matrices have 12/8/13 mathematical inputs, including retained-channel availability indicators. Large arrays remain in memory and are not committed. The newly completed MI/PCA/scaling diagnostics do not reopen frozen model/feature/sensor decisions.

## 2. Evidence and assignment verification — no preprocessing rerun

```powershell
python -B phase2_implementation/verify_submission.py
```

This reads frozen and compliance evidence, checks the new notebook/figures/table, verifies the unchanged scientific numbers and original report-page content, and runs the required semantic checks. It does not refit preprocessing, retrain classifiers, regenerate figures or predict. Any new verification output is small and explicitly scoped to the compliance review. Original historical verifiers remain unchanged and describe their earlier snapshot/package scope.

The [evidence-review notebook](notebooks/Phase2_Evidence_Review.ipynb) is separate, executed and unchanged. It can be inspected without any model cache. AP/ranking scores are checked against frozen evidence and hashes, not claimed to be recomputed from omitted public prediction arrays.

## 3. Full modelling reproduction — separate fresh workspace required

Full modelling reproduction is different from either command above. Completed official evidence must not be deleted or overwritten to bypass guards. No modelling experiment was rerun during compliance completion.

| Step | Existing root-based entry point | Prerequisites / expected outputs |
| --- | --- | --- |
| F6 selection | `python -B phase2_implementation/run_stage1.py` | Fresh output tree; raw CSV; Phase 1 baseline; static feature dependency/configuration and semantic/source-hash records. Produces bounded 16-trial evidence, selected LR/RF/LightGBM specifications and ignored `.cache/stage1/models/`. |
| Fixed sensor ablation | `python -B phase2_implementation/run_stage2.py` | Selected Stage 1 estimators/cache and fresh-run foundation hashes. Produces 21-run validation/class/resource tables, selection evidence and ignored `.cache/stage2/models/`. |
| Alert threshold freeze | `python -B phase2_implementation/run_stage3.py freeze` | Frozen approved final candidates and preceding evidence/models. Uses only block 14; produces threshold selection, protocol and freeze receipt. |
| Final evaluation | `python -B phase2_implementation/run_stage3.py test` | Existing threshold freeze and unchanged candidates. Produces final test metrics and ignored prediction arrays; never retunes decisions. |
| Explanations/assessment | `python -B -m src.phase2_stage3.analysis` | Frozen test/selection evidence and model caches; validation-only explanation sample. Produces explanations, dropout and engineering-criteria evidence. |

Fresh training requires copying the source, raw CSV and Phase 1 scientific artifacts to a separate workspace **without completed-run output guards**, then generating new-run prerequisite/protection manifests from that workspace. The original manifests contain hashes of a particular historical execution, including its README/source versions and selected model files; they must remain preserved, not silently relabeled as hashes for another run. Stage 1 semantic/source-hash prerequisites must be prepared before the first runner; Stage 2 protection must be prepared after Stage 1 results/models exist. The Stage 3 protocol records the fixed approved candidates before threshold selection. Historical modelling verifiers may require caches and original source versions; the current public compliance verifier does not.

This documentation identifies the complete settings and dependency order, but does **not claim one-command end-to-end training reproduction** from the compact public evidence bundle. Independently measured timing will depend on hardware and does not reproduce byte-for-byte. No model/cache binaries are required to understand or verify the public findings.

## Scientific specification index

- [Frozen split manifest](../phase1_strategy/Phase1_Split_Manifest.json).
- [Training-only class weights](stage1/evidence/class_weights.json): `N_train/(5*n_k)`; no SMOTE; validation/test are not rebalanced.
- [Feature parents](stage1/Feature_Dependencies.json), [sensor configurations](stage2/evidence/feature_availability_by_configuration.json), [full frozen model specifications](stage4/evidence/final_model_specifications.json).
- [Bounded selection configuration](stage1/evidence/experiment_configuration.json), [validation ablation](stage2/evidence/sensor_ablation_validation.csv), [threshold protocol](stage3/evidence/stage3_protocol.json).
- [Corrected resource protocol](stage2/evidence/measurement_protocol.json), [timing samples and host metadata](stage4/evidence/resource_protocol_public.json).
- [Prior-test-exposure disclosure](stage3/Methodology_Disclosure.md). The split is not pristine or previously unseen. Source order is not a reconstructed timestamp.

## Report and historical verification

`python -B phase2_implementation/build_compliance_report.py` rebuilds only the strategy-versus-reality appendix, retaining and checking the first ten approved scientific pages. It does not regenerate scientific results/figures. The report may exceed ten pages because no assignment page limit was specified.

`phase1_strategy/verify_phase1.py` checks the frozen Phase 1-only snapshot and intentionally rejects populated Phase 2 directories. It is not the current full-repository quick start. Historical Stage 4/5 report/package builders and verifiers describe the pre-compliance publication and retain their original hashes; current changes are recorded as explicit compliance exceptions. No original scientific evidence hash is silently rewritten.
