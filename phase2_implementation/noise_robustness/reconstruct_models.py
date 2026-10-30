"""Controlled reconstruction: frozen preprocessing and fit methods, isolated outputs.

No original model cache is loaded or manufactured. This script must run in the
recorded environment, after preparing the exact-commit local source snapshot.
"""
from pathlib import Path
import sys,json,hashlib,pickle,time,csv,platform,importlib.metadata
import argparse
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--work-dir',type=Path,required=True,help='Local-only workspace prepared by prepare_reconstruction_workspace.py; never committed.')
args=parser.parse_args();WORK=args.work_dir.resolve();SRC=WORK/'source'
sys.path.insert(0,str(SRC))
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from lightgbm import LGBMClassifier
from threadpoolctl import threadpool_limits,threadpool_info
from src.phase2_stage2.models import AblationModel,build_preprocessor
from src.phase2_stage2.contracts import frozen_weights
from src.phase2_stage3.common import FrozenPredictor
from src.phase2_stage1.evaluation import evaluate
from src.phase2_stage1.contracts import TRAIN_COUNTS,BLOCK13_COUNTS,index_digest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(rel):return json.loads((SRC/rel).read_text(encoding='utf8'))
def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf8')
versions={'numpy':'2.5.4','pandas':'3.0.6','scipy':'1.18.1','scikit-learn':'1.9.1','lightgbm':'4.7.0','joblib':'1.6.0','threadpoolctl':'3.7.0','psutil':'7.2.2','python-dateutil':'3.0.0','six':'1.17.0','tzdata':'2026.5','narwhals':'2.27.1','cloudpickle':'3.1.2'}
assert platform.python_version()=='3.14.7'
for k,v in versions.items():assert importlib.metadata.version(k)==v,(k,importlib.metadata.version(k),v)
snapshot=json.loads((WORK/'Source_Snapshot.json').read_text())
for rel,h in snapshot['source_sha256'].items():assert sha(SRC/rel)==h,rel
raw=SRC/'data/raw/pv_fault_dataset.csv';assert sha(raw)==snapshot['raw_sha256']
spec=load('phase2_implementation/stage4/evidence/final_model_specifications.json')['candidates']
historical=load('phase2_implementation/stage3/evidence/final_test_details.json')['results']
thresholds=load('phase2_implementation/stage3/evidence/stage3_threshold_selection.json')['results']
manifest=load('phase1_strategy/Phase1_Split_Manifest.json')
channels=['vdc1','vdc2','idc1','idc2'];keys=['RF__E4','LightGBM__E4']
frame=pd.read_csv(raw,float_precision='round_trip');frame.index=np.arange(len(frame))
assert len(frame)==1373798 and list(frame)==channels+['irr','pvt','f_nv']
bounds={'TRAIN':(0,1006129),'VALIDATION':(1056990,1173967),'block13':(1056990,1089790),'block14':(1140571,1173967),'TEST':(1227337,1373798)}
counts={n:{str(k):int(v) for k,v in frame.iloc[a:b].f_nv.value_counts().sort_index().items()} for n,(a,b) in bounds.items()}
assert {int(k):v for k,v in counts['TRAIN'].items()}==TRAIN_COUNTS
assert {int(k):v for k,v in counts['block13'].items()}==BLOCK13_COUNTS
assert list(counts['TEST'].values())==[124512,2361,2270,2410,14908]
assert sum(counts['TEST'].values())==146461
train=frame.iloc[slice(*bounds['TRAIN'])];test=frame.iloc[slice(*bounds['TEST'])]
weights=frozen_weights();assert all(abs(weights[k]-len(train)/(5*TRAIN_COUNTS[k]))<1e-14 for k in TRAIN_COUNTS)
provenance={'title':'Controlled reconstruction study; not original fitted artifacts','source_commit':snapshot['commit'],'python':sys.version,'platform':platform.platform(),'dependencies':versions,'partition_bounds':bounds,'class_counts':counts,'raw_sha256':sha(raw),'physical_channels':channels,'seed':42,'threads':2,'original_historical_hashes':{k:spec[k]['model_sha256'] for k in keys},'frozen_thresholds':{k:thresholds[k]['threshold'] for k in keys},'parameters':{k:spec[k]['estimator_parameters'] for k in keys},'constructor_adaptation':'Missing Stage1-cache clone replaced with clone(estimator(**full frozen parameters)); original Stage2 build_preprocessor and AblationModel.fit reused unchanged. No selection or F6 training. New object attributes mirror the original constructor.','fit_scope':'TRAIN only; no validation/TEST fitting','binary_identity':'NOT ESTABLISHED','fit_started_at_provenance_recording':False,'source_files':snapshot['source_sha256']}
write(OUT/'Reconstruction_Verification.json',{'status':'PROVENANCE_VERIFIED_BEFORE_FITTING','provenance':provenance})
(OUT/'Reconstruction_Provenance.md').write_text('# Controlled Reconstruction Study\n\nModels are reconstructed RF E4 and reconstructed LightGBM E4, never recovered originals.\n\nSource commit: `'+snapshot['commit']+'`. Exact recorded Python and model dependencies verified before fitting. Immutable raw CSV and TRAIN/VALIDATION/TEST counts verified. Full parameters, partition bounds, class weights and dependency versions are in `Reconstruction_Verification.json`.\n\nThe original Stage 2 constructor depends on a missing Stage 1 estimator cache. The reconstruction explicitly replaces that cache-cloning step with an unfitted estimator constructed from the complete frozen parameter projection, then clones it. It uses the unchanged original `build_preprocessor` factory and `AblationModel.fit` method. No original source is edited; no F6 selection or threshold selection is rerun. This adaptation is recorded, rather than treating a new model as an original binary.\n\nThe original fit method restricts fitting to all 1,006,129 TRAIN rows and verifies label counts, estimator parameters and feature dimension. FrozenPredictor is used for authorized clean TEST prediction. All newly fitted models and prediction arrays are isolated under the local-only reconstruction workspace.\n\nExact confusion-count agreement is the primary clean reproduction check. Aggregate confusion counts cannot establish the actual number of per-observation changed predictions when historical row-level predictions are unavailable; half the confusion L1 difference is only a lower bound on necessary changed classifications. A zero bound does not prove identical row-level predictions.\n\nBinary identity with the lost originals is NOT ESTABLISHED, irrespective of behavioral classification. The existing artifact-gate and recovery records are preserved.\n',encoding='utf8')
print('PROVENANCE VERIFIED; fitting authorized reconstructed models',flush=True)
models=WORK/'models';models.mkdir(exist_ok=True)
baselines={};verifications={};comparison=[]
def flatten(d,prefix=''):
    out={}
    for k,v in d.items():
        name=prefix+'.'+k if prefix else k
        if isinstance(v,dict):out.update(flatten(v,name))
        elif isinstance(v,(int,float)) and not isinstance(v,bool):out[name]=v
    return out
