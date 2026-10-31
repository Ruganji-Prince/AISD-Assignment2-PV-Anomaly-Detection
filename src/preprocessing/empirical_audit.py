"""TRAIN-only descriptive evidence and measured preprocessing-stage dimensions.

No predictive estimator, target-performance metric or downstream cache is used.
"""
import numpy as np
import pandas as pd
from .common import ROOT, OUT, SENSORS, write, digest
from src.pipeline_builder import POLICIES


def empirical_audit(study):
    train = study.partitions['TRAIN']
    reference = pd.read_csv(ROOT/'phase1_strategy/Training_Distributions.csv').set_index('sensor')
    records = []
    for sensor in SENSORS:
        x = train[sensor]
        q1, q3 = x.quantile([.25, .75])
        iqr = q3-q1
        lower, upper = q1-1.5*iqr, q3+1.5*iqr
        count = int(((x < lower) | (x > upper)).sum())
        record = dict(sensor=sensor, N=len(x), mean=float(x.mean()), median=float(x.median()),
                      std_ddof0=float(x.std(ddof=0)), std_ddof1=float(x.std()), minimum=float(x.min()), maximum=float(x.max()),
                      q1=float(q1), q3=float(q3), IQR=float(iqr), lower_fence=float(lower),
                      upper_fence=float(upper), flagged_count=count, flagged_pct=100*count/len(x),
                      skewness=float(x.skew()), excess_kurtosis=float(x.kurt()),
                      z_gt_3_count=int((((x-x.mean())/x.std(ddof=0)).abs()>3).sum()))
        old = reference.loc[sensor]
        for new, previous in [('mean','mean'),('median','median'),('std_ddof0','std'),
                              ('q1','q1'),('q3','q3'),('lower_fence','iqr_lower'),
                              ('upper_fence','iqr_upper'),('skewness','skewness')]:
            assert np.isclose(record[new], old[previous], rtol=0, atol=1e-10), (sensor,new)
        assert count == old.iqr_flagged_count and record['z_gt_3_count'] == old.z_gt_3_count
        records.append(record)
    distributions = pd.DataFrame(records)

    # Correlation-matrix inverse equals centered OLS VIF (with intercept).
    corr = train[SENSORS].corr().to_numpy()
    vif = dict(zip(SENSORS, np.diag(np.linalg.inv(corr)).tolist()))
    import json
    old_vif = json.loads((ROOT/'phase1_strategy/primary_audit.json').read_text())['training_vif']
    assert np.allclose(list(vif.values()), list(old_vif.values()), rtol=0, atol=1e-8)

    dimensions = []
    for policy, pre in study.preprocessors.items():
        channels = study.stats['model_ready'][policy]['raw_channels']
        cols = pre.named_steps['columns']
        numeric = cols.named_transformers_['numeric']
        for partition, frame in study.partitions.items():
            quality = pre.named_steps['quality'].transform(frame[channels])
            median = numeric.named_steps['median'].transform(quality)
            flags = cols.named_transformers_['missing'].transform(quality)
            engineered = numeric.named_steps['physical'].transform(median) if 'physical' in numeric.named_steps else median
            scaled = numeric.named_steps['scale'].transform(engineered) if 'scale' in numeric.named_steps else engineered
            combined = np.column_stack([scaled, flags])
            assert np.array_equal(combined, study.matrices[policy][partition])
            assert quality.shape == median.shape == (len(frame),len(channels))
            dimensions.append(dict(policy=policy, partition=partition, input_N=len(frame),
                                   original_predictors=6, retained_physical_channels=len(channels),
                                   post_quality_P=quality.shape[1], post_median_numeric_P=median.shape[1],
                                   indicator_P=flags.shape[1], post_imputation_plus_indicators_P=median.shape[1]+flags.shape[1],
                                   post_feature_numeric_P=engineered.shape[1], post_scaling_numeric_P=scaled.shape[1],
                                   final_design_P=combined.shape[1], post_feature_plus_indicators_P=combined.shape[1],
                                   PCA_diagnostic_input_P=6 if policy=='six_standard' else None,
                                   PCA_diagnostic_all_components_P=6 if policy=='six_standard' else None,
                                   PCA_95pct_view_P=2 if policy=='six_standard' else None,
                                   input_predictor_NxP=f'{len(frame)} x 6',
                                   post_quality_NxP=f'{quality.shape[0]} x {quality.shape[1]}',
                                   post_imputation_indicators_NxP=f'{len(frame)} x {median.shape[1]+flags.shape[1]}',
                                   post_feature_numeric_NxP=f'{engineered.shape[0]} x {engineered.shape[1]}',
                                   post_scaling_numeric_NxP=f'{scaled.shape[0]} x {scaled.shape[1]}',
                                   final_design_NxP=f'{combined.shape[0]} x {combined.shape[1]}'))
    dimensions = pd.DataFrame(dimensions)

    scale_rows = []
    for j,sensor in enumerate(SENSORS):
        raw = train[sensor].to_numpy()
        # Fit is already complete on TRAIN. These operations are transforms only.
        for name, array in [('raw',raw),('standard',study.standardized[:,j]),
                            ('robust',study.robust.transform(study.training_numeric)[:,j]),
                            ('minmax',study.minmax.transform(study.training_numeric)[:,j])]:
            series = pd.Series(array)
            scale_rows.append(dict(sensor=sensor, representation=name, mean=float(series.mean()),
                                   std_ddof0=float(series.std(ddof=0)), median=float(series.median()),
                                   q1=float(series.quantile(.25)),q3=float(series.quantile(.75)),
                                   minimum=float(series.min()),maximum=float(series.max()),skewness=float(series.skew())))
    scaling = pd.DataFrame(scale_rows)
    standardized = scaling[scaling.representation=='standard']
    assert np.allclose(standardized['mean'],0,atol=1e-10)
    assert np.allclose(standardized.std_ddof0,1,atol=1e-10)
    # The standardized input is TRAIN-only; independently verify PCA eigenvalues.
    eigenvalues = np.linalg.eigvalsh(np.cov(study.standardized,rowvar=False))[::-1]
    assert np.allclose(eigenvalues,study.pca.explained_variance_,rtol=0,atol=1e-10)
    pca = pd.DataFrame(dict(component=np.arange(1,7),eigenvalue=study.pca.explained_variance_,
                            explained_variance_ratio=study.pca.explained_variance_ratio_,
                            cumulative_explained_variance=np.cumsum(study.pca.explained_variance_ratio_)))
    # A held-out frame must be rejected before the preprocessing factory can fit.
    from .study import fit_training_preprocessor
    from unittest.mock import patch
    with patch('src.preprocessing.study.build_preprocessor',side_effect=AssertionError('Held-out fit attempted')) as factory:
        try:
            fit_training_preprocessor(study.partitions['VALIDATION'][SENSORS],'standard','F6')
        except ValueError:
            pass
        else:
            raise AssertionError('Held-out fitting was accepted')
        factory.assert_not_called()
    audit = dict(population='TRAIN',N=len(train),index_digest=digest(train.index),
                 raw_negative_irradiance=dict(count=int((study.raw.irr<0).sum()),
                                              minimum=float(study.raw.irr.min()),
                                              maximum=float(study.raw.loc[study.raw.irr<0,'irr'].max())),
                 verified_VIF=vif,VIF_method='Diagonal of inverse centered TRAIN Pearson correlation; agrees with original intercept-OLS VIF',
                 kurtosis_definition='Unbiased Fisher excess kurtosis; pandas Series.kurt',
                 IQR_rule='Q1 - 1.5 IQR; Q3 + 1.5 IQR; strict outside comparison',
                 standard_std_definition='population standard deviation, ddof=0',
                 heldout_fit_guard_passed=True,all_final_matrices_match_original=True,
                 selected_preprocessing_policy='six_standard, all six measured predictors; no physical-channel reduction selected',
                 other_policies='electrical_native and electrical_derived are existing alternative representations, not selected sensor adequacy results',
                 PCA_role='Exploratory only; six components available, two-component 95% view is not a selected pipeline or physical sensor reduction',
                 diagnostic_scalers_and_PCA_encapsulated=True)
    OUT.mkdir(parents=True,exist_ok=True)
    for name, frame in [('Training_Distribution_Diagnostics.csv',distributions),
                         ('Pipeline_Stage_Dimensions.csv',dimensions),('Scaling_Diagnostics.csv',scaling),('PCA_Diagnostics.csv',pca)]:
        frame.to_csv(OUT/name,index=False)
    write(OUT/'Empirical_Audit.json',audit)
    return dimensions, distributions, scaling, pca
