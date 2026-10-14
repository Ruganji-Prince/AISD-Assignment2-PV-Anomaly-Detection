# Dataset selection evidence and recommendation

Ruganji Prince · Assignment 2 AISD · 12 October 2026

**Status: the original-source dataset was approved on 12 October 2026.** This selection evidence
is retained alongside Phase1_Strategy_Report.pdf. Preliminary index split candidates below are feasibility
evidence; the final plan uses ordered 12/2/2 measured operating blocks with full separator buffers.

## Recommendation

The approved primary experimental operating-state dataset is the original-source Lazzaretti/Costa PV fault data,
with documented limitations. The supplied EddieOuyang mirror is retained as verification
evidence: both MAT files have identical SHA-256 hashes to the original. The original source is preferred for citation.
Its six exported sensor channels support the central ablation question, and labels correspond to physically
induced equipment conditions and natural building shade. It is computationally manageable: two files
total 28,077,185 bytes. The complete consolidated numeric matrix requires approximately 77 MB at float64;
auditing copies and sorting can use more memory.

There is no perfect candidate. The primary recommendation sacrifices exported timestamps and realistic
fault prevalence to retain a defensible experimental target. A limited PVDAQ operational slice is a possible
secondary *data-quality* study; without verified labels it cannot validate supervised fault recall or F1.
Merging these datasets is excluded from the proposed strategy. Cross-dataset fault-performance claims require compatible sensors and independently
supported labels, neither of which has yet been established for a second dataset.

## Evidence categories

Measured findings below come from downloaded files, not advertised sample counts. Documentation claims
are marked as such. `candidate_audit.json` contains the per-variable audit, distribution statistics,
class counts, label runs and timestamp summaries. `download_manifest.json` records actual bytes, URLs,
hashes and failed accesses. `source_metadata.json` records licenses and repository commits. Access date: 12 October 2026.

## Candidate comparison

| Candidate | Actual files inspected | Sensors/time structure | Labels and main limitation | Decision |
|---|---|---|---|---|
| PVDAQ/OEDI | Systems metadata 1,862 × 31; bounded operational sample 1 × 15 | Electrical/environmental columns; timestamp; site-dependent coverage | Sample has no fault target and four -99999 sentinel cells; one row cannot establish cadence | Optional secondary quality audit; select a bounded site/window later |
| pvdaq_access | Current README, repository redirect verified | Daily CSV/Parquet data lake access; site IDs required | Access tool, not independent dataset; old API assumed neither needed nor working | Use current NatLabRockies repository if PVDAQ selected |
| Zenodo 18225566 | ZIP 61,486 bytes; scenario CSV 500 × 14; dictionary and supplied script | Normalized scenario indicators; no timestamps or raw electrical channels | Decision/action label; priority is a derived target. Not raw fault-state monitoring | Reject as primary for this research |
| NASA POWER | Official site/documentation reviewed; no data downloaded | Environmental context, not plant electrical sensors | No verified equipment-fault target | Context only; no fault-label claims |
| EddieOuyang PV fault mirror | MAT files 1,373,798 × 3 and × 4 | Six sensor channels; no exported timestamps | Five operating states; experimentally induced faults and natural shade | Prefer original author's byte-identical source |
| PV-Fault-DS226 | Raw CSV 226,175 × 10; labeled CSV 226,175 × 14 | Seven acquired channels, two power columns, timestamps with gaps | Two subsystem labels, rule-derived assignment; rare short circuits; power inconsistencies | Alternative if timestamp audit is prioritized, with explicit label caveat |
| Kaggle Solar Power Generation | Four CSVs in 1,988,756-byte ZIP; dimensions below | Two plants, repeated inverter readings, 15-minute modal cadence and gaps | No fault labels; source license field does not establish a clear reuse license | Not primary supervised target; rights need clarification before redistribution |
| Zenodo 18326501 | One 1,145,740-byte PDF poster only | Poster describes 1-minute electrical and 5-minute IV acquisition | No tabular data file or dataset URL supplied in this record/poster | Not currently verified as usable data |

## Primary raw audit

`dataset_amb.mat` is N × 3; `dataset_elec.mat` is N × 4; N = 1,373,798 in each.
Consolidation here means adding columns in the supplied order, not concatenating rows or creating
new measurements. Total P = 7 includes the target; predictor P = 6. Rows are repeated measurements
from one two-string plant, not 1.37 million independent experiments.

