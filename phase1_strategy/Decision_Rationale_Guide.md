# Decision rationale and presentation guide

Ruganji Prince | AISD Assignment 2 | Phase 1 | 12 October 2026

The original author dataset is approved. These are measured audit findings and proposed engineering decisions, not model results. Full evidence is in Phase1_Strategy_Report.pdf; Decision_Log.csv is the compact ledger. Phase 2 requires separate explicit approval.

## 1. Original author dataset

**Simple explanation:** We need real measurements and a defensible account of plant conditions. The original author provides both; cite the original rather than a copy.

**Technical evidence:** Verified hashes; student approval.

**Selected approach:** Use pinned original, retain source limitations.

**Alternatives and why not selected:** PVDAQ lacks verified target; DS226 has rule labels.

**Assumptions and limitations:** The export is the documented experiment; annotation precision and exported count differences remain unresolved. Additional risk: Single plant; count discrepancy.

**Phase 2 verification:** Verify provenance and report transfer limits.

**Effect on the research question:** Provides a labeled basis for measuring sensing/performance trade-offs without changing the research question.

## 2. Five-class target plus equipment alert

**Simple explanation:** The label names an operating state. A building blocking sunlight is different from a broken electrical connection, so report equipment alerts separately.

**Technical evidence:** Source has five nominal labels; shade is environmental.

**Selected approach:** Keep Y=0..4; score equipment probabilities separately.

**Alternatives and why not selected:** Binary-all-anomalies obscures shade/fault distinction.

**Assumptions and limitations:** Source state labels correspond to the measurements; no per-row independent maintenance log is exported. Additional risk: Source annotations lack independent logs.

**Phase 2 verification:** Classwise scores and shade FPR.

**Effect on the research question:** Avoids equating environmental change with hardware failure and keeps maintenance relevance visible.

## 3. Source alignment

**Simple explanation:** A row number is a position in a file, not a date or a measured time gap. Do not invent clocks from nominal logging frequency.

**Technical evidence:** Equal array lengths; acquisition description.

**Selected approach:** Preserve index correspondence; no fabricated clocks.

**Alternatives and why not selected:** No defensible timestamp reconstruction.

**Assumptions and limitations:** Matching source positions correspond across channels; actual elapsed intervals and day boundaries are unobservable. Additional risk: Alignment cannot be clock-verified.

**Phase 2 verification:** Schema checks; source clarification if available.

**Effect on the research question:** Prevents unsupported time-aware claims while permitting honest PC replay and index-based evaluation.

## 4. Missingness classification

**Simple explanation:** A blank cell and an observation that never appears are different. No blanks are exported, while simultaneous temperature/irradiance zeros look suspicious.

**Technical evidence:** Zero exported NaNs; 62 suspicious paired zeros.

**Selected approach:** Mechanism uncertain; preserve raw and flag suspected events.

**Alternatives and why not selected:** Cannot prove MCAR with constant indicators.

**Assumptions and limitations:** Joint-zero patterns are suspected acquisition issues, not confirmed sentinels; no MCAR/MAR/MNAR mechanism is identified. Additional risk: Omitted rows unknowable.

**Phase 2 verification:** Dropout stress and suspect-zero sensitivity.

**Effect on the research question:** Keeps missing-data resilience separate from fabricated missingness evidence.

## 5. Conservative cleaning

**Simple explanation:** Different measurements need different validity rules. Negative temperature can be real; a tiny negative irradiance reading can be near-zero noise.

**Technical evidence:** One -0.0381 irradiance; negative temperatures plausible.

**Selected approach:** Proposed near-zero irradiance clamp; retain negative temperatures.

**Alternatives and why not selected:** Blanket zero deletion corrupts low-light data.

**Assumptions and limitations:** RMS channels have nonnegative magnitude; the proposed -1 W/m^2 tolerance is an uncalibrated engineering convention. Additional risk: -1 tolerance is engineering assumption.

**Phase 2 verification:** Compare unchanged irradiance and quality sensitivity.

**Effect on the research question:** Protects physically meaningful PV conditions that sparse models need to recognize.

## 6. Imputation and abstention

**Simple explanation:** A middle training value is a cheap fallback, but can still be wrong for daylight operation. Stop confident predictions when measurement loss becomes sustained.

