from pathlib import Path
import json,pickle,hashlib,datetime,warnings
import numpy as np
import pandas as pd
from src.phase2_stage1.contracts import ROOT,SEED,BLOCK13,SENSORS,DEPENDENCIES,sha,write_json,index_digest,runtime
from src.phase2_stage1.features import eligible
from src.phase2_stage1.evaluation import evaluate,hardware_alert_metrics
from src.phase2_stage2.contracts import CONFIGS,frozen_weights
OUT=ROOT/'phase2_implementation/stage3'
E=OUT/'evidence'
BLOCK14=(1140571,1173967)
TEST=(1227337,1373798)
CANDIDATES=['LR__F6','RF__E4','LightGBM__E4']
REFERENCES=['RF__F6','LightGBM__F6']
RULE='Maximize hardware-alert recall subject to combined Y in {0,4} FPR <= .01; break equal-recall ties by lower FPR, then higher threshold.'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def model_path(key):return ROOT/'.cache/stage2/models'/(key+'.pkl')
def load_model(key):
 with model_path(key).open('rb') as f:return pickle.load(f)
def load_part(bounds):
 a,b=bounds
 d=pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv',skiprows=range(1,a+1),nrows=b-a,float_precision='round_trip')
 d.index=np.arange(a,b);assert list(d)==SENSORS+['f_nv'];return d
class FrozenPredictor:
 """Read-only adapter for authorized Stage 3 partitions; historical guards remain unchanged."""
 def __init__(self,model,partition):self.model=model;self.partition=partition
 def predict_proba(self,X):
  m=self.model
  if list(X)!=m.channels or not X.index.is_unique or not X.index.is_monotonic_increasing:raise ValueError('Retained channels and ordered unique positions only')
  a,b=self.partition
  if len(X) and not ((X.index>=a)&(X.index<b)).all():raise ValueError('Prediction outside explicitly authorized partition')
  clean=m.pipeline.named_steps['quality'].transform(X)
  with warnings.catch_warnings():
   warnings.filterwarnings('ignore',message=r'`sklearn.utils.parallel.delayed` should be used.*',category=UserWarning)
   p=m.pipeline[1:].predict_proba(clean)
  p[~eligible(clean,m.boundaries)]=np.nan
  return p

def select_threshold(p,y):
 """Enumerate every distinct-score decision set plus a no-alert sentinel; exact tied scores stay together."""
 y=np.asarray(y);ok=np.isfinite(p).all(axis=1);s=np.nan_to_num(p,nan=0.)[:,1:4].sum(axis=1)
 order=np.argsort(-s[ok],kind='stable');v=s[ok][order];h=np.isin(y[ok][order],[1,2,3]);H=int(np.isin(y,[1,2,3]).sum());N=len(y)-H
 ends=np.r_[np.flatnonzero(np.diff(v)!=0),len(v)-1];tp=np.cumsum(h)[ends];fp=np.cumsum(~h)[ends]
 thresholds=np.r_[np.nextafter(v[0],np.inf),v[ends]];tp=np.r_[0,tp];fp=np.r_[0,fp]
 feasible=fp/N<=.01
 # Abstention does not alert and counts as a hardware miss. A finite above-max sentinel always yields zero FPR.
 ranked=sorted(np.flatnonzero(feasible),key=lambda i:(-int(tp[i]),int(fp[i]),-float(thresholds[i])))
 if not ranked:raise RuntimeError('No feasible threshold, including no-alert sentinel; invalid population')
 i=ranked[0];threshold=float(thresholds[i]);m=hardware_alert_metrics(s,y,threshold,ok)
 from sklearn.metrics import average_precision_score
 m['average_precision']=float(average_precision_score(np.isin(y,[1,2,3]),s))
 m.update({'selection_rule':RULE,'distinct_operating_points':len(thresholds),'feasible_operating_points':int(feasible.sum()),'no_alert_sentinel_selected':bool(i==0),'criterion_pass':m['combined_nonhardware_FPR']<=.01,'fallback':'If no positive-recall feasible point exists, retain the zero-alert sentinel and disclose zero recall; never weaken FPR constraint.'})
 return m

def protect():
 target=OUT/'Protected_Foundation_Hashes.json'
 if target.exists():return
 old=json.loads((ROOT/'phase2_implementation/stage2/Protected_Foundation_Hashes.json').read_text())['sha256']
 names=set(old)
 for folder in ['src/phase2_stage2','phase2_implementation/stage2']:
  names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 names.update(['phase2_implementation/run_stage2.py','phase2_implementation/verify_stage2.py'])
 names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'.cache/stage2/models').glob('*.pkl'))
 write_json(target,{'created_utc':now(),'sha256':{n:sha(ROOT/n) for n in sorted(names)}})
def check_protected():
 record=json.loads((OUT/'Protected_Foundation_Hashes.json').read_text())
 for n,h in record['sha256'].items():
  if sha(ROOT/n)!=h:raise AssertionError('Protected file changed: '+n)
 return len(record['sha256'])
def csv(name,rows):
 pd.DataFrame(rows).to_csv(E/name,index=False)