with threadpool_limits(2):
 for key in keys:
    family=key.split('__')[0];s=spec[key];params=dict(s['estimator_parameters']);params['class_weight']={int(k):v for k,v in params['class_weight'].items()}
    assert params['class_weight']==weights
    path=models/(key+'_reconstructed.pkl');assert not path.exists(),'Do not silently overwrite a reconstructed model'
    estimator=clone((RandomForestClassifier if family=='RF' else LGBMClassifier)(**params))
    m=AblationModel.__new__(AblationModel);m.family=family;m.config='E4';m.channels=channels.copy();m.feature_policy='engineered' if family=='LightGBM' else 'raw'
    m.frozen_estimator_params=estimator.get_params();assert m.frozen_estimator_params==params
    m.pipeline=Pipeline(build_preprocessor(family,m.channels).steps+[('model',estimator)])
    m.boundaries=tuple(sorted({v for b in manifest['operating_blocks'] for v in [b['start'],b['end_exclusive']]}))
    print('FIT START',key,flush=True);t=time.perf_counter();m.fit(train[channels],train.f_nv.to_numpy());fit_seconds=time.perf_counter()-t
    assert m.names()==s['feature_names'];assert m.fit_index_digest_==s['fit_index_digest']
    med=m.pipeline.named_steps['columns'].named_transformers_['numeric'].named_steps['median'].statistics_
    expected_med=s.get('training_medians',s.get('medians'))
    if expected_med is not None:np.testing.assert_array_equal(med,expected_med)
    path.write_bytes(pickle.dumps(m,protocol=5));h=sha(path)
    print('FIT COMPLETE',key,fit_seconds,'seconds; clean TEST gate',flush=True)
    p=FrozenPredictor(m,bounds['TEST']).predict_proba(test[channels]);r=evaluate(p,test.f_nv.to_numpy(),thresholds[key]['threshold']);r['hardware_alert_metrics']['average_precision']=r['hardware_AP']
    np.savez_compressed(WORK/(key+'_reconstructed_clean.npz'),p=p,y=test.f_nv.to_numpy(),index=test.index.to_numpy())
    baselines[key]=r;old=historical[key];cm=np.asarray(r['confusion_matrix']);oldcm=np.asarray(old['confusion_matrix']);delta=cm-oldcm
    for true_class in range(5):
        for predicted_class in range(6):
            comparison.append({'model':key,'metric':f'confusion.true{true_class}.pred{predicted_class if predicted_class<5 else "abstain"}','historical':int(oldcm[true_class,predicted_class]),'reconstructed':int(cm[true_class,predicted_class]),'difference':int(delta[true_class,predicted_class])})
    for field,value in flatten(r).items():
        if field in flatten(old):comparison.append({'model':key,'metric':field,'historical':flatten(old)[field],'reconstructed':value,'difference':value-flatten(old)[field]})
    diffs={field:float(value-flatten(old)[field]) for field,value in flatten(r).items() if field in flatten(old)}
    exact=bool(np.array_equal(cm,oldcm) and all(abs(v)<=1e-12 for v in diffs.values()))
    # Discrete changes to major confusion destinations are conservatively a failure.
    major_preserved=all(np.argsort(-oldcm[c,:5])[0]==np.argsort(-cm[c,:5])[0] for c in range(5))
    near=abs(r['macro_f1']-old['macro_f1'])<=.002 and all(abs(r['per_class'][str(c)]['recall']-old['per_class'][str(c)]['recall'])<=.002 and (r['per_class'][str(c)]['recall']>=.9)==(old['per_class'][str(c)]['recall']>=.9) for c in [1,2,3]) and abs(r['hardware_alert_metrics']['recall']-old['hardware_alert_metrics']['recall'])<=.002 and abs(r['hardware_alert_metrics']['combined_nonhardware_FPR']-old['hardware_alert_metrics']['combined_nonhardware_FPR'])<=.0002 and major_preserved
    kind='A' if exact else ('B' if near else 'C')
    if key=='LightGBM__E4' and abs(r['per_class']['1']['recall']-old['per_class']['1']['recall'])>.002:kind='C'
    verifications[key]={'name':'reconstructed '+family+' E4','reconstructed':True,'artifact_relative_path':path.relative_to(WORK).as_posix(),'artifact_sha256':h,'historical_expected_sha256':s['model_sha256'],'binary_identity':'NOT ESTABLISHED','fit_seconds':fit_seconds,'training_rows':len(train),'fit_index_digest':m.fit_index_digest_,'training_medians':med.tolist(),'maximum_absolute_confusion_cell_difference':int(abs(delta).max()),'confusion_L1_difference':int(abs(delta).sum()),'minimum_changed_classifications_lower_bound':int(abs(delta).sum()//2),'actual_changed_classifications':'Not identifiable from aggregate confusion counts without original per-row predictions.','confusion_cell_difference':delta.tolist(),'metric_differences':diffs,'classification':kind,'threadpools_during_fit':threadpool_info()}
    write(WORK/'Reconstructed_Clean_Baselines.json',baselines)
    write(OUT/'Reconstruction_Verification.json',{'status':'MODEL_GATE_COMPLETE' if len(verifications)==2 else 'FIRST_MODEL_GATE_COMPLETE','provenance':provenance,'models':verifications,'models_newly_fitted':True,'original_models_replaced':False,'thresholds_changed':False,'historical_evidence_changed':False})
    print('GATE',key,kind,'Macro-F1 difference',r['macro_f1']-old['macro_f1'],'CM max',abs(delta).max(),flush=True)
with (OUT/'Reconstruction_Baseline_Comparison.csv').open('w',newline='',encoding='utf8') as f:
    w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
ranking_ok=(baselines[keys[0]]['macro_f1']>baselines[keys[1]]['macro_f1'])==(historical[keys[0]]['macro_f1']>historical[keys[1]]['macro_f1'])
if not ranking_ok:
    for k in keys:verifications[k]['classification']='C'
success=all(v['classification'] in ['A','B'] for v in verifications.values())
v=json.loads((OUT/'Reconstruction_Verification.json').read_text());v.update({'status':'BOTH_BEHAVIORAL_GATES_PASS' if success else 'RECONSTRUCTION_FAILURE','models':verifications,'ranking_preserved':ranking_ok,'noise_authorized_by_gate':success});write(OUT/'Reconstruction_Verification.json',v)
protected=json.loads((WORK/'Protected_Original_Files.json').read_text());assert all(sha(ROOT/n)==h for n,h in protected.items())
print('BOTH GATES PASS' if success else 'STOP: RECONSTRUCTION FAILURE',flush=True)