**Technical evidence:** Skew/mean-median gaps; no baseline NaNs.

**Selected approach:** Train median, per-channel indicators, short causal fallback and abstention.

**Alternatives and why not selected:** Mean not robust; KNN expensive; interpolation lacks time.

**Assumptions and limitations:** One missing channel can occasionally be handled by a cheap fallback; median estimates may be very wrong during generation. Additional risk: Median can insert low-light values during generation.

**Phase 2 verification:** Training-only masks; all-row recall and coverage.

**Effect on the research question:** Makes monitoring availability explicit; an unreliable imputed alert is not useful monitoring.

## 7. Outlier retention

**Simple explanation:** Unusual measurements may be the fault signal we need. Statistical fences do not by themselves establish broken sensors.

**Technical evidence:** All six training IQR/z screens flag zero.

**Selected approach:** Statistical flags; no automatic capping.

**Alternatives and why not selected:** Generic winsorization can erase faults.

**Assumptions and limitations:** Physical validity and operating condition matter more than an isolated statistical threshold; future local spikes may require review. Additional risk: Global mixture screens may miss local anomalies.

**Phase 2 verification:** Within-condition review; cap only confirmed-artifact sensitivity.

**Effect on the research question:** Preserves rare fault information rather than making data look cleaner by removing it.

## 8. Association matching

**Simple explanation:** Class codes are names, not physical distances. Use methods that compare measurements with nominal classes rather than treating code 4 as twice code 2.

**Technical evidence:** Continuous X, nominal five-class Y.

**Selected approach:** Training MI plan; descriptive one-versus-rest effects.

**Alternatives and why not selected:** Pearson on numeric label codes is meaningless.

**Assumptions and limitations:** Associations are descriptive; adjacent-row independence and causal attribution are unsupported. Additional risk: Dependence/imbalance biases ranks.

**Phase 2 verification:** Fixed sampling/seed; block coverage; no causal claims.

**Effect on the research question:** Ranks observed sensor information without claiming physical causes.

## 9. Keep collinear sensors

**Simple explanation:** Two strings often behave similarly, but their differences during faults may be valuable. Keep the full reference and test sensor removal explicitly.

**Technical evidence:** Five correlated pairs; five VIFs >10.

**Selected approach:** Retain full reference; regularize linear model; named ablations.

**Alternatives and why not selected:** Automatic correlation deletion sacrifices string information.

**Assumptions and limitations:** Independent acquisition channels may carry fault-specific information despite global correlation. Additional risk: Attribution unstable under correlation.

**Phase 2 verification:** Compare classwise losses and explanatory stability.

**Effect on the research question:** Lets the central ablation experiment determine whether removing a sensor is defensible.

## 10. Encoding/scaling/transformation

**Simple explanation:** Scaling makes numerical units comparable; transforming changes their shape. Neither action reduces the number of measurements needed.

**Technical evidence:** No categorical X; differing units; mixed regimes.

**Selected approach:** No X encoding; StandardScaler linear, native tree; no reference log.

**Alternatives and why not selected:** Ordinal label geometry and blind log are inappropriate.

**Assumptions and limitations:** The chosen linear model is penalty-sensitive; tree thresholds are normally invariant to monotonic scaling. Additional risk: Standardization does not normalize shape.

**Phase 2 verification:** Fit per training fold; validate alternative scalers/log1p.

**Effect on the research question:** Supports lightweight models and physically understandable explanations.

## 11. PCA optional

**Simple explanation:** Mixing six readings into two mathematical components still requires taking those six readings. PCA and sensor removal answer different questions.

**Technical evidence:** Only six physical channels; high correlation.

**Selected approach:** Training-only variance analysis at 90/95%; original-sensor reference.

**Alternatives and why not selected:** PCA mixes signals and still needs its source sensors.

**Assumptions and limitations:** Variance explains numerical structure, not guaranteed rare-fault signal or hardware savings. Additional risk: Rare faults can occupy low-variance directions.

**Phase 2 verification:** Report loadings and predictive performance separately.

**Effect on the research question:** Separates mathematical compression from physical sensing reduction.

## 12. Buffered operating-block split

**Simple explanation:** Close neighbors are almost the same operating conditions. Keep whole measured operating blocks apart and preserve file order instead of randomly mixing rows.

