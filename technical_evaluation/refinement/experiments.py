import argparse,json,time,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from scipy.spatial import cKDTree
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from threadpoolctl import threadpool_limits
from technical_evaluation.common import ROOT,raw,part,CHANNELS,SENSORS,B13,B14,original,probs,sha,clean_json,digest
from technical_evaluation.metrics import evaluate,probability_metrics
OUT=ROOT/'technical_evaluation/refinement'
def write(name,x):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean_json(x),indent=2,allow_nan=False)+'\n',encoding='utf8')
def load(name):return json.loads((ROOT/'technical_evaluation'/name).read_text())
def freeze():assert sha(OUT/'Protocol.json')==json.loads((OUT/'Protocol_Freeze.json').read_text())['sha256']
def near():
 freeze();d=raw();train=part(d,'TRAIN');rows=[]
 for features in [CHANNELS,SENSORS]:
  scaler=StandardScaler().fit(train[features]);reference=scaler.transform(train[features]);tree=cKDTree(reference);start=time.perf_counter()
  for name in ['VALIDATION','TEST']:
   frame=part(d,name);distances=[]
   for i in range(0,len(frame),10000):dist,_=tree.query(scaler.transform(frame[features].iloc[i:i+10000]),k=1,eps=0,workers=2);distances.append(dist)
   distances=np.concatenate(distances);rows.append({'features':features,'partition':name,'TRAIN_reference_N':len(train),'query_N':len(frame),'criterion':'Euclidean TRAIN-standardized distance<=0.001','near_N':int((distances<=.001).sum()),'zero_distance_N':int((distances==0).sum()),'min':distances.min(),'q01':np.quantile(distances,.01),'median':np.median(distances),'max':distances.max(),'seconds_since_tree_build':time.perf_counter()-start,'query_index_digest':digest(frame.index)})
   print('FULL_NEAR_DUPLICATES',len(features),name,rows[-1]['near_N'],flush=True)
 write('results/full_near_duplicates.json',{'status':'VERIFIED','exact_query':True,'TRAIN_scaler_only':True,'results':rows,'interpretation':'Similarity is not proof of target leakage; naturally repeated operating regimes may resemble each other. No rows removed or settings selected. No independent-session claim.'})
def synthetic():
 freeze();d=raw();train=part(d,'TRAIN');m=original();results=[];samples=[]
 for seed in [42,43,44,45,46]:
  rng=np.random.default_rng(seed)
  for k in range(5):
   pool=np.flatnonzero(train.f_nv.to_numpy()==k);ids=np.sort(rng.choice(pool,10,replace=False));x=train.iloc[ids][CHANNELS].copy();vg=np.exp(rng.normal(0,.002,len(x)));ig=np.exp(rng.normal(0,.01,len(x)));x[['vdc1','vdc2']]=x[['vdc1','vdc2']].mul(vg,axis=0);x[['idc1','idc2']]=x[['idc1','idc2']].mul(ig,axis=0);p=probs(m,x);labels=p.argmax(1);results.append({'seed':seed,'source_conditioning_class':k,'N':len(x),'agreement_N':int((labels==k).sum()),'agreement_rate':float((labels==k).mean()),'actual_predictions':np.bincount(labels,minlength=5).tolist()})
   for j,(_,row) in enumerate(x.iterrows()):samples.append({'seed':seed,'source_position':int(ids[j]),'source_conditioning_class':k,'measurements':row.to_dict(),'predicted_class':int(labels[j]),'description':'TRAIN-derived joint empirical perturbation, not a validated physical fault simulation'})
 write('results/empirical_scenarios.json',{'generation_procedure_frozen':True,'samples_generated_once':250,'no_prediction_rejection':True,'no_TEST_used':True,'results':results,'overall_agreement':sum(v['agreement_N'] for v in results)/250,'seed_agreement':{str(seed):sum(v['agreement_N'] for v in results if v['seed']==seed)/50 for seed in [42,43,44,45,46]},'samples':samples,'original_five_presets':'Unchanged, still illustrative and separate from these empirical perturbations','limitations':'Conditioning labels refer to source observations, not independently validated new fault labels. Shared gains preserve voltage/current channel ratios within each pair, not all photovoltaic physics. Parent observations were used to train the model; this balanced demonstration is not independent generalization accuracy.'})
 print('EMPIRICAL_SCENARIOS_COMPLETE',sum(v['agreement_N'] for v in results),'/250',flush=True)