| Variable | Meaning and unit | Loaded type | Analytical category and role | NaN cells | Mean | Median | Skewness |
|---|---|---|---|---|---|---|---|
| vdc1 | String 1 voltage, V | float64 | Continuous predictor | 0 | 135.1183 | 37.7763 | 0.0852 |
| vdc2 | String 2 voltage, V | float64 | Continuous predictor | 0 | 134.7199 | 39.8375 | 0.1158 |
| idc1 | String 1 current, A | float64 | Continuous predictor | 0 | 2.2769 | 0.1136 | 1.0109 |
| idc2 | String 2 current, A | float64 | Continuous predictor | 0 | 2.0003 | 0.0441 | 1.1438 |
| irr | Irradiance, W/m² | float64 | Continuous predictor | 0 | 257.6111 | 1.7364 | 0.8897 |
| pvt | Reported aggregate module temperature, °C | float64 | Continuous predictor | 0 | 22.7728 | 18.4905 | 0.5943 |
| f_nv | Operating-state code, unitless | uint8 | Nominal categorical target | 0 | Not meaningful | Not meaningful | Not meaningful |

All 1,373,798 rows are complete for exported values, with 0 missing cells out of 9,616,586 cells (0%).
There are no exact duplicate consolidated rows and no infinite readings. This establishes neither
absence of omitted times nor absence of sensor errors. MCAR/MAR/MNAR cannot be diagnosed from a
constant all-zero missingness indicator; the mechanism is unidentifiable from these exported cells.

One irradiance reading is slightly negative (-0.0381 W/m²). It requires a documented near-zero sensor
tolerance, not automatic deletion. Negative temperature is physically possible in Curitiba: 24,172
temperature values are below zero, minimum -1.6543 °C. Both irradiance and temperature have 62 zero
values; whether these are valid simultaneous readings or sentinels needs further contextual checking.
Voltage skewness near zero does not prove a Gaussian distribution: day/night mixtures can be symmetric
while highly non-Gaussian. Median imputation is only a provisional fallback; a final choice needs operating-condition
analysis, and imputation is not presently necessary for NaNs.

| Label | Meaning | Actual count | Percentage |
|---|---|---|---|
| 0 | Normal | 1,162,931 | 84.6508% |
| 1 | Short circuit | 5,999 | 0.4367% |
| 2 | Resistive degradation | 10,371 | 0.7549% |
| 3 | Open circuit | 6,024 | 0.4385% |
| 4 | Building shadowing | 188,473 | 13.7191% |

These labels describe experimental operating conditions. Physically induced resistances do not demonstrate
years of natural degradation. Shade is an environmental operating condition and should not automatically
be counted as a hardware fault. Numeric label codes have no meaningful order.

## Timestamp, provenance and splitting risks

No MAT variable contains timestamps, dates or system IDs. The paper describes one-second exported
measurements, with electrical RMS aggregation and environmental averaging, but actual time intervals,
missing intervals, timezone and drift cannot be independently recovered from these arrays.
The acquisition index is retained as metadata. Calendar timestamps are not fabricated, and verified frequency is not claimed.
Index-based alignment is provisional, supported by the source description, not merely by equal lengths.

The paper's daytime real-data counts total 515,958, whereas the public export totals 1,373,798.
Normal and shade counts differ; equipment-fault counts agree exactly. The large low-irradiance fraction
is consistent with additional low-light coverage, but the reason for the discrepancy remains unverified.
Original timestamps/day boundaries would require source clarification if available; any interpretation must acknowledge the discrepancy.
The source experiment used scheduled midday induced faults on clear days, so scheduled context and
limited weather diversity constrain generalization. Neither Rwanda field reliability nor fault prognosis
is demonstrated by this dataset.

A preliminary contiguous 70/15/15 split gives the first partition zero short-circuit examples and only
five open-circuit examples. An 80/10/10 ordered split has all classes in each partition:

| Provisional partition | Index range, zero-based end-exclusive | N | Normal | Short | Degradation | Open | Shade |
|---|---|---|---|---|---|---|---|
| Training | [0, 1099038) | 1,099,038 | 922,726 | 2,458 | 6,917 | 2,410 | 164,527 |
| Validation | [1099038, 1236418) | 137,380 | 124,280 | 1,180 | 1,184 | 1,204 | 9,532 |
| Test | [1236418, 1373798) | 137,380 | 115,925 | 2,361 | 2,270 | 2,410 | 14,414 |

These are feasibility checks, not a finalized evaluation split. Class-preserving proportions are subordinate
to acquisition order; random shuffling of adjacent measurements is excluded. Day/episode boundaries, purge widths,
low-light eligibility and final target require Phase 1 decisions. Label runs can locate boundaries but do
not establish independent episodes. All global exploratory findings must be marked descriptive; learned
preprocessing and target-based feature selection will use training data only in Phase 2.

## PV-Fault-DS226 alternative audit