**Technical evidence:** 16 signal-defined blocks; high lag dependence; 70% misses short circuit.

**Selected approach:** 12/2/2 ordered blocks; exclude two whole separators.

**Alternatives and why not selected:** Random rows/short buffers fail; verified days unavailable.

**Assumptions and limitations:** Low-irradiance separators isolate measured regimes but do not certify separate days or statistically independent sessions. Additional risk: Blocks are proxies; residual same-site dependence.

**Phase 2 verification:** Sensitivity at irradiance 50/100/150 and run length 1800/3600/7200; report manifest changes.

**Effect on the research question:** Makes full/sparse results comparable without optimistic adjacent-row leakage.

## 13. Limited validation, not artificial CV

**Simple explanation:** Many readings are not many independent experiments. A few fault blocks cannot justify impressive-looking random five-fold validation.

**Technical evidence:** Short circuit concentrated in late blocks.

**Selected approach:** Block 13 selects settings; block 14 selects alert threshold.

**Alternatives and why not selected:** Early expanding folds lack class coverage.

**Assumptions and limitations:** Validation blocks remain representative enough for a small search; independent event coverage is limited. Additional risk: Few independent fault blocks.

**Phase 2 verification:** Small predeclared search; per-block results; freeze before test.

**Effect on the research question:** Matches evidence strength to the number of actual operating situations.

## 14. Ablation and useful detection

**Simple explanation:** Remove sensors deliberately and compare what is lost and saved under the same evaluation conditions. A small loss against a weak reference is not enough.

**Technical evidence:** Research question; temperature channel aggregates four probes.

**Selected approach:** Same partitions/models; fixed configs; macro-F1 Delta_s.

**Alternatives and why not selected:** Features are not devices; weak-reference delta insufficient.

**Assumptions and limitations:** A common evaluation population, bounded model budget and acquisition ledger make the configuration comparison fair. Additional risk: Sensor cost and rural burden unknown.

**Phase 2 verification:** Absolute targets, class recall, FPR, footprint and latency.

**Effect on the research question:** Connects absolute detection quality, sparse-loss, sensor requirements and computational cost.

## 15. Infrastructure and phase boundary

**Simple explanation:** Another person should reproduce the source and audit. Local documents do not constitute a live GitHub submission or permission to begin the next phase.

**Technical evidence:** Git unavailable; username supplied; publication forbidden without permission.

**Selected approach:** Local verified artifacts; manual Git setup; stop before Phase 2.

**Alternatives and why not selected:** Username is not authorization to create/push remote.

**Assumptions and limitations:** Pinned hashes and versions preserve local reproduction; remote access and course submission are manual infrastructure steps. Additional risk: Live GitHub/Canvas rubric unmet.

**Phase 2 verification:** User reviews report and separately authorizes remote/Phase 2.

**Effect on the research question:** Keeps work reproducible and preserves the strict Phase 1/Phase 2 boundary.

## Presentation questions and suggested answers

**Why this dataset rather than PVDAQ?**

It supplies real electrical/environmental readings and experimental state annotations, with manageable files and six channels for ablation. The PVDAQ sample supplies operational structure but no verified fault target. A PVDAQ quality audit would not establish comparable fault F1.

**What are N and P?**

N=1,373,798 raw source positions, P=7 total variables including Y, and six predictor channels. Repeated positions are not 1.37 million independent experiments.

**Are these natural field faults?**

Three equipment conditions were physically introduced; shade came from buildings. Resistive loads emulate a degradation condition, not years of natural aging. Public annotations lack independently exported experiment logs.

**Did you recover dates or measurement days?**

No. The files have no clocks/day/session IDs. Sixteen operating blocks come from observed low-irradiance separators; their resemblance to the documented day count does not establish dates or elapsed time.

**Why is random splitting dangerous?**

Training adjacent-position correlations exceed 0.9997. Random partitions can share nearly identical conditions and event fragments. We retain source order and complete measured blocks, with whole separator buffers.

**What are the exact final split proportions?**

Twelve/two/two of sixteen operating blocks, or 75/12.5/12.5% of blocks. After withholding two boundary separators, retained-row shares are 79.2498/9.2139/11.5363%; N values are 1,006,129, 116,977 and 146,461. These are not a reconstructed calendar split.

