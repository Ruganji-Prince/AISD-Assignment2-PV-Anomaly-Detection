# PV class measurement ranges — frozen TRAIN only

## Scope and provenance

Source: [original CSV](../data/raw/pv_fault_dataset.csv), SHA-256 `717278fdc338bf6713293c0495421a8be9ea02a0b64144e86e957a531edecb8a`. Dataset attribution: [source repository](https://github.com/clayton-h-costa/pv_fault_dataset), [Lazzaretti et al. (2020)](https://doi.org/10.3390/s20174688); preserved [source documentation](../phase1_strategy/PRIMARY_SOURCE_README.md).

The prediction unit is one exported observation. Only source positions **[0, 1006129)**, N=1,006,129, are analyzed. VALIDATION and TEST measurements are not loaded or used for summaries, interpretation-based selection or threshold design. Whole-CSV hashing verifies immutable bytes, not held-out measurement statistics. The complete frozen TRAIN interval is retained, including its background/low-irradiance observations; no operating-state or eligibility filtering, random resampling, class balancing or block deletion is applied. Labels are nominal, not ordinal. Class 4 is an environmental condition, not a hardware fault. Source order is not a verified timestamp, day, session or hour.

The existing [RetainedQuality convention](../src/transformers.py) is applied to the four electrical channels: nonfinite and negative electrical inputs would become NaN. TRAIN has **zero** such electrical inputs; quality output equals original electrical measurements exactly. Therefore no imputation, scaling, clipping, winsorization or outlier deletion is needed or applied for these physical-unit summaries. Medians are not fitted separately by class for inference. No model is loaded, fitted or queried. Original model SHA-256 is verified as `55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb`; no model bytes change.

## Calculation definitions and reproduction

- N is the number of TRAIN rows carrying the given class label; all four electrical channels have N valid observations, with no missing-value denominator change.
- Min/max are observed extrema, not physical validity limits or guaranteed classification thresholds.
- P5/P25/median/P75/P95 use NumPy `quantile(method="linear")`: for sorted x and q, h=(N−1)q, interpolate linearly between floor(h) and ceil(h). Median is q=.5.
- Mean is sum(x)/N; sample SD is sqrt(sum((x−mean)²)/(N−1)), `ddof=1`. SD is descriptive; dependent acquisition rows do not constitute N independent replicates or justify iid confidence intervals.
- Signed differences use the same row: ΔV=vdc1−vdc2 and ΔI=idc1−idc2. Absolute differences retain magnitude without direction. No voltage/current ratio with a near-zero denominator is introduced.
- Correlations are within-class Pearson and average-rank Spearman, computed pairwise on complete TRAIN electrical values. Descriptive association is not causal evidence or a hypothesis test.
- The overlap screen intersects each pair of classes' marginal [P5,P95] intervals. Fractions count each class's actual readings inclusively inside that intersection. These are interval-occupancy summaries, not density-overlap coefficients, classifier error rates or new decision thresholds.
- Tables round to four decimals (correlations six); [CSV](PV_Class_Measurement_Ranges.csv) uses 17 significant digits for all 20 physical-channel summaries. Derived/overlap tables are regenerated directly from the unrounded arrays, not rounded table entries.

Deterministic script: [class_measurement_ranges.py](class_measurement_ranges.py). No sampling, RNG, network access, model fitting, timestamps or environment-specific absolute paths are used. Verified runtime: Python 3.14.10, NumPy 2.5.4, pandas 3.0.6. Existing installation: `uv venv --python 3.14.10 .venv`, then `uv pip install --python .venv -r technical_evaluation/requirements.txt`.

From the repository root, using that environment:

```sh
python -B -m technical_evaluation.class_measurement_ranges
python -B -m technical_evaluation.class_measurement_ranges --check
```

The first command writes only this new Markdown report and its CSV. `--check` recomputes both and verifies byte-identical output without writing. Raw CSV/model hashes, split constants, frozen class counts, unchanged quality values and lossless CSV round-trip are checked on every run. Scientific reports, historical results and frontend files are not modified.

## Class support and existing irradiance regime

| Class | Label | N | irr <100 W/m²: N | Fraction of class |
| --- | --- | --- | --- | --- |
| 0 | Normal operation | 844805 | 615051 | 72.8039% |
| 1 | Short circuit | 1226 | 0 | 0.0000% |
| 2 | Resistive degradation | 5695 | 0 | 0.0000% |
| 3 | Open circuit | 1204 | 0 | 0.0000% |
| 4 | Natural building shade | 153199 | 3111 | 2.0307% |

The 100 W/m² boundary is the existing project regime/separator boundary, used only to describe support here. The rule does not become an electrical classification threshold and does not filter these summaries. Mixed operating regimes can make class extrema and means misleading without quantiles and joint relationships.

## Observed physical-channel distributions

| Class | Channel | Unit | N | Min | P5 | P25 | Median | P75 | P95 | Max | Mean | Sample SD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | vdc1 | V | 844805 | 0.3799 | 0.4668 | 0.9337 | 2.3061 | 267.6650 | 292.5700 | 363.9740 | 109.2540 | 131.7959 |
| 0 | vdc2 | V | 844805 | 0.3164 | 0.4250 | 0.8963 | 2.4814 | 266.2910 | 290.0140 | 368.7490 | 108.5960 | 131.0457 |
| 0 | idc1 | A | 844805 | 0.0418 | 0.0510 | 0.0630 | 0.1045 | 2.0818 | 8.2122 | 9.6549 | 1.8770 | 3.1357 |
| 0 | idc2 | A | 844805 | 0.0046 | 0.0064 | 0.0080 | 0.0388 | 1.9338 | 7.8652 | 9.4339 | 1.7860 | 3.0742 |
| 1 | vdc1 | V | 1226 | 255.6440 | 258.7753 | 261.4460 | 263.2285 | 265.1028 | 267.7080 | 271.3500 | 263.2523 | 2.6749 |
| 1 | vdc2 | V | 1226 | 194.6570 | 200.5577 | 202.4325 | 204.0525 | 205.8000 | 209.1983 | 260.9270 | 204.9584 | 5.9844 |
| 1 | idc1 | A | 1226 | 8.6613 | 8.7727 | 8.8751 | 9.1310 | 9.3217 | 9.4214 | 9.4946 | 9.1029 | 0.2344 |
| 1 | idc2 | A | 1226 | 0.0465 | 8.4549 | 8.5899 | 8.8388 | 9.0470 | 9.1426 | 9.4987 | 8.7535 | 0.7109 |
| 2 | vdc1 | V | 5695 | 240.2350 | 246.8404 | 250.0970 | 255.1210 | 261.3260 | 267.2385 | 271.8070 | 255.8909 | 6.6947 |
| 2 | vdc2 | V | 5695 | 0.8570 | 227.2595 | 232.0375 | 237.2230 | 244.5755 | 258.5468 | 351.5870 | 238.8638 | 15.2333 |
| 2 | idc1 | A | 5695 | 7.5460 | 7.8330 | 8.2621 | 8.9781 | 9.1494 | 9.3198 | 9.6181 | 8.7449 | 0.5057 |
| 2 | idc2 | A | 5695 | 0.0442 | 6.6115 | 7.7809 | 8.4060 | 8.6061 | 8.8145 | 9.0537 | 8.1173 | 0.8279 |
| 3 | vdc1 | V | 1204 | 0.7783 | 1.6395 | 1.6504 | 251.6510 | 264.0990 | 266.8979 | 269.5480 | 133.0015 | 131.2002 |
| 3 | vdc2 | V | 1204 | 0.7887 | 2.1527 | 2.1644 | 2.1953 | 270.3670 | 273.0028 | 276.1040 | 135.9845 | 134.1242 |
| 3 | idc1 | A | 1204 | 0.0983 | 0.1015 | 0.1050 | 7.8082 | 9.0650 | 9.1426 | 9.2276 | 4.5886 | 4.4788 |
| 3 | idc2 | A | 1204 | 0.0401 | 0.0432 | 0.0454 | 0.0507 | 8.9871 | 9.0932 | 9.1732 | 4.5093 | 4.4734 |
| 4 | vdc1 | V | 153199 | 154.2880 | 258.3207 | 270.8130 | 282.0240 | 298.8520 | 320.4700 | 362.8930 | 285.3167 | 20.9215 |
| 4 | vdc2 | V | 153199 | 53.4102 | 242.9450 | 261.9555 | 287.9150 | 311.4165 | 348.6480 | 360.1130 | 288.8073 | 31.7565 |
| 4 | idc1 | A | 153199 | 0.2083 | 0.4538 | 2.4055 | 4.0246 | 5.3909 | 7.2223 | 9.3977 | 3.9799 | 2.0028 |
| 4 | idc2 | A | 153199 | 0.0241 | 0.0994 | 0.9181 | 2.6620 | 4.2149 | 6.1335 | 9.4360 | 2.7232 | 1.9457 |

## Joint electrical differences

| Class | Channel | Unit | N | Min | P5 | P25 | Median | P75 | P95 | Max | Mean | Sample SD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | vdc1-vdc2 | V | 844805 | -178.3820 | -10.3280 | -0.4570 | -0.0014 | 0.1929 | 12.2900 | 134.0020 | 0.6580 | 11.2243 |
| 0 | abs(vdc1-vdc2) | V | 844805 | 0.0000 | 0.0198 | 0.0810 | 0.2600 | 5.0770 | 17.8458 | 178.3820 | 4.3564 | 10.3653 |
| 0 | idc1-idc2 | A | 844805 | -1.5314 | 0.0394 | 0.0535 | 0.0601 | 0.1019 | 0.3054 | 2.4578 | 0.0910 | 0.1336 |
| 0 | abs(idc1-idc2) | A | 844805 | 0.0000 | 0.0410 | 0.0538 | 0.0608 | 0.1104 | 0.3326 | 2.4578 | 0.1081 | 0.1201 |
| 1 | vdc1-vdc2 | V | 1226 | -1.2990 | 53.0655 | 57.0992 | 59.2000 | 61.0373 | 63.7225 | 66.2360 | 58.2940 | 6.3451 |
| 1 | abs(vdc1-vdc2) | V | 1226 | 0.5650 | 53.0655 | 57.0992 | 59.2000 | 61.0373 | 63.7225 | 66.2360 | 58.2961 | 6.3256 |
| 1 | idc1-idc2 | A | 1226 | -0.3106 | 0.1009 | 0.2160 | 0.2797 | 0.3570 | 0.4740 | 9.3819 | 0.3494 | 0.6824 |
| 1 | abs(idc1-idc2) | A | 1226 | 0.0004 | 0.1137 | 0.2163 | 0.2801 | 0.3570 | 0.4740 | 9.3819 | 0.3546 | 0.6797 |
| 2 | vdc1-vdc2 | V | 5695 | -89.2450 | 1.6404 | 15.4430 | 18.0630 | 20.6080 | 23.9105 | 267.5428 | 17.0271 | 13.4572 |
| 2 | abs(vdc1-vdc2) | V | 5695 | 0.0290 | 5.5476 | 15.5505 | 18.1230 | 20.6935 | 24.1036 | 267.5428 | 18.1205 | 11.9440 |
| 2 | idc1-idc2 | A | 5695 | -0.0460 | 0.3344 | 0.4472 | 0.5348 | 0.6270 | 1.2278 | 9.5734 | 0.6276 | 0.6375 |
| 2 | abs(idc1-idc2) | A | 5695 | 0.0338 | 0.3344 | 0.4472 | 0.5348 | 0.6270 | 1.2278 | 9.5734 | 0.6276 | 0.6374 |
| 3 | vdc1-vdc2 | V | 1204 | -274.4697 | -271.3441 | -268.7333 | 250.1291 | 261.9103 | 264.7462 | 267.3805 | -2.9831 | 265.3137 |
| 3 | abs(vdc1-vdc2) | V | 1204 | 246.1843 | 258.7170 | 261.8825 | 265.1576 | 268.7333 | 271.3441 | 274.4697 | 265.1879 | 4.1479 |
| 3 | idc1-idc2 | A | 1204 | -9.0747 | -8.9865 | -8.8825 | 7.7670 | 9.0179 | 9.0978 | 9.1791 | 0.0793 | 8.9517 |
| 3 | abs(idc1-idc2) | A | 1204 | 7.7393 | 8.7856 | 8.8791 | 8.9572 | 9.0210 | 9.0978 | 9.1791 | 8.9477 | 0.1122 |
| 4 | vdc1-vdc2 | V | 153199 | -178.3370 | -64.3989 | -30.3970 | 0.3520 | 22.7595 | 55.3264 | 193.3528 | -3.4906 | 37.2235 |
| 4 | abs(vdc1-vdc2) | V | 153199 | 0.0010 | 4.0468 | 15.1715 | 25.2800 | 40.7920 | 72.7905 | 193.3528 | 30.4958 | 21.6281 |
| 4 | idc1-idc2 | A | 153199 | -8.5261 | -0.3152 | 0.2173 | 1.0306 | 2.3300 | 4.5205 | 8.9833 | 1.2567 | 2.0019 |
| 4 | abs(idc1-idc2) | A | 153199 | 0.0002 | 0.1358 | 0.2523 | 1.2296 | 2.5454 | 4.9848 | 8.9833 | 1.6873 | 1.6552 |

Signed values distinguish which channel is larger; absolute values quantify imbalance. These are same-observation relationships, not differences of independently sampled class averages. Marginal quantile boxes do not recover a full four-dimensional joint distribution.

| Class | N | V pair Pearson | V pair Spearman | I pair Pearson | I pair Spearman | ΔV/ΔI Pearson | ΔV/ΔI Spearman |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 844805 | 0.996369 | 0.972227 | 0.999271 | 0.937474 | -0.496055 | -0.338312 |
| 1 | 1226 | 0.084545 | 0.299893 | 0.284087 | 0.755469 | -0.781774 | -0.849231 |
| 2 | 5695 | 0.469574 | 0.838923 | 0.638650 | 0.903597 | -0.025318 | -0.840286 |
| 3 | 1204 | -0.999839 | -0.739401 | -0.999788 | -0.744533 | 0.999873 | 0.580600 |
| 4 | 153199 | 0.045605 | -0.006958 | 0.486217 | 0.545716 | -0.686352 | -0.835128 |

## Distribution overlap

Number of class pairs with intersecting full observed min–max ranges (out of 10 pairs per channel): vdc1=10/10, vdc2=10/10, idc1=10/10, idc2=10/10. Extrema can be driven by a few unusual observations; central intervals give a different, still descriptive view.

| Classes A / B | Channel | Unit | Intersection of P5–P95 intervals | A observations inside | B observations inside |
| --- | --- | --- | --- | --- | --- |
| 0 / 1 | vdc1 | V | [258.7753, 267.7080] | 6.5397% | 89.8858% |
| 0 / 1 | vdc2 | V | [200.5577, 209.1983] | 0.2402% | 89.8858% |
| 0 / 1 | idc1 | A | None | 0.0000% | 0.0000% |
| 0 / 1 | idc2 | A | None | 0.0000% | 0.0000% |
| 0 / 2 | vdc1 | V | [246.8404, 267.2385] | 10.9642% | 89.9912% |
| 0 / 2 | vdc2 | V | [227.2595, 258.5468] | 5.3673% | 89.9912% |
| 0 / 2 | idc1 | A | [7.8330, 8.2122] | 1.8409% | 18.0509% |
| 0 / 2 | idc2 | A | [6.6115, 7.8652] | 12.1002% | 25.0044% |
| 0 / 3 | vdc1 | V | [1.6395, 266.8979] | 28.8193% | 89.9502% |
| 0 / 3 | vdc2 | V | [2.1527, 273.0028] | 35.3284% | 89.9502% |
| 0 / 3 | idc1 | A | [0.1015, 8.2122] | 48.3478% | 45.0997% |
| 0 / 3 | idc2 | A | [0.0432, 7.8652] | 35.5114% | 45.0997% |
| 0 / 4 | vdc1 | V | [258.3207, 292.5700] | 26.7137% | 62.9776% |
| 0 / 4 | vdc2 | V | [242.9450, 290.0140] | 31.2015% | 47.9709% |
| 0 / 4 | idc1 | A | [0.4538, 7.2223] | 12.6326% | 89.9999% |
| 0 / 4 | idc2 | A | [0.0994, 6.1335] | 13.0253% | 90.0104% |
| 1 / 2 | vdc1 | V | [258.7753, 267.2385] | 87.3573% | 29.8683% |
| 1 / 2 | vdc2 | V | None | 0.0000% | 0.0000% |
| 1 / 2 | idc1 | A | [8.7727, 9.3198] | 69.4127% | 55.7858% |
| 1 / 2 | idc2 | A | [8.4549, 8.8145] | 44.8613% | 38.3319% |
| 1 / 3 | vdc1 | V | [258.7753, 266.8979] | 85.2365% | 43.5216% |
| 1 / 3 | vdc2 | V | [200.5577, 209.1983] | 89.8858% | 0.0000% |
| 1 / 3 | idc1 | A | [8.7727, 9.1426] | 45.0245% | 44.6013% |
| 1 / 3 | idc2 | A | [8.4549, 9.0932] | 80.4241% | 44.8505% |
| 1 / 4 | vdc1 | V | [258.7753, 267.7080] | 89.8858% | 12.7586% |
| 1 / 4 | vdc2 | V | None | 0.0000% | 0.0000% |
| 1 / 4 | idc1 | A | None | 0.0000% | 0.0000% |
| 1 / 4 | idc2 | A | None | 0.0000% | 0.0000% |
| 2 / 3 | vdc1 | V | [246.8404, 266.8979] | 88.8850% | 45.0166% |
| 2 / 3 | vdc2 | V | [227.2595, 258.5468] | 89.9912% | 0.0000% |
| 2 / 3 | idc1 | A | [7.8330, 9.1426] | 68.9025% | 44.9336% |
| 2 / 3 | idc2 | A | [6.6115, 8.8145] | 90.0088% | 0.3322% |
| 2 / 4 | vdc1 | V | [258.3207, 267.2385] | 31.7296% | 12.3898% |
| 2 / 4 | vdc2 | V | [242.9450, 258.5468] | 25.4609% | 15.4759% |
| 2 / 4 | idc1 | A | None | 0.0000% | 0.0000% |
| 2 / 4 | idc2 | A | None | 0.0000% | 0.0000% |
| 3 / 4 | vdc1 | V | [258.3207, 266.8979] | 44.2691% | 11.8075% |
| 3 / 4 | vdc2 | V | [242.9450, 273.0028] | 44.8505% | 28.8775% |
| 3 / 4 | idc1 | A | [0.4538, 7.2223] | 0.0000% | 89.9999% |
| 3 / 4 | idc2 | A | [0.0994, 6.1335] | 0.0000% | 90.0104% |

“None” means only that the two **central marginal intervals** do not intersect. Tails can still overlap, and absence of overlap in one marginal summary does not certify a separator, fault mechanism or generalization to another acquisition regime. Conversely, overlapping central intervals do not imply identical multivariate distributions. Interval intersections across different channels need not describe the same observations.

## Class-specific descriptive findings

- **Normal operation:** 615,051/844,805 observations (72.8039%) have irradiance below the existing 100 W/m² regime boundary. The vdc1 median is 2.3061 V but the mean is 109.2540 V and P75 is 267.6650 V. This marked regime mixture makes a single “normal voltage band” misleading. Median absolute voltage/current differences are 0.2600 V / 0.0608 A.
- **Short circuit:** the median signed voltage difference is 59.2000 V, compared with 18.0630 V for resistive degradation. However, the classes' vdc1 central intervals intersect at [258.7753, 267.2385] V and their current distributions also overlap. These contrasts describe sampled operating states, not a diagnostic cutoff.
- **Resistive degradation:** median absolute current difference is 0.5348 A. Its vdc2 extrema [0.8570, 351.5870] V are much broader than its central interval [227.2595, 258.5468] V, demonstrating why extrema alone are poor representative ranges. No unusual observation is deleted here.
- **Open circuit:** 603 observations have vdc1>vdc2 and 601 have vdc1<vdc2. Median absolute differences are 265.1576 V and 8.9572 A, despite signed means of only -2.9831 V and 0.0793 A. Opposite difference directions cancel in the signed means; the absolute values and near-perfect negative pairwise Pearson correlations expose the paired structure. The labels alone do not establish the physical cause of each individual observation.
- **Natural building shade:** median absolute voltage/current differences are 25.2800 V / 1.2296 A. Its vdc1 central interval intersects normal at [258.3207, 292.5700] V; all four normal/shade central marginal intervals overlap. Shade remains environmental, and electrical overlap prevents a guaranteed class-specific UI input range.

## Interpretation boundary

The tables describe observed **P(measurements | class, TRAIN)**, not the reverse classification probability or the Random Forest decision boundaries. A forest combines learned feature splits across trees, fitted TRAIN preprocessing and class weighting; its boundaries cannot be inferred from class-specific min/max, medians or percentile intervals. Normal and shade can overlap in electrical space, and relative channel relationships must be considered alongside marginal distributions. Any visual range illustration must remain descriptive and must not promise a returned class for arbitrary values inside a range.

No new classifier rule, confidence estimate, feature selection, threshold optimization or deployment change is proposed. Existing TEST-exposure and lack-of-independent-session limitations remain unchanged. These summaries are not a held-out evaluation, a safety envelope, physical causality or field-validated fault limits. Frontend implementation is intentionally deferred until review of the actual distributions.
