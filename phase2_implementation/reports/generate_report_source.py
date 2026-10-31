"""Generate the IEEE reflection source and decision log from preprocessing evidence.

This command reads compact CSV/JSON only. It never executes preprocessing,
fits an estimator, generates a diagnostic image, or accesses model artifacts.
"""
from pathlib import Path
import csv
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
E=ROOT/'phase2_implementation/compliance'
def load(n):return json.loads((E/n).read_text(encoding='utf8'))
def csvrows(n):return list(csv.DictReader((E/n).open(encoding='utf8')))
def esc(s):
    mapping={'\\':r'\textbackslash{}','_':r'\_','&':r'\&','%':r'\%','#':r'\#','$':r'\$','{':r'\{','}':r'\}','≥':r'$\geq$','≤':r'$\leq$','×':r'$\times$','²':r'$^2$','°':r'$^\circ$','—':'---','–':'--','−':'-'}
    return ''.join(mapping.get(c,c) for c in str(s))
def num(x,places=4):return f'{float(x):.{places}f}'

def main():
    evidence=load('Preprocessing_Evidence.json');audit=load('Empirical_Audit.json')
    dist=csvrows('Training_Distribution_Diagnostics.csv');dims=csvrows('Pipeline_Stage_Dimensions.csv')
    scales=csvrows('Scaling_Diagnostics.csv');pca=csvrows('PCA_Diagnostics.csv')
    mi=evidence['mutual_information']['scores_nats'];vif=audit['verified_VIF']
    maxmean=max(abs(float(x['mean'])) for x in scales if x['representation']=='standard')
    irr={x['representation']:x for x in scales if x['sensor']=='irr'}
    # Planned wording is read against the preserved Phase 1 strategy. No fictitious deviation.
    decisions=[
      ('Missingness / imputation','TRAIN-median contingency and availability indicators','Retained; no exported gaps to fill','0/9,616,586 missing cells (0%); Fig. 1; Table I'),
      ('Suspicious paired zeros','Annotate, without assuming a missing sentinel','Retained as observations, not relabeled missing','62 paired irr/pvt zeros; runs 1/32/29; Fig. 1'),
      ('Negative irradiance','Near-zero physical convention with caution','Retained: -1 <= irr < 0 becomes zero in processed data','One value -0.0381 W/m²; no raw CSV change; Fig. 3'),
      ('Negative temperature','Retain physically valid negative Celsius','Retained; no automatic zero-floor','24,172 released negative-Celsius rows; TRAIN min -1.6543 °C; Fig. 3'),
      ('Outlier policy','IQR / distribution-qualified Z screening; no automatic capping','Retained; no winsorization or row deletion','All six TRAIN IQR counts=0 (0%); skew 0.0683–1.1450; Table II; Fig. 3'),
      ('Target / imbalance','Nominal f_nv; no categorical predictor encoding or initial SMOTE','Retained observed labels and natural partition prevalence','TRAIN counts 844805/1226/5695/1204/153199; normal 83.966%; Fig. 2'),
      ('Predictor correlation','TRAIN Pearson |r| >= 0.85; assess physical meaning before deletion','Retained screen; no automatic predictor removal','Five flagged pairs, r=0.8623–0.9891; Figs. 4–5; Table III'),
      ('VIF / retention','TRAIN VIF >10 warning; preserve reference physical inputs','Retained; all six reference channels remain','Five VIF>10; maximum 56.3457; Table IV; Figs. 4–5'),
      ('Target relevance','TRAIN-only MI for continuous predictors / nominal target','Implemented descriptive proportional-sample MI; no feature deletion','N=50,000, k=3, seed=42; MI 0.1124–0.3006 nats; Fig. 6; Table IV'),
      ('Standardization','TRAIN-fitted standardization for scale-sensitive representations','Retained six-channel standardized reference; flags unscaled','Max absolute TRAIN scaled mean '+f'{maxmean:.2e}'+'; each population std=1; Fig. 7; Table V'),
      ('Scaling alternatives','Robust/MinMax sensitivity; optional justified log transform','Robust/MinMax diagnostic only; no log transform selected','irr robust median=0, IQR=1; MinMax TRAIN range=[0,1]; skew stays 0.8745; Fig. 7'),
      ('Exploratory PCA','TRAIN-standardized variance/loadings; not physical sensor reduction','Implemented six-component diagnostic; reference pipeline not reduced','PC1=82.5301%; first two=95.1677%; 90%/95% need two; Fig. 8; Table VI'),
      ('Ordered split','12/2/2 signal-block split and withheld separators','Retained exact bounds; no random row split or fabricated time','N=1006129/116977/146461; 104231 separators; Table VII'),
      ('Leakage controls','Fit learned quantities on TRAIN; transform held-out only','Retained; guarded entry point rejects held-out fit before factory call','All fit-ledger N=1006129; TRAIN digest verified; Table VIII'),
      ('Physical features','Domain-grounded features with retained-parent constraints','Existing optional electrical-derived representation retained; not a sensor-selection outcome','4 raw + 5 derived + 4 flags=13 columns; all parents retained; Table VII'),
      ('Output dimensions','Track retained observations and physical/mathematical inputs','Measured every quality, median, flag, feature and scaling stage','Primary: N×6 -> N×12; alternatives N×8 / N×13; Table VII'),
      ('Population discrepancy','Verify source/count mismatch without forcing agreement','Retained full raw population; descriptive irradiance-qualified audit','irr >=100 gives N=515958 and literature counts exactly; source does not specify exact filter; Table I')]
    fields=['Preprocessing step','Phase 1 planned strategy','Phase 2 actual execution / change','Empirical justification / metric / figure']
    with (E/'Strategy_vs_Reality.csv').open('w',encoding='utf8',newline='') as f:w=csv.writer(f);w.writerow(fields);w.writerows(decisions)
    md='# Preprocessing strategy versus reality\n\nNo downstream predictive result is used. Retained strategies are explicitly identified; descriptive implementation additions do not imply model or sensor selection.\n\n| '+' | '.join(fields)+' |\n| '+' | '.join(['---']*4)+' |\n'
    for row in decisions:md+='| '+' | '.join(x.replace('|','\\|') for x in row)+' |\n'
    (E/'Strategy_vs_Reality.md').write_text(md,encoding='utf8')
    out=[]
    def add(s):out.append(s)
    def table(caption,label,headers,rows,spec=None,wide=False):
        env='table*' if wide else 'table';width=r'\textwidth' if wide else r'\columnwidth'
        if spec is None:spec='l'+'r'*(len(headers)-1)
        add('\\begin{'+env+'}[!t]\n\\caption{'+caption+'}\\label{'+label+'}\n\\centering\\footnotesize\n')
        add('\\begin{tabularx}{'+width+'}{'+spec+'}\n\\toprule\n'+' & '.join(headers)+r' \\ \midrule'+'\n')
        for row in rows:add(' & '.join(row)+r' \\'+'\n')
        add('\\bottomrule\n\\end{tabularx}\n\\end{'+env+'}\n')
    add(r'''\documentclass[conference]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage{amsmath,amssymb,graphicx,booktabs,tabularx,array,url}
\usepackage[hidelinks]{hyperref}
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}
\title{Photovoltaic Data Preprocessing and Feature Engineering:\\An Empirical Strategy-to-Execution Audit}
\author{\IEEEauthorblockN{Ruganji Prince}
\IEEEauthorblockA{Carnegie Mellon University Africa\\04-652 Artificial Intelligence System Design\\Assignment 3: Data Preprocessing Phase 2}}
\begin{document}
\maketitle
\begin{abstract}
This reflection executes and audits a photovoltaic measurement preprocessing strategy using the released 1,373,798-row dataset. The workflow retains suspicious observations, isolates learned statistics to the training partition, and implements target-free transformations through Scikit-Learn Pipeline and ColumnTransformer. Eight diagnostic figures support numerical checks of missingness, distributions, collinearity, target association, scaling and exploratory PCA. The six-channel reference produces twelve mathematical inputs with availability indicators; alternative representations are documented without a predictive comparison. No classifier is fitted and no deployment-performance conclusion is drawn.
\end{abstract}
\begin{IEEEkeywords}
Photovoltaic measurements, preprocessing, feature engineering, data quality, leakage prevention, mutual information, PCA.
\end{IEEEkeywords}

\section{Scope, Data and Source Audit}
The current milestone is data preprocessing and feature engineering. The original-author dataset~\cite{dataset} and associated monitoring study~\cite{study} provide two provisionally aligned source vectors. The immutable CSV preserves exported source order and contains $N=1{,}373{,}798$ observations and $P=7$ variables: six continuous predictors and nominal target $f\_nv$ (Table~\ref{tab:data}). Voltage/current quantities are source-described DC RMS measurements; module temperature aggregates source probes. Integer target codes are labels, not an ordinal or continuous measurement.

The study describes nominal 1\,Hz acquisition, per-second electrical RMS calculations, one-second irradiance/temperature averages and a 16-day experiment. Released arrays contain no timestamp. Absolute time and uninterrupted one-second spacing cannot be reconstructed. Sixteen signal-defined blocks are therefore not verified days, sessions or hours. All references to positions describe export order only.

The raw class counts are 1,162,931 / 5,999 / 10,371 / 6,024 / 188,473 for normal / short circuit / resistive degradation / open circuit / natural building shade. Filtering $irr\geq100\,\mathrm{W/m^2}$ yields 515,958 rows and the literature counts 309,253 / 5,999 / 10,371 / 6,024 / 184,311 exactly. This suggests a possible evaluation-population explanation, but the study does not explicitly document that exact filter. Low-irradiance values are not all labeled nighttime, and no rows are removed to force agreement with the paper.
''')
    table('Raw schema and exported missingness (all rows).','tab:data',['Variable / role','Unit','Missing'],[
      [r'\texttt{vdc1}, \texttt{vdc2}: continuous predictors','V',r'0 (0\%)'],
      [r'\texttt{idc1}, \texttt{idc2}: continuous predictors','A',r'0 (0\%)'],
      [r'\texttt{irr}: continuous predictor',r'$\mathrm{W/m^2}$',r'0 (0\%)'],
      [r'\texttt{pvt}: continuous predictor',r'$^\circ$C',r'0 (0\%)'],
      [r'\texttt{f\_nv}: nominal target','---',r'0 (0\%)']],spec='Yrr')
    add(r'''
\section{Quality, Missingness and Outlier Decisions}
\subsection{Missingness and suspicious values}
The implementation audits the approved Phase 1 strategy~\cite{phase1} against executed preprocessing evidence.
Figure~\ref{fig:missing} displays a seed-42 uniform sample of 5,000 TRAIN positions. The full release has zero conventional missing cells out of 9,616,586 (0\%); all 1,373,798 rows are complete. MCAR/MAR/MNAR inference from observed missingness is not applicable: neither Little's MCAR test nor missing-indicator Cramer's V is meaningful with a constant, all-observed mask. Unrecorded intervals remain unobservable. No missingness mechanism is inferred from zero NaNs.

The 62 paired $irr=0,pvt=0$ observations occur in runs of 1/32/29 and remain suspicious observations rather than confirmed missing values. The source does not establish zero as a missing sentinel. One irradiance value is $-0.0381\,\mathrm{W/m^2}$; the predeclared convention clamps $-1\leq irr<0$ to zero only in processed matrices. Values below $-1$ and negative electrical measurements would become unavailable. All 24,172 released negative-Celsius observations remain valid candidates; TRAIN temperature reaches $-1.6543\,{}^\circ$C (Table~\ref{tab:outliers}). The raw CSV remains unchanged.

TRAIN-median contingency imputation and per-retained-channel availability indicators are retained. There are no exported NaNs requiring ordinary imputation. A median is less sensitive to extremes than a mean, but a low-light median can still be unsuitable during generation. Mode is unsuitable for continuous measurements; KNN adds distance and computational assumptions; interpolation requires continuity not established here. Eligibility flags allow at most one unavailable retained channel for at most two consecutive source positions, resetting at gaps/block boundaries; all arrays preserve row alignment.

\subsection{Distribution-qualified screening rather than forced capping}
Figure~\ref{fig:outliers} compares raw with reference-cleaned TRAIN measurements. The audit uses $[Q_1-1.5\,IQR,Q_3+1.5\,IQR]$ and a complementary distribution-qualified $|Z|>3$ screen. Table~\ref{tab:outliers} reports the actual fences, skewness and unbiased Fisher excess kurtosis. Every predictor has zero IQR flags (0\%) and zero $|Z|>3$ flags under the retained full-TRAIN reference. Negative excess kurtosis and multi-regime mixtures do not justify a Gaussian assumption. In particular, current/irradiance mean--median differences show why no universal mean-filling rule is asserted.

No automatic statistical capping or row deletion is selected. Broad full-population fences are screens, not physical-validity certificates; rare fault-state measurements may carry genuine information. Nearly identical panels in Fig.~\ref{fig:outliers} are expected, not evidence of a failed cleaning operation. The only observed quality change is the one near-zero irradiance clamp. This deterministic engineering convention changes one processed value and is not claimed to be literally lossless; its original value remains recoverable in the immutable export.

\section{Relationships, Relevance and Feature Retention}
Figure~\ref{fig:target} shows all TRAIN labels at natural prevalence: 844,805 / 1,226 / 5,695 / 1,204 / 153,199, with normal representing 83.9659\%. No target encoding as a continuous quantity, synthetic oversampling or row duplication is introduced. No categorical predictor requires ordinal or one-hot encoding. Nominal-target association is separated from predictor--predictor correlation.

Figure~\ref{fig:correlation} is the upper-triangle six-predictor TRAIN Pearson matrix; $f\_nv$ is excluded. Table~\ref{tab:pairs} lists all five pairs with $|r|\geq0.85$. Figure~\ref{fig:scatter} displays a uniform seed-42 sample of 20,000 TRAIN positions; correlations and descriptive OLS lines use full TRAIN. Spearman is a possible sensitivity method, not an unperformed result claimed in this report. Association does not imply significance or causation under dependent repeated readings.

The original TRAIN VIF values are independently checked as the diagonal of the inverse centered Pearson matrix, equivalent to intercept-OLS VIF. Five values exceed 10 (Table~\ref{tab:association}), confirming strong dependence without proving physical redundancy. All six reference inputs are retained; VIF/correlation alone does not select a physical-channel removal.

Figure~\ref{fig:mi} is \emph{Target Association / Mutual Information Feature Screening}, not trained-model feature importance. Continuous-predictor/nominal-target MI uses a seed-42 proportional stratified sample of 50,000 TRAIN observations, $k=3$, and TRAIN-fitted standardization. Sample counts are 41,983 / 61 / 283 / 60 / 7,613. Table~\ref{tab:association} gives the scores in nats. Imbalance, ties and dependent rows limit interpretation. These descriptive scores do not trigger predictor deletion or establish causal sensor importance.
''')
    table('TRAIN distribution and outlier audit, before reference cleaning. $N=1{,}006{,}129$ per predictor. All IQR and $|Z|>3$ counts are zero; excess kurtosis is unbiased Fisher kurtosis.','tab:outliers',
          ['Predictor',r'$Q_1$',r'$Q_3$','IQR','Lower','Upper','Skew','Excess kurt.'],
          [[esc(x['sensor'])]+[num(x[k],4) for k in ['q1','q3','IQR','lower_fence','upper_fence','skewness','excess_kurtosis']] for x in dist],spec='Yrrrrrrr',wide=True)
    table(r'Five flagged TRAIN predictor pairs. Full-TRAIN values support Figs.~\ref{fig:correlation}--\ref{fig:scatter}.','tab:pairs',['Predictors','Pearson $r$'],[[esc(a+' / '+b),num(r,6)] for a,b,r in evidence['correlation']['high_pairs']],spec='Yr')
    table('TRAIN-only VIF verification and descriptive nominal-target MI. MI uses a proportional 50,000-observation sample, not model-based importance.','tab:association',['Predictor','VIF','MI (nats)'],[[esc(k),num(vif[k],6),num(mi[k],6)] for k in mi],spec='Yrr')
    add(r'''
\section{Scaling and Exploratory Dimensionality}
Figure~\ref{fig:scaling} compares the existing raw, StandardScaler, RobustScaler and MinMaxScaler irradiance representations. The standardized six-input reference supports scale-sensitive later methods; native-scale alternatives remain documented separately. Standardization aligns units/penalties rather than asserting Gaussian input. Table~\ref{tab:scaling} records actual TRAIN behavior. Across all six standardized channels, absolute means are below $10^{-10}$ and population standard deviations are one within $10^{-10}$.

The irradiance median is 1.8733 while the raw mean is 257.9285\,W/m$^2$. Robust scaling centers the median at zero and maps its IQR to one; MinMax maps the quality-processed TRAIN range to [0,1]. Held-out values are not guaranteed to stay within [0,1]. Positive affine scaling leaves skewness effectively unchanged at 0.8745; the tiny raw-versus-processed difference reflects the single near-zero quality clamp. No log transform was selected or added merely to reproduce an illustrative assignment example. Robust/MinMax are diagnostic alternatives, not a retrospective replacement of the reference preprocessing.

Figure~\ref{fig:pca} includes individual/cumulative variance and both 90\% and 95\% cutoffs. Full-SVD PCA fits a TRAIN-only standardized six-column matrix; covariance eigenvalues are independently verified (Table~\ref{tab:pca}). PC1 explains 82.5301\%; the first two explain 95.1677\%, crossing both cutoffs. A two-component diagnostic view omits 4.8323\% of variance and is not described as lossless. PCA is not selected in the primary pipeline. All six measured inputs remain necessary to compute its components, so two mathematical components do not mean two physical sensors.
''')
    table('TRAIN irradiance scaling behavior (population standard deviation). Values follow quality processing except the raw row.','tab:scaling',['Representation','Mean','Std.','Median','Min.','Max.','Skew'],[[esc(x['representation'])]+[num(x[k],6) for k in ['mean','std_ddof0','median','minimum','maximum','skewness']] for x in scales if x['sensor']=='irr'],spec='Yrrrrrr',wide=True)
    table('Exploratory TRAIN PCA: six standardized physical inputs. Ratios are fractions.','tab:pca',['PC','Eigenvalue','Individual','Cumulative'],[[x['component'],num(x['eigenvalue'],6),num(x['explained_variance_ratio'],6),num(x['cumulative_explained_variance'],6)] for x in pca],spec='Yrrr')
    add(r'''
\section{Leakage-Free Architecture and Measured Outputs}
The outer Pipeline is \texttt{RetainedQuality} $\rightarrow$ \texttt{ColumnTransformer}~\cite{sklearn} (Table~\ref{tab:architecture}). Deterministic quality checks sit before the ColumnTransformer because physical conventions apply to retained-channel DataFrames. Its numeric branch contains median imputation, optional parent-constrained physical features and optional StandardScaler; the parallel branch supplies all retained-channel missingness indicators. No target or source/block identifier enters either branch. Diagnostic Robust/MinMax and StandardScaler--PCA chains are also explicit Pipelines; their learned parameters use TRAIN only.

The ordered partitions retain 1,006,129 / 116,977 / 146,461 rows; separator intervals [1006129,1056990) and [1173967,1227337) withhold 104,231 source positions. TRAIN is [0,1006129), validation [1056990,1173967), and test [1227337,1373798). These rows remain in the raw export. The split follows 12/2/2 signal-defined blocks; the separator rule $irr<100\,\mathrm{W/m^2}$ for at least 3,600 consecutive positions does not establish a verified hour. Neighbor dependence precludes a naive random row split. The original validation sub-block purposes remain planning metadata, not operations executed in this preprocessing submission.

The guarded fit entry point checks the complete ordered TRAIN index before constructing a preprocessor. A held-out fit attempt is rejected before the factory is called. Medians/scaling/PCA parameters and the fit ledger are checked against TRAIN reference evidence; validation/test are transformed only. The historical reserved partition is not claimed to be previously unseen or pristine; no downstream evaluation is presented.

\subsection{Initial and final $N\times P$}
The full raw matrix is $1{,}373{,}798\times7$, including the separate nominal target. The predictor matrix initially has six columns. Table~\ref{tab:dimensions} measures each stage for all three partitions. The primary six-channel reference retains every predictor and partition row; six availability flags produce twelve mathematical design columns. No missing exported measurement is synthesized. Scaling preserves numerical column count, and no information-loss claim is made for the single documented irradiance convention.

The electrical-native and electrical-derived branches are existing alternative representations, not evidence that four channels suffice. Four raw values plus four flags yield eight columns. The derived branch adds $P_1=vdc1\,idc1$, $P_2=vdc2\,idc2$, $P_{total}=P_1+P_2$, $|vdc1-vdc2|$ and $|idc1-idc2|$, giving thirteen mathematical columns. RMS products are proxies, not independent instantaneous-power measurements. Every derived feature uses retained parents. PCA remains a separate diagnostic $N\times6$ to $N\times6$ transformation, with an optional $N\times2$ inspection view; it does not replace the primary $N\times12$ design.

\section{Strategy versus Reality and Reproducibility}
Tables~\ref{tab:strategy1}--\ref{tab:strategy2} compare meaningful Phase 1 preprocessing choices~\cite{phase1} with actual execution and empirical evidence. Retained decisions are identified directly; no deviation is invented. MI/PCA and alternative representations are descriptive implementation additions, not downstream predictive conclusions.

The executed notebook contains thirteen sequential code cells. It reads the immutable export, checks schema/quality, fits only preprocessing/diagnostic estimators on TRAIN, transforms held-out arrays, and records compact measured evidence. All eight existing 300-DPI PNGs are retained byte-for-byte in \texttt{figures/}; no cosmetic regeneration occurred. Reusable transformers, pipeline construction and statistical audit code reside in \texttt{src/}. The report source uses the unmodified IEEEtran conference class~\cite{ieee}; repository instructions distinguish notebook execution, evidence verification and PDF compilation. No private review files, environment, model cache or prediction arrays are required.

\section{Limitations and Current-Stage Conclusion}
One controlled Brazilian plant does not establish geographic or deployment transferability. Neighboring rows are not independent fault episodes; uncertain timing and provisional paired-vector alignment remain limitations. Zero NaNs cannot identify omitted intervals. Full-TRAIN statistical screens may not detect condition-specific anomalies, so zero IQR flags are not a safety guarantee. MI/PCA describe association/variance rather than causality or sensor adequacy. Duplicate removal is not claimed. The output is an empirically justified, reproducible preprocessing implementation; no classifier recommendation, model performance or resource-acceptance result is reported.
''')
    # The output table exposes parallel branches rather than inventing a sequential indicator stage.
    dimrows=[]
    short={'six_standard':'Six standardized (reference)','electrical_native':'Electrical native (alternative)','electrical_derived':'Electrical derived (alternative)'}
    for x in dims:
        dimrows.append([esc(short[x['policy']]),esc(x['partition']),f"{int(x['input_N']):,}",'6',x['retained_physical_channels'],x['post_quality_P'],x['post_median_numeric_P']+'+'+x['indicator_P'],x['post_imputation_plus_indicators_P'],x['post_feature_numeric_P'],x['post_scaling_numeric_P'],x['final_design_P']])
    table(r'Measured predictor stages for every partition. $N$ stays fixed across each row. Raw $P=7$ includes the excluded target; original predictor $P=6$. M+I lists numeric medians plus the parallel indicators; C is their logical concatenation before optional derived features. F and S count numeric columns after feature engineering and scaling; D is the actual final concatenation. Native/derived policies apply no numerical scaler. PCA diagnostic: six input/all components, two-component 95\% view; primary design unchanged.','tab:dimensions',
          ['Representation','Partition','$N$','$P_0$','Phys.','Q','M+I','C','F','S','D'],dimrows,spec='YYrrrrrrrrr',wide=True)
    table('Actual leakage-free preprocessing architecture. TRAIN $N=1{,}006{,}129$ for every learned fit; held-out partitions transform only.','tab:architecture',
          ['Location / component','Operation and fitting scope'],[
              ['Outer Pipeline: quality','Deterministic schema/finite/physical conventions; no estimated distribution parameters.'],
              ['ColumnTransformer: numeric','TRAIN median; optional target-free derivatives; optional TRAIN StandardScaler.'],
              ['ColumnTransformer: flags','TRAIN MissingIndicator(features=all); one indicator per retained physical input.'],
              ['Parallel diagnostics','Robust/MinMax Pipeline and StandardScaler--PCA Pipeline; full TRAIN fits only.'],
              ['Guard / assembly','TRAIN-only schema guard, separate nominal targets, row-aligned held-out transforms.']],spec='YY')
    for j,chunk in enumerate([decisions[:9],decisions[9:]],1):
        table('Preprocessing strategy versus reality'+(' (continued)' if j==2 else '')+'. Retention is not described as a forced deviation. Figure numbers refer to this IEEE paper.','tab:strategy'+str(j),
              ['Step','Phase 1 planned strategy','Phase 2 actual execution','Empirical justification / metric / figure'],[[esc(v) for v in row] for row in chunk],spec='YYYY',wide=True)
    captions=[
      ('missing','Missingness pattern: seed-42 uniform TRAIN display, N=5,000. Full-export conventional missingness is 0/9,616,586 cells; the 62 paired zeros remain observations.'),
      ('target',r'Target distribution: all 1,006,129 TRAIN positions, unchanged nominal class labels and natural prevalence. Normal contributes approximately 83.966\%; no resampling is applied.'),
      ('outliers','TRAIN raw versus reference-cleaned boxplots with IQR whiskers and retained observations. No statistical capping or deletion is selected; zero outside-fence flags reflect the actual full-TRAIN screen, not physical certification.'),
      ('correlation',r'TRAIN predictor-only upper-triangle Pearson correlation. Five pairs satisfy $|r|\geq0.85$; f\_nv is excluded. Warning thresholds do not automatically remove physical measurements.'),
      ('scatter','All five collinear pairs. Seed-42 uniform TRAIN scatter display N=20,000; fitted descriptive lines and Pearson values use full TRAIN. Neither lines nor association imply causal or independent samples.'),
      ('mi','Target Association / Mutual Information Feature Screening. Continuous-predictor / nominal-target MI, seed 42, proportional TRAIN sample N=50,000, k=3. This is descriptive preprocessing relevance, not trained-model feature importance.'),
      ('scaling','Original TRAIN transformation/scaling grid. StandardScaler is the reference standardized representation; Robust/MinMax are diagnostics. Original algorithm labels describe intended preprocessing rationale only. No log transform or downstream model-selection outcome is claimed.'),
      ('pca',r'Exploratory StandardScaler--PCA fitted on full TRAIN only. Bars give individual variance, line cumulative variance, dashed/dotted lines 90\%/95\% cutoffs. Two components explain 95.1677\%, requiring all six physical inputs.')]
    figures=load('Diagnostic_Inventory.json')
    add('\n\\clearpage\n')
    for x,(label,caption) in zip(figures,captions):
        add('\\begin{figure*}[!t]\n\\centering\n\\includegraphics[width=0.98\\textwidth,height=0.62\\textheight,keepaspectratio]{../../'+x['file']+'}\n\\caption{'+caption+'}\\label{fig:'+label+'}\n\\end{figure*}\n')
    add(r'''
\clearpage
\begin{thebibliography}{00}
\bibitem{dataset} C. H. Costa, ``PV Fault Dataset,'' original-author repository, commit e9ed8ad8072dcb3ffc643b0f3604219798708551. [Online]. Available: \url{https://github.com/clayton-h-costa/pv_fault_dataset}. Original source README and Apache-2.0 license retained.
\bibitem{study} A. E. Lazzaretti et al., ``A monitoring system for online fault detection and classification in photovoltaic plants,'' \emph{Sensors}, vol. 20, no. 17, art. 4688, 2020, doi: 10.3390/s20174688.
\bibitem{phase1} R. Prince, ``Data preprocessing and feature engineering strategy,'' approved Phase 1 report and original audit evidence, Oct. 2026. Retained in \texttt{phase1\_strategy/}.
\bibitem{sklearn} Scikit-learn developers, ``Pipeline, ColumnTransformer, preprocessing, mutual\_info\_classif and PCA documentation.'' [Online]. Available: \url{https://scikit-learn.org/stable/}. Exact implementation versions are pinned in the repository.
\bibitem{ieee} IEEE, ``Manuscript templates for conference proceedings.'' [Online]. Available: \url{https://www.ieee.org/conferences/publishing/templates.html}. Unmodified IEEEtran v1.8b conference class distributed with report source; template provenance recorded separately.
\end{thebibliography}
\end{document}
''')
    source=''.join(out)
    (HERE/'Assignment3_Phase2.tex').write_text(source,encoding='utf8')
    print('IEEE source and 17-item numerical decision log generated from preprocessing evidence.')

if __name__=='__main__':main()
