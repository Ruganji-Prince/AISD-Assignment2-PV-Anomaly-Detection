"""Protected Phase 1/Stage 1 contracts and immutable Stage 2 configuration."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
from src.phase2_stage1.contracts import ROOT,SENSORS,TRAIN,BLOCK13,SEED,DEPENDENCIES,TRAIN_COUNTS,BLOCK13_COUNTS,counts,index_digest,runtime,write_json,sha
OUT=ROOT/'phase2_implementation/stage2'
EVIDENCE=OUT/'evidence'
CONFIGS={'F6':SENSORS,'E5':['vdc1','vdc2','idc1','idc2','irr'],'E4':['vdc1','vdc2','idc1','idc2'],
 'C3':['idc1','idc2','irr'],'C2':['idc1','idc2'],'S4':['vdc1','idc1','irr','pvt'],'S2':['vdc1','idc1']}
FAMILIES=['LR','RF','LightGBM']
WARMUPS=100
TIMED_CALLS=2000


def foundation_check():
 record=json.loads((OUT/'Protected_Foundation_Hashes.json').read_text(encoding='utf8'))
 for name,expected in record['sha256'].items():
  if sha(ROOT/name)!=expected:raise ValueError('Changed protected foundation file: '+name)
 return {'all_hashes_match':True,'protected_files':len(record['sha256']),'foundation_commit':record['git_HEAD']}


def load_partitions():
 foundation_check();path=ROOT/'data/raw/pv_fault_dataset.csv'
 train=pd.read_csv(path,nrows=TRAIN[1],float_precision='round_trip')
 val=pd.read_csv(path,skiprows=range(1,BLOCK13[0]+1),nrows=BLOCK13[1]-BLOCK13[0],float_precision='round_trip')
 train.index=np.arange(*TRAIN);val.index=np.arange(*BLOCK13)
 assert list(train)==SENSORS+['f_nv'] and list(val)==SENSORS+['f_nv']
 assert counts(train.f_nv)==TRAIN_COUNTS and counts(val.f_nv)==BLOCK13_COUNTS
 return train,val


def frozen_weights():
 record=json.loads((ROOT/'phase2_implementation/stage1/evidence/class_weights.json').read_text(encoding='utf8'))
 # Load the exact Stage 1 values once; do not design/recompute weights for configurations.
 return {int(k):v for k,v in record['weights'].items()}


def schema(X,channels,training=False):
 if not isinstance(X,pd.DataFrame) or list(X.columns)!=list(channels):raise ValueError('Only retained raw channels are allowed; labels/index/time/block fields prohibited.')
 if not X.index.is_unique or not X.index.is_monotonic_increasing:raise ValueError('Ordered unique source positions required.')
 if training:
  if len(X)!=TRAIN[1] or not np.array_equal(X.index,np.arange(*TRAIN)):raise ValueError('Fit is restricted to frozen TRAIN.')
 elif len(X) and not ((X.index>=BLOCK13[0])&(X.index<BLOCK13[1])).all():
  raise ValueError('Stage 2 predictions restricted to block 13; block 14 and test disabled.')


def available_features(config,family):
 raw=CONFIGS[config];derived=[k for k,parents in DEPENDENCIES.items() if set(parents)<=set(raw)] if family=='LightGBM' else []
 return {'raw_channels':raw,'physical_channel_count':len(raw),'engineered_features':derived,
  'mathematical_feature_count':2*len(raw)+len(derived),'numeric_features':raw+derived,
  'availability_indicators':['missingindicator_'+c for c in raw],
  'mathematical_feature_names':['numeric__'+c for c in raw+derived]+['missing__missingindicator_'+c for c in raw],
  'dependencies':{k:DEPENDENCIES[k] for k in derived},'all_dependencies_retained':all(set(DEPENDENCIES[k])<=set(raw) for k in derived)}
