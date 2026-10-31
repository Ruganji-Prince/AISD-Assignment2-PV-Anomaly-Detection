from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'phase2_implementation/compliance'
FIGURES=ROOT/'phase2_implementation/preprocessing_diagnostics'
SENSORS=['vdc1','vdc2','idc1','idc2','irr','pvt']
TRAIN=(0,1006129);VALIDATION=(1056990,1173967);TEST=(1227337,1373798)
SEED=42
UNITS={'vdc1':'V','vdc2':'V','idc1':'A','idc2':'A','irr':'W/m²','pvt':'°C'}
LABELS=['Normal','Short circuit','Resistive degradation','Open circuit','Building shade']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,obj):
 Path(p).parent.mkdir(exist_ok=True,parents=True);Path(p).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n',encoding='utf8')
def digest(index):
 import numpy as np
 return hashlib.sha256(np.asarray(index,dtype=np.int64).tobytes()).hexdigest()
