# Final independent rubric audit

## Decision and integrity

The release supports the exemplary band with material limitations in each category. A conservative **91/100** remains defensible; **100/100 is not established**. The five category scores were reassessed against the actual professor-supplied one-page grid, not accepted from the previous self-assessment. The [87-row matrix](Requirement_Evidence_Matrix.md) separates demonstrated checkpoints, partial evidence and mathematically inapplicable statistics. The official grid supplies bands, not per-checkpoint point allocations; precise point deductions remain judgment calls.

The baseline is public main `d007880c89a0312dbdf540678e9c8bf4cec3216e`. All 588 existing files except the explicitly corrected root README remain protected by a new byte-level manifest. This includes source, all scientific results, frozen protocols, reports, executed notebook, raw CSV, original model and earlier evidence. No cloud writes, model fitting, deployment operations, TEST-guided selection or main integration occurred.

Original RF SHA-256: `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`. Original raw CSV SHA-256: `717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a`. Approved Phase 1 PDF SHA-256: `dfb3f253f3e059ece168d9c6edffc10f68a0a21ba8b738a6fb2b2d2c1d962497`. Original submission tag remains `submission-ready-20261124`, annotated object `b39525d624839615eb23c5d2f52cbe3e188756f3`, target `d49cff533e5fe8860bacfb9942779ab003db47db`.

## Rubric 1 — data hygiene, features and collinearity

The prediction unit is one exported PV observation, not an event/day/session. N=1,373,798, P=7, six continuous physical predictors and five-class nominal target `f_nv`. The fresh audit confirms zero conventional NaNs/infinities and 62 paired irradiance/temperature zeros. These zeros remain observations, not confirmed missingness. Missingness indicators are constant zero: Little's missing-pattern test is not estimable; a missingness-versus-label Cramér V denominator has `min(r−1,c−1)=0`. MCAR/MAR/MNAR cannot be identified from these exports. These are applicability exceptions, not manufactured negative test results.

TRAIN outlier diagnostics use 1.5 IQR fences, |Z|>3 and modified MAD |Z|>3.5. Distribution tests and skewness are descriptive on dependent readings. [Clipping comparison](../evidence/rubric1/clipping_comparison.json): block-13 RF macro-F1 is .956297122 without clipping and with IQR clipping, versus .956041296 with quantile clipping. These are existing separate experimental fits; no new clipping policy was adopted. Statistically unusual fault observations are not automatically invalid.

TRAIN Pearson voltage-pair r=.989102760 and Spearman=.932559144 exceed .85. VIFs are vdc1=52.1682, vdc2=56.3457, idc1=31.4956, idc2=15.7808, irr=39.2927, pvt=4.0698. The official grid has no numeric VIF cutoff; the project uses >10. Correlation alone does not justify deletion. TRAIN-only MI uses 50,000 seed-42 observations; two standardized principal components explain .951676668 of variance but require the original physical channels.

| Physical channel | Unit | Deployed E4 treatment | Evidence and reason |
| --- | --- | --- | --- |
| vdc1 | V | Retained | Measured four-channel validation meets declared constraints; voltage-pair redundancy alone is insufficient for removal |
| vdc2 | V | Retained | Same ablation evidence; large balanced-sample permutation loss is predictive association |
| idc1 | A | Retained | Current and pair relationships support evaluated diagnosis; removal configurations do not establish an accepted smaller solution |
| idc2 | A | Retained | Retained pair supports the evaluated fault distinctions; continuous dropout is unsafe |
| irr | W/m² | Excluded from deployed predictor | E4 does not require the irradiance sensor; useful for audit/regime slicing, not leaked into inference |
| pvt | °C | Excluded from deployed predictor | E4 does not require module temperature; remains available for descriptive cohort analysis |

[All 21 configurations](../../phase2_implementation/stage2/evidence/sensor_ablation_validation.csv) provide the actual comparison. Four physical channels produce eight mathematical RF inputs after indicators. Derived differences/ratios require their parent sensors; PCA is not physical sensor reduction. Target, acquisition index and operating block are not predictors. Hypothetical relative error costs are sensitivity assumptions, not elicited monetary losses.

## Rubric 2 — leakage walkthrough

| Population | Exact positions | Use | Isolation evidence / limitation |
| --- | --- | --- | --- |
| TRAIN | [0,1006129), N=1,006,129 | Original model fit; preprocessing, class weights, MI/PCA/clipping diagnostics | Fitted E4 medians freshly match TRAIN: [51.2504,53.1038,.1105,.0432] |
| Validation block 13 | [1056990,1089790), N=32,800 | Original fixed-model/sensing comparison | No new selection in this audit |
| Validation block 14 | [1140571,1173967), N=33,396 | Original hardware threshold; later experimental calibration | Calibration uses 256-position tiles, 64-position purges and zero fit/evaluation overlap; one physical block limits independence |
| Full VALIDATION | [1056990,1173967), N=116,977 | Frozen validation partition, including within-partition background positions | Distinct from just the two active blocks |
| TEST | [1227337,1373798), N=146,461 | Previously inspected, retrospective reporting and parity reproduction only | Not a pristine prospective holdout |
| Excluded separators | [1006129,1056990), [1173967,1227337) | Excluded from the three partitions | Total 104,231 positions |

