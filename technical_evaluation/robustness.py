"""Frozen-model diagnostics; simulated perturbations are not field observations."""
import json
import numpy as np
import pandas as pd
from scipy.stats import ks_2samp,wasserstein_distance
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from .common import *
from .metrics import evaluate

def main():
 d=raw();m=original();train=part(d,'TRAIN');rng=np.random.default_rng(42);tau=.5913558658757772
 derived=lambda f:{'temperature':f.pvt.to_numpy(),'electrical_output':(f.vdc1*f.idc1+f.vdc2*f.idc2).to_numpy(),'voltage_imbalance':(abs(f.vdc1-f.vdc2)/(abs(f.vdc1)+abs(f.vdc2)+1e-12)).to_numpy(),'current_imbalance':(abs(f.idc1-f.idc2)/(abs(f.idc1)+abs(f.idc2)+1e-12)).to_numpy()}
 bounds={k:np.unique(np.quantile(v,[.25,.5,.75])) for k,v in derived(train).items()};subgroups=[];shift=[];predictions={}
 for name in PARTS:
  frame=part(d,name);p=probs(m,frame);predictions[name]=p;CACHE.mkdir(parents=True,exist_ok=True);np.savez_compressed(CACHE/(name+'_probabilities.npz'),p=p,index=frame.index.to_numpy())
  cohort={'irradiance':np.digitize(frame.irr,[100,400,800]),'signal_block':groups(frame.index)}
  cohort.update({k:np.digitize(v,bounds[k]) for k,v in derived(frame).items()})
  for variable,g in cohort.items():
   for value in np.unique(g):
    mask=g==value;result=evaluate(p[mask],frame.f_nv.to_numpy()[mask],tau);subgroups.append({'partition':name,'variable':variable,'group':int(value),'small_N':int(mask.sum())<100,'small_class_support':{str(k):int(sum(frame.f_nv.to_numpy()[mask]==k))<50 for k in range(5)},**result})
  if name!='TRAIN':
   for c in SENSORS:
    x=train[c].to_numpy();z=frame[c].to_numpy();edges=np.unique(np.quantile(x,np.linspace(0,1,11)));edges[0]=-np.inf;edges[-1]=np.inf;a=np.histogram(x,edges)[0]/len(x);b=np.histogram(z,edges)[0]/len(z);a=np.maximum(a,1e-6);b=np.maximum(b,1e-6);a/=a.sum();b/=b.sum();iqr=np.subtract(*np.quantile(x,[.75,.25]));shift.append({'partition':name,'sensor':c,'PSI':sum((b-a)*np.log(b/a)),'KS_statistic':ks_2samp(x,z).statistic,'Wasserstein_sensor_units':wasserstein_distance(x,z),'Wasserstein_per_TRAIN_IQR':wasserstein_distance(x,z)/iqr if iqr else None,'TRAIN_bins':edges.tolist(),'cohort_fractions':b,'TRAIN_fractions':a,'KS_p_value':'Not interpreted: dependent rows do not support iid significance.'})
 write('evidence/rubric4/subgroups.json',{'boundaries_TRAIN_quartiles':bounds,'irradiance_W_per_m2':[100,400,800],'block0':'Outside signal-defined operating intervals; not a verified session.','metrics':subgroups})
 write('evidence/rubric4/shift.json',{'reference':'TRAIN-fitted decile bins; PSI epsilon1e-6 then normalization','results':shift,'class_prevalence':{n:part(d,n).f_nv.value_counts(normalize=True).sort_index().to_dict() for n in PARTS},'interpretation':'Source-position cohort shift, not verified temporal drift; effect sizes are descriptive.'})
 test=part(d,'TEST');p=predictions['TEST'];wrong=(test.f_nv.to_numpy()==0)&(p.argmax(1)==4);correct=(test.f_nv.to_numpy()==0)&(p.argmax(1)==0)
 write('evidence/rubric4/normal_shade_errors.json',{'normal_to_shade_N':int(wrong.sum()),'correct_normal_N':int(correct.sum()),'shade_precision':evaluate(p,test.f_nv)['per_class']['4']['precision'],'medians':{c:{'misclassified_normal':float(test.loc[wrong,c].median()),'correct_normal':float(test.loc[correct,c].median())} for c in SENSORS},'interpretation':'Measured conditional sensor differences are predictive associations; no causal attribution is established.'})
 val=d.iloc[slice(*B13)];ids=np.sort(rng.choice(len(val),12000,replace=False));sample=val.iloc[ids];scale=train[CHANNELS].quantile(.75)-train[CHANNELS].quantile(.25);base=evaluate(probs(m,sample),sample.f_nv,tau);experiments=[]
 def run(kind,f,seed=None,amount=None,channel=None):
  r=evaluate(probs(m,f),f.f_nv,tau);experiments.append({'experiment':kind,'seed':seed,'amount':amount,'channel':channel,'delta_macro_f1_fixed_five':r['macro_f1_fixed_five']-base['macro_f1_fixed_five'],**r})
 for magnitude in [.01,.02,.05,.1]:
  for seed in [42,43,44]:
   f=sample.copy();f[CHANNELS]=np.maximum(0,f[CHANNELS].to_numpy()+np.random.default_rng(seed).normal(size=(len(f),4))*scale.to_numpy()*magnitude);run('Gaussian_noise_TRAIN_IQR',f,seed,magnitude)
 for magnitude in [-.1,-.05,.05,.1]:
  f=sample.copy();f[CHANNELS]=np.maximum(0,f[CHANNELS]+scale*magnitude);run('additive_bias_TRAIN_IQR',f,amount=magnitude)
 for channel in CHANNELS:
  f=sample.copy();f[channel]=np.nan;run('entire_channel_dropout',f,channel=channel)
  for side,q in [('low',.05),('high',.95)]:
   f=sample.copy();f[channel]=train[channel].quantile(q);run('saturation_'+side,f,amount=q,channel=channel)
 f=sample.copy();f[CHANNELS[:2]]=np.nan;run('two_channel_dropout',f,channel='vdc1+vdc2')
 f=sample.copy();f[CHANNELS]=np.tile((train[CHANNELS].max()+scale).to_numpy(),(len(f),1));run('finite_OOD_TRAIN_max_plus_IQR',f)
 write('evidence/rubric4/stress.json',{'population':'Fixed seed42 natural-prevalence 12000 observations from VALIDATION block13; no TEST selection','index_digest':digest(sample.index),'scale_TRAIN_IQR':scale.to_dict(),'baseline':base,'results':experiments,'interpretation':'Simulated sensor perturbations, not measured field failures. Dropout coverage follows offline eligibility/abstention policy; public API separately rejects missing inputs. No robustness model or new threshold was fitted.'})
 # Raw-channel permutation recomputes every downstream mathematical feature.
 ids=np.concatenate([rng.choice(np.flatnonzero(val.f_nv.to_numpy()==k),200,replace=False) for k in range(5)]);sample=val.iloc[np.sort(ids)];baseline=evaluate(probs(m,sample),sample.f_nv)['macro_f1_fixed_five'];importance=[]
 for channel in CHANNELS:
  for repeat in range(3):
   f=sample.copy();f[channel]=rng.permutation(f[channel].to_numpy());score=evaluate(probs(m,f),f.f_nv)['macro_f1_fixed_five'];importance.append({'channel':channel,'repeat':repeat,'baseline_macro_f1':baseline,'permuted_macro_f1':score,'decrease':baseline-score})
 write('evidence/rubric4/RF_raw_channel_permutation.json',{'population':'VALIDATION block13 balanced200/class=1000; seed42; three repeats; not natural-prevalence performance','sample_index_digest':digest(sample.index),'results':importance,'causality':'Not causal; correlated channels can redistribute importance.'})
 # TRAIN-only joint-neighborhood investigation; illustrative scenarios remain unchanged.
 scaler=StandardScaler().fit(train[CHANNELS]);ri=np.sort(rng.choice(len(train),100000,replace=False));nn=NearestNeighbors(n_neighbors=100,n_jobs=2).fit(scaler.transform(train[CHANNELS].iloc[ri]));cases=json.loads((ROOT/'web/synthetic_test_cases.json').read_text());records=[]
 for case in cases:
  f=pd.DataFrame([case['input']],columns=CHANNELS,index=[0]);distance,neighbors=nn.kneighbors(scaler.transform(f));p=probs(m,f)[0];records.append({'intended_label':case['intent'],'predicted_label':int(p.argmax()),'raw_model_probabilities_uncalibrated':p,'nearest_TRAIN_standardized_distance':distance[0,0],'neighbor100_class_counts':train.f_nv.iloc[ri[neighbors[0]]].value_counts().sort_index().to_dict(),'outside_TRAIN_q005_q995':{c:bool(f[c].iloc[0]<train[c].quantile(.005) or f[c].iloc[0]>train[c].quantile(.995)) for c in CHANNELS}})
 write('evidence/rubric4/synthetic_investigation.json',{'reference':'Seed42 natural-prevalence TRAIN sample100000; TRAIN-fitted scaling; no TEST tuning','cases':records,'TRAIN_class_channel_quantiles':{str(k):train.loc[train.f_nv==k,CHANNELS].quantile([.005,.25,.5,.75,.995]).to_dict() for k in range(5)},'interpretation':'Hand-designed marginal electrical signatures need not follow the learned joint distribution. Neighbors and ranges are descriptive, not certified OOD detection. Presets and historical examples remain unchanged.'})
 print('ROBUSTNESS_AND_SHIFT_COMPLETE',flush=True)

def contiguous_dropout():
 from .metrics import evaluate
 freeze_check();d=raw();f=d.iloc[slice(*B13)];m=original();out=[]
 for channel in CHANNELS:
  z=f.copy();z[channel]=np.nan;out.append({'channel':channel,**evaluate(probs(m,z),z.f_nv,.5913558658757772)})
 write('evidence/rubric4/contiguous_dropout.json',{'population':'Full uninterrupted VALIDATION block13 source positions','results':out,'interpretation':'Persistent missingness is not equivalent to isolated missing samples. The eligibility rule abstains after two consecutive unavailable source positions. API rejects missing values.'})
