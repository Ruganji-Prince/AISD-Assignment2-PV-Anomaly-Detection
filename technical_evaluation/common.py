from pathlib import Path
import json,hashlib,datetime,platform,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'technical_evaluation'
CACHE=ROOT/'.cache/technical_evaluation'
SENSORS=['vdc1','vdc2','idc1','idc2','irr','pvt']
CHANNELS=SENSORS[:4]
PARTS={'TRAIN':(0,1006129),'VALIDATION':(1056990,1173967),'TEST':(1227337,1373798)}
B13=(1056990,1089790);B14=(1140571,1173967)
SEED=42
SHA='55b0e94d86f548b14444182de977f521e4ab79e7d92b339190b45ed23bd5ccdb'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(index):return hashlib.sha256(np.asarray(index,dtype='<i8').tobytes()).hexdigest()
def clean_json(x):
 if isinstance(x,dict):return {str(k):clean_json(v) for k,v in x.items()}
 if isinstance(x,(list,tuple,np.ndarray)):return [clean_json(v) for v in x]
 if isinstance(x,(np.integer,)):return int(x)
 if isinstance(x,(np.floating,float)):return float(x) if np.isfinite(x) else None
 if isinstance(x,np.bool_):return bool(x)
 return x

def write(name,x):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean_json(x),indent=2,allow_nan=False)+'\n',encoding='utf8')
def csv(name,rows):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True);pd.DataFrame(rows).to_csv(p,index=False)
def load(name):return json.loads((OUT/name).read_text(encoding='utf8'))
def freeze_check():assert sha(OUT/'Protocol.json')==load('Protocol_Freeze.json')['protocol_sha256'];assert sha(ROOT/'models/rf_e4/model.pkl')==SHA

def raw():
 freeze_check();d=pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv',float_precision='round_trip');assert d.shape==(1373798,7) and list(d)==SENSORS+['f_nv'];return d

def blocks():return json.loads((ROOT/'phase1_strategy/Phase1_Split_Manifest.json').read_text())['operating_blocks']
def groups(index):
 a=np.asarray(index);out=np.zeros(len(a),dtype=int)
 for b in blocks():out[(a>=b['start'])&(a<b['end_exclusive'])]=b['block']
 return out

def part(d,name):a,b=PARTS[name];return d.iloc[a:b]
def original():
 from src.inference.cli import load_model
 freeze_check();return load_model()
def probs(model,d):
 from src.phase2_stage3.common import FrozenPredictor
 return FrozenPredictor(model,(int(d.index.min()),int(d.index.max())+1)).predict_proba(d[model.channels])
def version_info():
 from importlib.metadata import version
 return {'python':platform.python_version(),'platform':platform.platform(),'seed':SEED,'threads':2,'packages':{k:version(k) for k in ['numpy','pandas','scipy','scikit-learn','lightgbm','matplotlib','joblib']}}
