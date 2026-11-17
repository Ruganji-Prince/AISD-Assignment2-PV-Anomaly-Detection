"""Immutable foundation, F6-only fitting contract, and train/block-13 loading."""
from pathlib import Path
import hashlib,json,platform,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'phase2_implementation/stage1'
EVIDENCE=OUT/'evidence'
SEED=42
SENSORS=['vdc1','vdc2','idc1','idc2','irr','pvt']
CLASSES=['Normal','Short circuit','Resistive degradation','Open circuit','Building shade']
TRAIN_COUNTS={0:844805,1:1226,2:5695,3:1204,4:153199}
RAW_COUNTS={0:1162931,1:5999,2:10371,3:6024,4:188473}
PAPER_COUNTS={0:309253,1:5999,2:10371,3:6024,4:184311}
TRAIN=(0,1006129)
BLOCK13=(1056990,1089790)
BLOCK13_COUNTS={0:18504,1:1232,2:1222,3:1206,4:10636}
DEPENDENCIES={'P1':['vdc1','idc1'],'P2':['vdc2','idc2'],
 'P_total':['vdc1','idc1','vdc2','idc2'],'V_diff':['vdc1','vdc2'],'I_diff':['idc1','idc2']}

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def write_json(path,obj):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')

def foundation_check():
 record=json.loads((OUT/'Phase1_Protected_Hashes.json').read_text(encoding='utf8'))
 for name,expected in record['sha256'].items():
  if sha(ROOT/name)!=expected:raise ValueError('Changed protected Phase 1 file: '+name)
 return {'protected_files':len(record['sha256']),'foundation_commit':record['foundation_commit'],'all_hashes_match':True}

def counts(y):return {int(k):int(v) for k,v in pd.Series(np.asarray(y)).value_counts().sort_index().items()}

def weights(y):
 n=counts(y)
 if n!=TRAIN_COUNTS:raise ValueError('Weights must use exactly the frozen training population.')
 return {k:len(y)/(5*n[k]) for k in range(5)}

def index_digest(index):return hashlib.sha256(np.asarray(index,dtype=np.int64).tobytes()).hexdigest()

def validate_predictors(X):
 if not isinstance(X,pd.DataFrame) or list(X.columns)!=SENSORS:
  raise ValueError('Exactly the six F6 raw columns are required; labels/index/block/time features prohibited.')
 if not X.index.is_unique or not X.index.is_monotonic_increasing:raise ValueError('Source positions must be unique and ordered.')

def train_only(X):
 validate_predictors(X)
 if len(X)!=TRAIN[1] or not np.array_equal(X.index.to_numpy(),np.arange(*TRAIN)):
  raise ValueError('Fitting is restricted to the complete frozen training partition.')

def load_stage1():
 foundation_check();path=ROOT/'data/raw/pv_fault_dataset.csv'
 # Never construct block-14 or test frames for Stage 1 model selection.
 train=[];val=[];offset=0;raw_counts={k:0 for k in range(5)}
 thresholds={s:{'N':0,'class_counts':{k:0 for k in range(5)}} for s in ['irr_le_0','irr_lt_10','irr_lt_50','irr_lt_100','irr_ge_100']}
 for c in pd.read_csv(path,chunksize=100000,float_precision='round_trip'):
  assert list(c)==SENSORS+['f_nv'] and not c.isna().any().any()
  end=offset+len(c);c.index=np.arange(offset,end);c.index.name='source_position'
  for k,v in counts(c.f_nv).items():raw_counts[k]+=v
  masks=[c.irr<=0,c.irr<10,c.irr<50,c.irr<100,c.irr>=100]
  for key,m in zip(thresholds,masks):
   thresholds[key]['N']+=int(m.sum())
   for k,v in counts(c.loc[m,'f_nv']).items():thresholds[key]['class_counts'][k]+=v
  for bounds,dest in [(TRAIN,train),(BLOCK13,val)]:
   lo=max(bounds[0],offset);hi=min(bounds[1],end)
   if lo<hi:dest.append(c.loc[lo:hi-1].copy())
  offset=end
 assert offset==1373798 and raw_counts==RAW_COUNTS
 assert thresholds['irr_ge_100']['N']==515958 and thresholds['irr_ge_100']['class_counts']==PAPER_COUNTS
 assert thresholds['irr_lt_100']['N']==857840
 train=pd.concat(train);val=pd.concat(val)
 assert counts(train.f_nv)==TRAIN_COUNTS and counts(val.f_nv)==BLOCK13_COUNTS
 discrepancy={'raw_N':offset,'paper_class_counts':PAPER_COUNTS,'paper_total':sum(PAPER_COUNTS.values()),
  'difference':offset-sum(PAPER_COUNTS.values()),'raw_class_counts':raw_counts,'thresholds':thresholds,
  'population_policy':'Primary experiment retains all approved training/validation rows; no irradiance filtering.',
  'interpretation':'Exact numerical agreement supports an irradiance-qualified interpretation; the source filtering procedure is not explicitly verified.'}
 return train,val,discrepancy

def runtime():
 from importlib.metadata import version
 import psutil
 return {'python':sys.version,'platform':platform.platform(),'machine':platform.machine(),
  'processor':platform.processor(),'physical_cores':psutil.cpu_count(logical=False),
  'logical_cores':psutil.cpu_count(),'RAM_bytes':psutil.virtual_memory().total,
  'dependencies':{x:version(x) for x in ['numpy','pandas','scipy','scikit-learn','lightgbm','matplotlib','joblib','psutil']},
  'seed':SEED,'threads':2}