def uncertainty():
 freeze();old=load('evidence/rubric3/uncertainty.json');cms=np.stack([np.asarray(v) for v in old['RF_group_confusion_matrices'].values()]);rng=np.random.default_rng(42);allfixed=[];supported=[];conditional=[];absent=0
 def score(cm,only_present=False):
  n=cm.sum(1);den=n+cm.sum(0);f=np.divide(2*np.diag(cm),den,out=np.zeros(5),where=den>0);return float(f[n>0].mean()) if only_present else float(f.mean())
 for _ in range(1000):
  cm=cms[rng.integers(0,12,12)].sum(0);allfixed.append(score(cm));supported.append(score(cm,True))
  if (cm.sum(1)>0).all():conditional.append(score(cm))
  else:absent+=1
 summary=lambda x:{'N':len(x),'mean':np.mean(x),'percentile95':np.quantile(x,[.025,.975])}
 write('results/bootstrap_sensitivity.json',{'seed':42,'repetitions':1000,'unit':'Preserved12 TRAIN grouped-OOF block confusion matrices','unconditional_fixed_five_zero_unsupported_convention':summary(allfixed),'supported_true_classes_only':summary(supported),'conditional_all_five_support':summary(conditional),'resamples_without_all_five_support':absent,'grouped_per_fold':[{k:r[k] for k in ['fold','family','unseen_true_classes','fit_class_support','eval_class_support','metrics']} for r in load('evidence/rubric2/grouped_validation.json')['folds']],'limitation':'All are sensitivity summaries conditional on one fitted grouped-OOF experiment. They are not intervals for deployed TEST performance or independent population coverage; supported-class metric changes its class set.'})
 print('BOOTSTRAP_SENSITIVITY_COMPLETE',flush=True)
def calibration():
 freeze();import technical_evaluation.experiments as ex
 old_write,old_cache=ex.write,ex.CACHE
 ex.write=lambda name,x:write('results/calibration/'+Path(name).name,x);ex.CACHE=ROOT/'.cache/technical_refinement/calibration'
 try:ex.calibration(raw())
 finally:ex.write=old_write;ex.CACHE=old_cache
 old=load('evidence/rubric3/calibration_TEST_retrospective.json');new=json.loads((OUT/'results/calibration/calibration_TEST_retrospective.json').read_text())
 for method,item in old['methods'].items():
  for metric in ['multiclass_Brier','log_loss']:assert abs(item['probability_quality'][metric]-new['methods'][method]['probability_quality'][metric])<1e-12
  assert abs(item['probability_quality']['top_label_reliability']['ECE']-new['methods'][method]['probability_quality']['top_label_reliability']['ECE'])<1e-12
 d=raw();train=part(d,'TRAIN');results={}
 for name in ['most_frequent','prior']:
  model=DummyClassifier(strategy=name).fit(train[CHANNELS],train.f_nv);results[name]={}
  for partition,frame in [('VALIDATION_BLOCK13',d.iloc[slice(*B13)]),('TEST',part(d,'TEST'))]:
   p=model.predict_proba(frame[CHANNELS]);metrics=evaluate(p,frame.f_nv);reference=load('evidence/rubric3/model_comparison.json')['results']['Dummy_'+name][partition];assert abs(metrics['macro_f1_fixed_five']-reference['macro_f1_fixed_five'])<1e-12;results[name][partition]={'metrics':metrics,'probability_quality':probability_metrics(p,frame.f_nv)};np.testing.assert_allclose(p.sum(1),1,atol=1e-12)
 write('results/baseline_reverification.json',{'status':'REPRODUCED','results':results,'class_order':[0,1,2,3,4],'calibration_metrics_match_previous_within':1e-12,'probability_normalization':'All250 synthetic/calibration output class distributions normalized; calibration transform clips and renormalizes; support guards execute per class/fold.'})
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(6,4))
 for method,item in new['methods'].items():
  b=[v for v in item['probability_quality']['top_label_reliability']['bins'] if v['N']];ax.plot([v['mean_probability'] for v in b],[v['observed_frequency'] for v in b],marker='o',label=method)
 ax.plot([0,1],[0,1],':',color='gray');ax.set(xlabel='Mean top-label probability',ylabel='Observed correctness',title='Reproduced historical TEST reliability (retrospective)');ax.legend();fig.tight_layout();folder=OUT/'figures';folder.mkdir(exist_ok=True);fig.savefig(folder/'reproduced_reliability.png',dpi=180);plt.close(fig)
 normalization()
 print('CALIBRATION_BASELINE_REPRODUCTION_COMPLETE',flush=True)
def normalization():
 import pickle
 d=raw();m=original();record=load('refinement/results/calibration/calibration_TEST_retrospective.json');rows=[]
 for method in ['sigmoid','isotonic']:
  path=ROOT/'.cache/technical_refinement/calibration'/('calibration_'+method+'.pkl');assert sha(path)==record['methods'][method]['private_artifact_sha256'];mapper=pickle.loads(path.read_bytes())
  for name,frame in [('BLOCK14',d.iloc[slice(*B14)]),('TEST',part(d,'TEST'))]:
   q=mapper.transform(probs(m,frame));np.testing.assert_allclose(q.sum(1),1,atol=1e-12);assert np.isfinite(q).all() and(q>=0).all();rows.append({'method':method,'population':name,'N':len(q),'maximum_row_sum_error':float(abs(q.sum(1)-1).max()),'minimum_probability':float(q.min()),'positive_negative_fit_support':mapper.support})
 write('results/probability_normalization.json',{'status':'VERIFIED','rows':rows,'no_calibrated_threshold_selected':True,'no_production_calibration':True})
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['near','synthetic','uncertainty','calibration','normalization']);a=p.parse_args();threadpool_limits(2);globals()[a.stage]()
if __name__=='__main__':main()