The actual raw file uses semicolons. It contains timestamp, I1, I2, V1, V2, Irr, T1, T2, P1 and P2.
The labeled file adds numeric and text labels for each subsystem; neither counterpart label may be used
as a predictor. Timestamps cover 10–23 January 2026 on 12 observed dates; timezone is absent.
The median interval is 1.057237 s, maximum 163,354.074604 s. There are no NaNs or duplicate timestamps,
but this does not erase large recording gaps. Seven acquired channels are distinct from nine numerical
columns: power must not automatically be counted as two additional physical sensors.

Raw power does not equal the supplied voltage-current product within 0.001 W on 25,301 rows for P1
and 19,705 rows for P2. Raw P1 reaches -473.672988 W despite nonnegative exported voltage/current.
This is a data-quality concern requiring source clarification, not evidence of a fault by itself.

Class distributions are in `candidate_audit.json`. Short-circuit labels occur only 53 times in subsystem 1
and 133 in subsystem 2. Preprint labeling uses measured-signal thresholds and fallback rules. Therefore
performance against these labels partly measures agreement with the labeling rules, even though the
experiment induced physical faults. The preprint is not peer reviewed; descriptions also differ in campaign
length (11 versus 12 days). This dataset is more suitable for timestamp/synchronization diagnostics but
less suitable for claims of independently verified fault detection.

## Other candidate audit details and access actions

Kaggle generation files: plant 1 = 68,778 × 7; plant 2 = 67,698 × 7. Weather files: plant 1 = 3,182 × 6;
plant 2 = 3,259 × 6. No exported missing cells occur. Nevertheless, between each entity's first and last
timestamp, 15-minute grids have 3,026 and 4,110 absent generation slots, and 82 and 5 absent weather
slots respectively. These are missing records, not NaNs. Repeated plant timestamps across inverters are
expected; the entity-time key is the relevant duplicate check. Cumulative yields can reveal system identity
and long-term information. Zero nighttime power is legitimate. No fault-label field exists.
The API reports the license name as “Data files © Original Authors”; this is not an explicit open license
grant, so intended academic reuse and redistribution require verification with the original source. The archive downloaded
without login in this session; no manual login is currently required.

The maintenance subset's 500 rows have scenario/action labels, not timestamps or measured voltage/current.
Its priority and severity/status fields can leak decision logic. `data_gap_rate` is a normalized indicator,
not observed per-channel missingness. Zenodo metadata identifies CC BY 4.0.

PVDAQ metadata and the tiny sample verify anonymous HTTPS data-lake access. The 1-row operational
sample is a schema and sentinel check only; no representative N, class distribution, cadence or missingness
claim is made for a full site. Current access software is at NatLabRockies/pvdaq_access following the
NREL URL redirect. Any download is restricted to a bounded site/window following file-size checks; whole-lake downloading is excluded.

Zenodo 18326501 provides a poster without a tabular download link. Obtaining usable data requires a
separate authoritative release or asking the listed author for access. No contact has been sent.
The MDPI PDF endpoint returned HTTP 403; the original paper was retrieved as full-text XML via Europe PMC.
NASA POWER has not been downloaded because it is contextual, not a competing fault-data source.

## Approved choice and final Phase 1 plan

The original author dataset is approved **with missing timestamps, count discrepancy and experimental
sampling explicitly acknowledged**. The final target is five-class operating-state classification with
separate equipment-alert analysis. The final plan allocates 16 measured index operating blocks 12/2/2
and withholds two whole low-irradiance separators; these are not verified dates. See Phase1_Strategy_Report.pdf
for exact bounds, class coverage, preprocessing and leakage design. No production pipeline, model training
or Phase 2 deliverable has been created. Git/GitHub submission and separate Phase 2 approval remain outstanding.

## Sources

1. Supplied Assignment 2 PDF: pp. 1–10, especially Phase 1 rubric pp. 4–5 and submission rules p. 3.
2. Supplied Assignment 1 proposal: pp. 1–2, including sensor ablation equation and project timeline.
3. Original dataset: https://github.com/clayton-h-costa/pv_fault_dataset and downloaded README/LICENSE.
4. Original paper: https://doi.org/10.3390/s20174688; full XML retrieved via https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7506914/fullTextXML.
5. Candidate mirror: https://github.com/EddieOuyang2004/pv_fault_dataset.
6. PVDAQ: https://data.openei.org/submissions/4568; access tool https://github.com/NatLabRockies/pvdaq_access.
7. Maintenance scenarios: https://doi.org/10.5281/zenodo.18225566.
8. DS226: https://doi.org/10.5281/zenodo.19259504 and https://www.preprints.org/manuscript/202607.2348.
9. Solar generation: https://www.kaggle.com/datasets/anikannal/solar-power-generation-data.
10. Benchmark poster: https://doi.org/10.5281/zenodo.18326501.
11. Environmental context: https://power.larc.nasa.gov/.