The split allocates 12/2/2 signal-defined blocks. Irradiance <100 W/m² for at least 3,600 consecutive **source positions** defines separators. Positions are not verified seconds, hours, sessions or days. No timestamp variable or verified physical session identifier exists. Random row splitting would mix neighboring acquisition regimes and is inappropriate.

Fresh independent feature hashes give zero cross-partition intersections for all three pairs under both six- and four-channel views. The existing exhaustive standardized-neighbor audit finds 62,917 near TEST neighbors among four-channel TRAIN states and 1,125 for six channels at distance≤.001; zero exact-distance matches. Similar states are not automatic leakage, but they weaken independent-observation claims. Nine grouped fold fits use fit-only imputation/scaling/weights. Class 1 occurs in TRAIN block 12 only, preventing full-support independent folds. No new target, preprocessing, calibration or fold leakage is identified; **physical independence is not established**.

## Rubric 3 — modeling and evaluation

Identical E4 physical inputs, block-13 VALIDATION only:

| Family | Macro-F1 | Macro AP |
| --- | ---: | ---: |
| LR E4 | .588207357 | .653734349 |
| RF E4 | .956297122 | .989740014 |
| LightGBM E4 | .855657128 | .991518322 |

LR F6 (.893869804 F1) is a separate six-channel resource reference, not a same-input competitor. RF E4 alone passes the four archived validation criteria among 21 configurations: macro-F1≥.80, each hardware-class recall≥.90, degradation≤.05, physical channels≤4. The original 10 ms/10 MiB engineering requirements were **not** part of that four-criterion pass and remain unmet. No TEST result was used for a new winner.

TRAIN supports are [844805,1226,5695,1204,153199]. Dummy TEST macro-F1=.183799862; a TRAIN-q99 current-imbalance binary rule has TEST hardware recall=.342280926 and combined nonhardware FPR=.000186487. It is not a five-class baseline. AP is recall-step-weighted average precision, not trapezoidal PR-AUC. Hardware P@top1% uses 1,465 TEST positions. MAE on arbitrary nominal codes has no meaningful physical distance and is N/A. [New fixed-weight balanced-accuracy sensitivity](Weighted_BA_Sensitivity.json) provides 80 summaries with hypothetical class priorities; no utility/winner is selected.

Fresh RF retrospective TEST reproduction gives macro-F1=.950481150 and macro AP=.976218899, identical confusion matrices and unchanged frozen-threshold rates. At historical tau=.5913558658757772, missed-hardware fraction=.004544809 among true classes 1–3; combined FPR=.000832018 among true 0/4. This **historical alert rule is not the production argmax rule**.

The exact 1e-12 TEST hardware-AP reproduction check failed: one fresh value differs by −5.8405747e-8 from archived .9933539110201307. Repeated parallel/sequential probabilities differ by at most3.33e-16; all argmax classes are identical, while score-order AP changes near ties. [Diagnostics](AP_Numerical_Diagnostic.json) preserve the discrepancy. No archival result, probability normalization or test tolerance was changed. Exact score-order reproducibility is PARTIAL, not silently labeled reproduced.

Experimental TEST original/sigmoid/isotonic Brier scores are .079293/.051306/.053112; log loss .151089/.089088/.092305; top-label ECE .023762/.014281/.011333. Selection was block-14 cross-fitted log loss, not TEST. No calibration map, probability confidence or calibrated alert threshold is deployed. The grouped-OOF bootstrap uses 1,000 draws; 671 have all five true supports. Fixed-five interval .373881–.721550 versus conditional all-support .495205–.623462 demonstrates sensitivity, not guaranteed independent-population coverage.

## Rubric 4 — engineering failure modes

