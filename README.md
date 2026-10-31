# Resource-Efficient and Explainable AI for Photovoltaic Anomaly Detection Under Sparse Sensing Constraints

Ruganji Prince · 04-652 Artificial Intelligence System Design

**Current milestone: Data Preprocessing.** This repository currently presents the data-preprocessing stage of the PV anomaly-detection project. The objective is to prepare defensible photovoltaic measurements for later investigation of sensing and computational trade-offs. Downstream work is outside the current submission scope.

**Task Type: Multiclass Classification.** The [original dataset](https://github.com/clayton-h-costa/pv_fault_dataset), pinned at `e9ed8ad8072dcb3ffc643b0f3604219798708551`, is associated with [Lazzaretti et al. (2020)](https://doi.org/10.3390/s20174688).

| Property | Description |
| --- | --- |
| N × P | 1,373,798 × 7 |
| Predictors | vdc1, vdc2 (V); idc1, idc2 (A); irr (W/m²); pvt (°C) |
| Target | f_nv: 0 normal, 1 short circuit, 2 resistive degradation, 3 open circuit, 4 natural building shade |
| Types | Six continuous measurements and one nominal target; integer labels are not ordinal or continuous |

The [raw CSV](data/raw/pv_fault_dataset.csv), [conversion/source provenance](data/raw/README.md), [variable inventory](phase1_strategy/Variable_Inventory.csv) and [original license](phase1_strategy/PRIMARY_SOURCE_LICENSE.txt) are retained unchanged apart from navigation in the raw-data guide. Voltage/current are source-described DC RMS quantities; module temperature aggregates source probes.

![First ten raw observations](figures/raw_dataset_preview.png)

Preview of the raw photovoltaic monitoring dataset. First ten observations in exported source order. All ten have f_nv = 0.

## Data-quality findings

The export has zero conventional missing cells and 1,373,798 complete rows. This does not diagnose MCAR/MAR/MNAR or prove uninterrupted monitoring. The 62 paired irr/pvt zeros remain suspicious observations, not confirmed missing values. One irradiance value is -0.0381 W/m²; the existing quality convention clamps -1 ≤ irr < 0 to zero. Valid negative Celsius observations remain unchanged. No automatic statistical outlier deletion or capping is used.

The irradiance-qualified subset irr ≥ 100 W/m² contains 515,958 observations and reproduces literature class counts exactly. This suggests a possible evaluation-population explanation, but the paper does not explicitly document that filtering operation. Low-irradiance rows are retained rather than deleted to force agreement.

## Preprocessing workflow

Immutable data → schema/quality audit → original ordered partitions → TRAIN-only median/scaling fit → transform validation/test → descriptive diagnostics and output-dimension checks. Paired zeros remain observed. Contingency median imputation and retained-channel indicators are preserved. StandardScaler, native-scale and physical-derived representations are demonstrated without fitting downstream predictors. Robust/MinMax scaling and PCA remain descriptive alternatives; no new transformation or sensor choice is selected.

TRAIN [0,1006129), VALIDATION [1056990,1173967), TEST [1227337,1373798) are retained, with 104,231 separator positions. Sixteen signal-defined blocks are not verified days, sessions or hours. Nominal 1 Hz acquisition, per-second electrical RMS values, one-second environmental averages and the study's 16-day duration do not reconstruct timestamps or uninterrupted spacing. CSV order is source-position order only. The separator remains irr < 100 W/m² for at least 3,600 consecutive source positions, not a verified hour. The reserved partition is not claimed to be historically unseen.

Five TRAIN predictor pairs have |r| ≥ 0.85; five VIF values exceed 10. Dependence does not justify automatic deletion. Nominal-target association uses a proportional 50,000-observation TRAIN MI sample; scatterplots use 20,000 TRAIN positions. Exploratory TRAIN-scaled PCA explains approximately 95.17% with two mathematical components; all six physical inputs are still required to calculate them.

## Deliverables and execution

- [Approved Phase 1 report](phase1_strategy/Phase1_Strategy_Report.pdf) and [audit evidence](phase1_strategy/Supporting_Evidence_Index.md)
- [Executed preprocessing notebook](phase2_implementation/notebooks/Phase2_Preprocessing_Implementation.ipynb)
- [Preprocessing-stage report](phase2_implementation/reports/Phase2_Final_Report.pdf)
- [Eight diagnostics](phase2_implementation/preprocessing_diagnostics/README.md)
- [Preprocessing strategy versus reality](phase2_implementation/compliance/Strategy_vs_Reality.md)
- [Setup and reproduction](phase2_implementation/Reproduction_Guide.md)

After environment setup, run from the root:

```text
python -B phase2_implementation/execute_preprocessing.py
python -B phase2_implementation/verify_submission.py
```

## Structure

```text
data/raw/                         Immutable CSV and provenance
phase1_strategy/                  Original strategy and audit evidence
src/transformers.py               Target-free quality and physical transformations
src/pipeline_builder.py           Pipeline / ColumnTransformer definitions
src/preprocessing/                Preprocessing study and shared constants
phase2_implementation/notebooks/   Executed preprocessing notebook
phase2_implementation/reports/     Preprocessing report and text
phase2_implementation/compliance/  Preprocessing evidence and reflection table
phase2_implementation/preprocessing_diagnostics/  Eight original figures
```

Processed arrays, environments and local review material are excluded. The current report makes no deployment-performance, globally minimum-sensing or causal claims. Historical Phase 1 planning remains labeled as planning.