**How did you prevent leakage?**

The plan freezes groups first, fits every learned transformation and class weight on training only, chooses model settings on validation block 13 and alert threshold on block 14, then evaluates test blocks 15–16 once. This prevents fitted preprocessing leakage; absent logs still limit session independence.

**Why not five-fold cross-validation?**

Only late blocks contain substantial short-circuit examples. Earlier expanding folds lack the class; random row folds share event conditions. A small supported holdout is more honest than manufacturing independent replication.

**Why this imputation method?**

Baseline exports have no NaNs. Median plus flags is a contingency baseline because means and medians differ strongly: current1 training mean 2.2481 A versus median 0.1105 A. Median can insert a low-light value in daylight, so its usefulness must be tested and sustained outages cause abstention.

**Is missingness MCAR?**

We cannot determine it: all exported NaN indicators are zero. The 62 simultaneous irradiance/temperature zeros suggest acquisition issues but are not documented missing sentinels. Synthetic MCAR masks are test assumptions, not diagnoses of original data.

**Why retain outliers?**

All six training IQR and z-score screens flag zero values; broad day/night-mixture fences are not evidence for capping. Genuine faults can produce unusual measurements. We preserve them and separately flag suspected sensor problems.

**Why F1/AP instead of accuracy?**

Normal is 84.6508% of raw rows and short circuit only 0.4367%. A normal-only classifier looks accurate while missing every fault. Macro-F1, per-class recall and one-versus-rest AP expose this; AP is the declared PR summary, not automatically trapezoidal PR area.

**How does imbalance change training?**

Weights, if used, are computed only from the relevant training partition and compared with unweighted models. Oversampling dependent readings does not create new independent faults. Report per-class supports and false alarms.

**Why keep correlated voltage/current channels?**

String channels can agree in normal operation and diverge during string faults. Five pairs exceed the 0.85 screen and five VIF values exceed 10, but those warnings do not prove physical channels are dispensable.

**Why use or not use PCA?**

PCA can describe redundancy after training-only scaling, with 90/95% variance cutoffs. It mixes channels and may discard low-variance fault information, so original measurements remain the reference. No PCA was fitted in Phase 1.

**What is PCA versus physical sensor reduction?**

Two components built from six measurements still need those measurements. Temperature is one exported input but aggregates four probes. Sensor ablation tracks input channels and acquisition requirements separately from mathematical feature count.

**How does sensor ablation answer the question?**

Compare full F6 and the predeclared E5/E4/C3/C2/S4/S2 configurations with identical partitions, labels, model budget and scoring rows. Delta_s uses five-class macro-F1; classwise losses, latency, artifact size and acquisition points determine whether a sparse configuration is useful.

**What does practically useful mean?**

The study proposes macro-F1>=0.80, equipment-class recall>=0.90, equipment FPR<=1%, at most four channels with macro-F1 loss<=0.05, PC inference p95<=10 ms and artifact<=10 MiB. These are unmeasured engineering aspirations, not field safety standards. Maintenance cost, severity and actual prevalence are needed for operational acceptance.

**How does the project relate to Rwanda?**

It studies a sensing/compute trade-off relevant to resource-constrained monitoring. A Brazilian clear-day experimental installation cannot certify behavior under Rwanda weather, hardware, maintenance practices or natural fault prevalence.

**What are the main limitations?**

Absent clocks/logs, provisional index alignment, one installation, scheduled induced conditions, imbalance and few equipment-fault blocks, uncertain joint-zero/label transitions, paper/export count discrepancy, and unverified geographic transfer.

**What if future labels are unavailable?**

Report novelty/residual scores, proxy agreement and quality behavior, seek independent event review, and do not invent precision/recall/F1 against verified faults. Keep source annotations, proxy rules, synthetic masks and model scores separate.

**Have you found a useful minimal sensor set?**

No. Phase 1 supplies the audit and plan only. Classifier training, final diagnostics and sensor ablation need separate explicit approval.

**Is the assignment submitted?**

Local Phase 1 artifacts are prepared and checked. Git installation/init, explicitly authorized GitHub creation/push and the Canvas live URL remain outstanding; a local PDF is not an online submission.