| Failure mode | Actual evidence | Operational consequence | Existing mitigation | Remaining risk |
| --- | --- | --- | --- | --- |
| Normal confused with shade | 6,604 normal→shade; shade precision .691080866 | Environmental condition overcalled | Environmental label separated from hardware | Field utility not validated |
| Hardware subtype confusion | LightGBM TEST short-circuit recall .499364676 | High aggregate alerts can conceal subtype misses | RF chosen using validation constraints; per-class reporting | Historical TEST cannot prove prospective safety |
| Operating-regime shift | TRAIN-bin TEST idc1 PSI≈4.627, KS≈.431 | Changed input mix and class support | Irradiance/electrical subgroup supports and FPRs | No verified timestamp/site drift or monitoring |
| Noise / bias | Simulated5% IQR-noise F1≈.796863–.798149 | Sensor error can substantially degrade diagnosis | Schema/range warnings and fixed stress disclosure | Not measured field noise; no causal claim |
| Retained-channel dropout / saturation | Full-block vdc1 dropout F1≈.0000432292; separate isolated tests | Missing required sensors can invalidate inference | Missing/nonfinite inputs rejected | Saturation may be finite; no certified graceful degradation |
| OOD finite inputs | Existing perturbation and range-warning evidence | Forest may still return a class | Range warnings; no calibrated confidence shown | Warning is not an OOD detector or safety abstention |
| Cloud unavailable or initializing | Current first health62.9s; historical observed-zero-replica56.94s | Demonstration delayed | Bounded startup/retry, no local fabricated result, offline CLI | No uptime SLA or always-on replica |
| Anonymous API overload | Process-local capacity2 and deadlines | Resource/quota exhaustion possible | 2KB body cap, generic errors, bounded responses | No distributed authenticated rate limiter |

[RF permutation](../evidence/rubric4/RF_raw_channel_permutation.json) uses a balanced 1,000-row validation sample and three repeats. Native SHAP evidence is for **LightGBM**, not RF; descriptive MI is not a trained-model explanation. Predictive associations are not causal attributions. Controlled perturbations are simulated, not observed field failure rates.

## Rubric 5 — current reproducibility and serving evidence

Anonymous clone and a new isolated Python3.14.10 environment installed all 41 pinned packages with a successful compatibility check. The new release-specific verifier and 50 regressions are executed without refitting models. Existing 13-cell notebook execution and actual Linux image evidence are retained as earlier receipts, not rerun. No private cache is required for essential inference; reproducing every original nonpublished model does require archived binaries or separately labeled public refits.

Current Vercel deployment `dpl_EobcLSoR4iY4NSXYn5jxNCX5jvba` is READY: nine output files, zero models/Python/functions. All eight public asset hashes match the frozen manifest. Azure revision `pv-anomaly-detection--submission-api-20261128` uses immutable image `sha256:8c233e77ec370131f44670fcaf812a5aa27a79f7ca56bb8b7eff1beebc9cd946`, Consumption0.5vCPU/1GiB,min0/max1,HTTPS8000. All six CORS origins pass; unrelated origin is rejected. Five live browser classes, all four workflow steps and 320/390/768/1440 widths pass. Full failure/retry/accessibility evidence remains in the unchanged final-release package; this audit does not claim manual assistive-technology certification.

Fresh first health latency=62,900.484ms; this is not a controlled cold-start distribution. Five prediction checks had forest5.985–9.932ms, preprocessing4.866–17.287ms, server12.251–27.592ms and network468.748–482.523ms. These five values are checks, not a new percentile benchmark. Historical Azure30-request warm network p95=248.988ms, preprocessing p95=7.263ms, forestp95=7.868ms and serverp95≈16.62ms remain separate. Different component p95s must not be added. Server timing excludes platform bootstrap and full response transmission; wall time is not billed CPU.

The original artifact is12,232,020bytes=11.665363312MiB, exceeding10MiB by16.65%. Archived complete-path p95=36.808295ms also exceeds10ms. Historical cost scenarios dated27November estimate$0/$0/$5.40/$33.48 for10/30/200/720 allocated replica-hours, conditional on shared free grants and stated assumptions. Empty ActualCost rows do not prove a zero invoice; remaining student credit, tax, egress and aggregate usage are not verified. No new pricing promise is made.

Reachable-history scanning inspected840blobs across79commits. One marker-only private-key header in a negative security test was reviewed; no actual key was detected. The original scan still flags the fixture. Pattern scans, dependency advisories and input tests are bounded assurance, not proof against arbitrary credentials or vulnerabilities. No secret values were published.

## Actual safe improvements and mandatory checks

A: corrected the root README quick-check command and stale Vercel inference wording; supplied a new current-release verifier without altering frozen historical gates; normalized dot segments for Windows long-path link checks; consolidated exact current evidence and defense commands. B: added fixed-weight balanced-accuracy sensitivity and fresh frozen-RF metric reproduction, retaining the AP exception. No model changes or new expensive experiments were needed.

Mandatory A: public clone/README and essential installation/inference/tests verified. Mandatory B: zero identified unaddressed implementation leakage, **qualified by historical exposure and limited physical independence**. Mandatory C: existing cloud live and bounded secret scan reviewed, **not an unrestricted security certification**. The legacy gate failure and small AP reproduction exception are disclosed, not hidden or converted into passing historical checks. No critical artifact, class-prediction, split or implementation-leakage failure was found.
