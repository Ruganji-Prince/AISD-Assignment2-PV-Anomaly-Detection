"""Paired Gaussian sensitivity study, gated on verified reconstructed models.

No fitting or threshold selection is implemented here. Original evidence and
predictions are read-only. New prediction metrics belong to this post-hoc study.
"""
from pathlib import Path
import sys,json,hashlib,pickle,csv
import argparse
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--work-dir',type=Path,required=True,help='Local-only workspace prepared by prepare_reconstruction_workspace.py; never committed.')
args=parser.parse_args();WORK=args.work_dir.resolve();SRC=WORK/'source'
sys.path.insert(0,str(SRC))
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from src.phase2_stage3.common import FrozenPredictor
from src.phase2_stage1.evaluation import evaluate
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save_csv(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
gate=json.loads((OUT/'Reconstruction_Verification.json').read_text());assert gate['status']=='BOTH_BEHAVIORAL_GATES_PASS'
keys=['RF__E4','LightGBM__E4'];channels=['vdc1','vdc2','idc1','idc2'];alphas=[0,.01,.02,.05,.1];seeds=[101,202,303,404,505,606,707,808,909,1010]
baseline=json.loads((WORK/'Reconstructed_Clean_Baselines.json').read_text())
models={};artifact_hash={};preprocess_hash={}
for k in keys:
    path=WORK/gate['models'][k]['artifact_relative_path'];artifact_hash[k]=sha(path);assert artifact_hash[k]==gate['models'][k]['artifact_sha256']
    with path.open('rb') as f:models[k]=pickle.load(f)
    preprocess_hash[k]=hashlib.sha256(pickle.dumps(models[k].pipeline[:-1],protocol=5)).hexdigest()
raw=SRC/'data/raw/pv_fault_dataset.csv';assert sha(raw)==gate['provenance']['raw_sha256']
frame=pd.read_csv(raw,float_precision='round_trip');frame.index=np.arange(len(frame))
train=frame.iloc[:1006129][channels];test=frame.iloc[1227337:1373798];clean=test[channels].copy();y=test.f_nv.to_numpy();assert len(y)==146461
means=train.mean().to_numpy();sd=train.std(ddof=0).to_numpy();minimum=train.min().to_numpy();maximum=train.max().to_numpy()
assert np.isfinite(train.to_numpy()).all() and (train.to_numpy()>=0).all()
scales=[{'channel':c,'unit':'V' if c.startswith('vdc') else 'A','TRAIN_N':len(train),'TRAIN_mean':means[j],'TRAIN_std_population_ddof0':sd[j],'TRAIN_min':minimum[j],'TRAIN_max':maximum[j],**{'noise_SD_'+str(int(a*100))+'pct':sd[j]*a for a in alphas[1:]}} for j,c in enumerate(channels)]
save_csv('Noise_Scale_Diagnostics.csv',scales)
print('TRAIN-DERIVED PHYSICAL SCALES',json.dumps(scales),flush=True)
rows=[];class_rows=[];alert_rows=[];ranges=[];pairs=[];confusions=[]
def collect(k,a,seed,m):
    b=baseline[k];h=m['hardware_alert_metrics'];bh=b['hardware_alert_metrics']
    row={'model':k,'alpha':a,'seed':seed,'macro_f1':m['macro_f1'],'weighted_f1':m['weighted_f1'],'macro_AP':m['macro_AP'],'hardware_macro_recall':m['hardware_macro_recall'],'coverage':m['coverage'],'abstentions':int(np.asarray(m['confusion_matrix'])[:,5].sum()),'alert_precision':h['precision'],'alert_recall':h['recall'],'alert_f1':h['f1'],'alert_AP':m['hardware_AP'],'normal_FPR':h['normal_false_alarm_rate'],'shade_FPR':h['shade_false_alarm_rate'],'combined_FPR':h['combined_nonhardware_FPR'],'alert_TP':h['TP'],'alert_FP':h['FP'],'alert_FN':h['FN'],'delta_macro_f1':b['macro_f1']-m['macro_f1'],'macro_f1_retention':m['macro_f1']/b['macro_f1'],'delta_hardware_macro_recall':b['hardware_macro_recall']-m['hardware_macro_recall'],'delta_alert_recall':bh['recall']-h['recall'],'delta_combined_FPR':h['combined_nonhardware_FPR']-bh['combined_nonhardware_FPR']}
    for c in range(5):
        pc=m['per_class'][str(c)]
        row.update({f'class{c}_{metric}':pc[metric] for metric in ['precision','recall','f1','AP']})
        class_rows.append({'model':k,'alpha':a,'seed':seed,'class':c,**pc,'delta_recall':b['per_class'][str(c)]['recall']-pc['recall'],'delta_f1':b['per_class'][str(c)]['f1']-pc['f1']})
    for c,name in [(1,'short'),(2,'degradation'),(3,'open')]:row['delta_'+name+'_recall']=b['per_class'][str(c)]['recall']-m['per_class'][str(c)]['recall']
    rows.append(row);alert_rows.append({'model':k,'alpha':a,'seed':seed,**{p:row[p] for p in ['alert_precision','alert_recall','alert_f1','alert_AP','normal_FPR','shade_FPR','combined_FPR','alert_TP','alert_FP','alert_FN','coverage','delta_alert_recall','delta_combined_FPR']}})
    confusions.append({'model':k,'alpha':a,'seed':seed,'confusion_matrix':m['confusion_matrix'],'columns':[0,1,2,3,4,'abstain']})
for k in keys:collect(k,0,0,baseline[k])
base_values=clean.to_numpy(copy=True)
def diagnose(a,seed,values):
    for j,c in enumerate(channels):
        v=values[:,j];low=int((v<minimum[j]).sum());high=int((v>maximum[j]).sum());negative=int((v<0).sum())
        ranges.append({'alpha':a,'seed':seed,'channel':c,'N':len(v),'below_TRAIN_min_count':low,'below_TRAIN_min_fraction':low/len(v),'above_TRAIN_max_count':high,'above_TRAIN_max_fraction':high/len(v),'negative_count':negative,'negative_fraction':negative/len(v),'handling':'No explicit clipping; original RetainedQuality converts negative electrical readings to missing, then frozen imputation/abstention policy applies.'})
diagnose(0,0,base_values)
with threadpool_limits(2):
 for a in alphas[1:]:
  for seed in seeds:
    # Same standard-normal draws across alpha for each seed give controlled
    # dose changes; both models receive the SAME DataFrame for each pair.
    z=np.random.default_rng(seed).standard_normal(base_values.shape)
    values=base_values+z*(a*sd);noisy=pd.DataFrame(values,index=clean.index,columns=channels)
    digest=hashlib.sha256(noisy.to_numpy().tobytes()).hexdigest();diagnose(a,seed,values)
    # Verify physical derivatives on actual frozen imputation output. This
    # invokes transforms only; manual formulas are QA, never model inputs.
    m=models['LightGBM__E4'];q=m.pipeline.named_steps['quality'].transform(noisy)
    numeric=m.pipeline.named_steps['columns'].named_transformers_['numeric'];imputed=numeric.named_steps['median'].transform(q)
    actual=numeric.named_steps['physical'].transform(imputed);v1,v2,i1,i2=imputed.T
    expected=np.column_stack([imputed,v1*i1,v2*i2,v1*i1+v2*i2,np.abs(v1-v2),np.abs(i1-i2)])
    np.testing.assert_array_equal(actual,expected)
    for k in keys:
        p=FrozenPredictor(models[k],(1227337,1373798)).predict_proba(noisy);metrics=evaluate(p,y,gate['provenance']['frozen_thresholds'][k]);collect(k,a,seed,metrics)
        assert hashlib.sha256(noisy.to_numpy().tobytes()).hexdigest()==digest
        assert hashlib.sha256(pickle.dumps(models[k].pipeline[:-1],protocol=5)).hexdigest()==preprocess_hash[k]
    pairs.append({'alpha':a,'seed':seed,'physical_input_sha256':digest,'identical_input_for_both_models':True,'derived_features_verified':True})
    save_csv('Noise_Robustness_Seed_Level.csv',rows)
    print('PAIRED',a,seed,[(r['model'],round(r['macro_f1'],6),round(r['alert_recall'],6),round(r['combined_FPR'],6),r['abstentions']) for r in rows[-2:]],flush=True)
save_csv('Noise_Robustness_Class_Metrics.csv',class_rows);save_csv('Noise_Robustness_Alert_Metrics.csv',alert_rows);save_csv('Noise_Range_Diagnostics_Seed_Level.csv',ranges);save_csv('Noise_Paired_Input_Verification.csv',pairs)
df=pd.DataFrame(rows);summary=[]
for (k,a),group in df.groupby(['model','alpha'],sort=False):
    r={'model':k,'alpha':a,'repetitions':len(group)}
    for field in df.columns:
        if field in ['model','alpha','seed']:continue
        r[field+'_mean']=float(group[field].mean());r[field+'_std']=float(group[field].std(ddof=1)) if len(group)>1 else 0.
    summary.append(r)
save_csv('Noise_Robustness_Summary.csv',summary)
rg=pd.DataFrame(ranges);rs=[]
for (a,c),group in rg.groupby(['alpha','channel'],sort=False):
    r={'alpha':a,'channel':c,'repetitions':len(group),'N_per_repeat':146461}
    for field in ['below_TRAIN_min_count','below_TRAIN_min_fraction','above_TRAIN_max_count','above_TRAIN_max_fraction','negative_count','negative_fraction']:
        r[field+'_mean']=float(group[field].mean());r[field+'_std']=float(group[field].std(ddof=1)) if len(group)>1 else 0.
    rs.append(r)
save_csv('Noise_Range_Diagnostics.csv',rs)
(OUT/'Noise_Confusion_Counts.json').write_text(json.dumps(confusions,indent=2),encoding='utf8')
for k in keys:assert sha(WORK/gate['models'][k]['artifact_relative_path'])==artifact_hash[k]
protected=json.loads((WORK/'Protected_Original_Files.json').read_text());assert all(sha(ROOT/n)==h for n,h in protected.items())
verification={'title':'Additional Post-Hoc Noise Robustness Analysis using behaviorally verified reconstructed models','source_commit':gate['provenance']['source_commit'],'reconstruction_gate':{k:gate['models'][k]['classification'] for k in keys},'test_sample_count':146461,'reconstructed_model_hashes':artifact_hash,'historical_expected_hashes':gate['provenance']['original_historical_hashes'],'binary_identity':'NOT ESTABLISHED','preprocessing_provenance':'Unchanged source-commit build_preprocessor and AblationModel.fit; TRAIN-only reconstruction, frozen transforms during noise analysis.','preprocessing_state_sha256':preprocess_hash,'frozen_thresholds':gate['provenance']['frozen_thresholds'],'physical_channels':channels,'training_scales':scales,'std_definition':'Population SD ddof=0 of raw physical TRAIN channels; those TRAIN E4 readings are finite and nonnegative.','noise_equation':'x_noisy = x + N(0, (alpha * sigma_TRAIN)^2)','alpha_levels':alphas,'seeds':seeds,'repetitions_per_nonzero_level':10,'clean_repetitions':1,'noise_clipped':False,'existing_quality_policy_applied':'Negative electrical readings converted to missing; frozen medians and existing availability/abstention logic retained.','paired_inputs':pairs,'prediction_rows':len(rows),'clean_baseline_comparison_file':'Reconstruction_Baseline_Comparison.csv','models_fitted_for_reconstruction':True,'models_refitted_during_noise':False,'preprocessing_fitted_on_TRAIN_during_reconstruction':True,'preprocessing_refitted_on_TEST_or_noisy_inputs':False,'thresholds_changed':False,'new_predictions_generated_for_reconstructed_clean_baseline_and_noisy_inputs':True,'original_clean_predictions_replaced':False,'historical_evidence_modified':False,'protected_existing_files_verified':len(protected),'std_across_repeats':'Sample SD ddof=1; alpha=0 has n=1 and std=0 by convention, not estimated uncertainty.','interpretation':'Synthetic noise seed variation is not independent-dataset sampling uncertainty. The original engineering conclusion remains unchanged.','files_created':[p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file() and p.name not in ['Noise_Robustness_Analysis.md','Noise_Robustness_Verification.json','Artifact_Recovery_Report.md','Artifact_Recovery_Search.json']],'existing_files_modified':[],'committed':False,'pushed':False}
(OUT/'Noise_Robustness_Reconstructed_Verification.json').write_text(json.dumps(verification,indent=2),encoding='utf8')
print('NOISE STUDY COMPLETE: 40 paired noisy inputs, 80 noisy model evaluations, originals unchanged.',flush=True)
