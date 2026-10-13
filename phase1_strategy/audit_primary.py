"""Reproducible Phase 1 evidence audit; never writes cleaned data or fits an ML model.

Source order is retained as an acquisition-index proxy, not reconstructed time.
Statistics affecting preprocessing proposals use only the proposed training prefix.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import importlib.metadata

import numpy as np
import pandas as pd
from scipy.io import loadmat, whosmat
from scipy.stats import pointbiserialr

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/candidate_evidence'
OUT = ROOT / 'phase1_strategy'
SENSORS = ['vdc1', 'vdc2', 'idc1', 'idc2', 'irr', 'pvt']
LABELS = {0:'Normal', 1:'Short circuit', 2:'Resistive degradation', 3:'Open circuit', 4:'Building shade'}
INFO = {
    'vdc1': ('String 1 DC RMS voltage', 'V'),
    'vdc2': ('String 2 DC RMS voltage', 'V'),
    'idc1': ('String 1 DC RMS current', 'A'),
    'idc2': ('String 2 DC RMS current', 'A'),
    'irr': ('Reported one-second average plane-of-array irradiance', 'W/m^2'),
    'pvt': ('Reported one-second average of aggregate module temperature', 'deg C'),
    'f_nv': ('Experimental operating-state annotation', 'unitless'),
}
EXPECTED_HASHES = {
    'amb':'e4619812a5b6c1331332248f052cb09938f9a43ccac8bcc512796c6e906da7e0',
    'elec':'c04ed3fcc0e338703e87d387b1ce6ef51da1848e77b4d491e62afe08934ce494',
}

def runs(mask: np.ndarray) -> list[dict]:
    """Return maximal true runs as zero-based, end-exclusive index intervals."""
    changes = np.diff(np.r_[False,mask,False].astype(np.int8))
    return [{'start':int(a),'end_exclusive':int(b),'length':int(b-a)}
            for a,b in zip(np.flatnonzero(changes==1),np.flatnonzero(changes==-1))]

def class_counts(y: np.ndarray) -> dict[str,int]:
    return {str(k):int(np.count_nonzero(y==k)) for k in LABELS}

def partition(y: np.ndarray,start: int,end: int) -> dict:
    return {'start':start,'end_exclusive':end,'N':end-start,'labels':class_counts(y[start:end])}

def vif(frame: pd.DataFrame) -> dict[str,float]:
    """VIF from standardized predictor regression with an intercept; audit only."""
    z = (frame.to_numpy()-frame.mean().to_numpy())/frame.std(ddof=0).to_numpy()
    result = {}
    for i,name in enumerate(frame.columns):
        other = np.column_stack([np.ones(len(z)),np.delete(z,i,axis=1)])
        coef = np.linalg.lstsq(other,z[:,i],rcond=None)[0]
        residual = z[:,i]-other@coef
        one_minus_r2 = float((residual@residual)/(z[:,i]@z[:,i]))
        result[name] = float(1/max(one_minus_r2,1e-15))
    return result

def main() -> None:
    OUT.mkdir(exist_ok=True)
    arrays,files,stored_types = {},[],{}
    for kind in ('amb','elec'):
        path = RAW/f'clayton-h-costa_dataset_{kind}.mat'
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED_HASHES[kind]:
            raise ValueError(f'Source content changed: {path.name}. Review before auditing.')
        header = whosmat(path)
        files.append({'name':path.name,'bytes':path.stat().st_size,'sha256':digest,'variables':header})
        stored_types.update({name:typ for name,_,typ in header})
        arrays.update({k:np.asarray(v).ravel() for k,v in loadmat(path).items() if not k.startswith('__')})
    assert set(arrays)==set(SENSORS+['f_nv'])
    assert len({len(v) for v in arrays.values()})==1
    frame = pd.DataFrame({k:arrays[k] for k in SENSORS+['f_nv']})
    y = frame.f_nv.to_numpy()
    n = len(frame)
    assert set(np.unique(y))==set(LABELS)
    # Label-free separators from observed irradiance, not inferred dates.
    # The paper identifies 100 W/m^2 as the inverter-start region. Requiring
    # 3,600 consecutive source positions suppresses brief clouds/dropout zeros.
    # Neither threshold is evidence that a block is a verified measurement day.
    low_light_separators = [r for r in runs(frame.irr.lt(100).to_numpy()) if r['length']>=3600]
    operating_blocks = [{'block':i+1,'start':left['end_exclusive'],'end_exclusive':right['start'],
                         'N':right['start']-left['end_exclusive']}
                        for i,(left,right) in enumerate(zip(low_light_separators[:-1],low_light_separators[1:]))]
    assert len(operating_blocks)==16, 'Source grouping changed; review split strategy.'
    first,second = low_light_separators[12],low_light_separators[14]
    splits = {'training':partition(y,0,first['start']),
              'validation':partition(y,first['end_exclusive'],second['start']),
              'test':partition(y,second['end_exclusive'],n)}
    validation_blocks = {'model_selection':partition(y,operating_blocks[12]['start'],operating_blocks[12]['end_exclusive']),
                         'alert_threshold':partition(y,operating_blocks[13]['start'],operating_blocks[13]['end_exclusive'])}
    train = frame.iloc[:splits['training']['end_exclusive']]
    inventory = []
    for name in frame:
        col = frame[name]
        meaning,unit = INFO[name]
        is_target = name=='f_nv'
        entry = {'name':name,'meaning':meaning,'unit':unit,'mat_header_class':stored_types[name],
                 'loaded_dtype':str(col.dtype),'analytical_category':'Nominal categorical' if is_target else 'Continuous',
                 'role':'target' if is_target else 'predictor','missing_count':int(col.isna().sum()),
                 'missing_pct':float(col.isna().mean()*100),'unique':int(col.nunique())}
        entry['potential_leakage']='Target itself: exclude from all predictors.' if is_target else 'No target-derived content documented; shared conditions and source alignment remain risks.'
        if is_target:
            entry.update(treatment='Preserve five nominal codes; never scale, impute or use as a predictor.',
                         justification='Codes identify unordered experimental operating states; mapping is not severity.')
        else:
            entry.update(treatment='Retain; quality flags; training-only median fallback if needed; scaler depends on model.',
                         justification='Measurements support physical interpretation and sensor ablation; no automatic correlation deletion.')
            entry.update(raw_min=float(col.min()),raw_max=float(col.max()),raw_mean=float(col.mean()),
                         raw_median=float(col.median()),raw_skewness=float(col.skew()),
                         negative_count=int(col.lt(0).sum()),zero_count=int(col.eq(0).sum()))
            if name=='irr':
                entry['treatment']='Retain; proposed flagged clamp for -1<=irr<0; suspected joint-zero annotation; training-only fallback/scaling if needed.'
                entry['justification']='One -0.0381 reading; zero generation can be valid; irradiance helps distinguish environment from equipment change.'
            elif name=='pvt':
                entry['treatment']='Retain negative temperatures; annotate suspected joint-zero events; no raw log; training-only fallback/scaling if needed.'
                entry['justification']='Subzero readings are plausible; aggregate of four source probes is one exported feature, not one physical sensing point.'
        inventory.append(entry)
    pd.DataFrame(inventory).to_csv(OUT/'Variable_Inventory.csv',index=False)
    counts = pd.DataFrame([{'label':k,'meaning':v,'N':int((y==k).sum()),'pct':float((y==k).mean()*100)} for k,v in LABELS.items()])
    counts.to_csv(OUT/'Class_Distribution.csv',index=False)
    corr = train[SENSORS].corr()
    corr.to_csv(OUT/'Training_Correlation.csv')
    flagged_pairs = [{'a':a,'b':b,'pearson_r':float(corr.loc[a,b])} for i,a in enumerate(SENSORS)
                     for b in SENSORS[i+1:] if abs(corr.loc[a,b])>=.85]
    # Distributions and fences are train-prefix diagnostics, not caps applied to data.
    stats = []
    for name in SENSORS:
        col = train[name]
        q1,q3 = col.quantile([.25,.75]); lower,upper=q1-1.5*(q3-q1),q3+1.5*(q3-q1)
        z = (col-col.mean())/col.std(ddof=0)
        flags = (col<lower)|(col>upper)
        entry = {'sensor':name,'mean':float(col.mean()),'median':float(col.median()),'std':float(col.std(ddof=0)),
                 'skewness':float(col.skew()),'q1':float(q1),'q3':float(q3),'iqr_lower':float(lower),'iqr_upper':float(upper),
                 'iqr_flagged_count':int(flags.sum()),'iqr_flagged_pct':float(flags.mean()*100),
                 'z_gt_3_count':int(z.abs().gt(3).sum()),'flags_by_label':class_counts(train.f_nv.to_numpy()[flags.to_numpy()])}
        stats.append(entry)
    pd.DataFrame([{k:v for k,v in row.items() if k!='flags_by_label'} for row in stats]).to_csv(OUT/'Training_Distributions.csv',index=False)
    pairedzero = (frame.irr==0)&(frame.pvt==0)
    zero_runs = runs(pairedzero.to_numpy())
    label_change = np.r_[True,y[1:]!=y[:-1]]
    starts=np.flatnonzero(label_change); ends=np.r_[starts[1:],n]
    episodes=[{'start':int(a),'end_exclusive':int(b),'length':int(b-a),'label':int(y[a])} for a,b in zip(starts,ends)]
    pd.DataFrame(episodes).to_csv(OUT/'Label_Runs.csv',index=False)
    equipment = [e for e in episodes if e['label'] in (1,2,3)]
    # This flags exact run crossing only; it does not certify day/session independence.
    boundaries = [first['start'],first['end_exclusive'],second['start'],second['end_exclusive']]
    crossing = [e for e in equipment if any(e['start']<b<e['end_exclusive'] for b in boundaries)]
    missing = frame.isna().to_numpy()
    window_profiles=[]
    for start in range(0,n,100000):
        end=min(start+100000,n); block=frame.iloc[start:end]
        active_normal=block[(block.f_nv==0)&(block.irr>=100)]
        window_profiles.append({'start':start,'end_exclusive':end,'N':len(block),'missing_cells':int(block.isna().sum().sum()),
                                'labels':class_counts(block.f_nv.to_numpy()),'active_normal_N':len(active_normal),
                                'active_normal_medians':{c:None if active_normal.empty else float(active_normal[c].median()) for c in SENSORS}})
    lag_corr = {sensor:{str(lag):float(train[sensor].iloc[:-lag].corr(train[sensor].shift(-lag).iloc[:-lag]))
                        for lag in (1,10,100,600,3600)} for sensor in SENSORS}
    relevance = {sensor:{str(label):float(pointbiserialr(train.f_nv.eq(label).to_numpy(),train[sensor].to_numpy()).statistic)
                         for label in LABELS} for sensor in SENSORS}
    metadata = json.loads((OUT/'source_metadata.json').read_text())
    result = {'audit_date':'2026-10-12','python':platform.python_version(),
              'packages':{p:importlib.metadata.version(p) for p in ('numpy','pandas','scipy','pymupdf','reportlab')},
              'source_commit':metadata['clayton-h-costa']['commit'],'files':files,
              'raw_N':n,'raw_total_columns':7,'raw_predictors':6,'raw_cells':int(frame.size),
              'raw_missing_cells':int(missing.sum()),'raw_missing_pct':float(missing.mean()*100),
              'raw_complete_rows':int((~missing.any(axis=1)).sum()),'raw_incomplete_rows':int(missing.any(axis=1).sum()),
              'raw_duplicate_rows':int(frame.duplicated().sum()),'raw_infinite_cells':int(np.isinf(frame.to_numpy()).sum()),
              'missing_runs_by_sensor':{c:runs(frame[c].isna().to_numpy()) for c in SENSORS},
              'class_counts':class_counts(y),'normal_to_smallest_class_ratio':float((y==0).sum()/(y==1).sum()),
              'paired_zero_rows':int(pairedzero.sum()),'paired_zero_runs':zero_runs,
              'negative_irradiance_rows':np.flatnonzero(frame.irr.lt(0).to_numpy()).tolist(),
              'inventory':inventory,'proposed_split':splits,
              'group_rule':{'irradiance_below':100,'min_consecutive_positions':3600,'allocation_blocks':[12,2,2]},
              'low_light_separators':low_light_separators,'operating_blocks':operating_blocks,
              'excluded_separator_rows':n-sum(x['N'] for x in splits.values()),
              'excluded_separator_intervals':[first,second],'validation_subblocks':validation_blocks,
              'retained_row_split_pct':{key:float(value['N']/sum(p['N'] for p in splits.values())*100) for key,value in splits.items()},
              'equipment_label_runs_crossing_base_boundaries':crossing,'equipment_label_run_count':len(equipment),
              'training_statistics':stats,'training_correlated_pairs':flagged_pairs,'training_vif':vif(train[SENSORS]),
              'training_lag_index_correlations':lag_corr,'training_point_biserial_ovr_effects':relevance,
              'acquisition_index_profiles':window_profiles,
              'temporal_status':'No timestamp/day/session metadata. Operating blocks and separator buffers are signal-based index proxies, not recovered time.'}
    (OUT/'primary_audit.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    split_manifest = {key:result[key] for key in ['source_commit','raw_N','raw_total_columns','raw_predictors',
                      'group_rule','operating_blocks','proposed_split','excluded_separator_intervals',
                      'excluded_separator_rows','validation_subblocks','retained_row_split_pct','temporal_status']}
    split_manifest['status']='Phase 1 planned evaluation manifest; no processed dataset or classifier has been generated.'
    split_manifest['target']='f_nv five-class nominal operating state; equipment probabilities summed for 1,2,3'
    split_manifest['predictors']=SENSORS
    split_manifest['source_sha256']={r['name']:r['sha256'] for r in files}
    (OUT/'Phase1_Split_Manifest.json').write_text(json.dumps(split_manifest,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['raw_N','raw_total_columns','raw_missing_cells','paired_zero_rows','proposed_split','training_correlated_pairs','training_vif']},indent=2))

if __name__=='__main__':
    main()
