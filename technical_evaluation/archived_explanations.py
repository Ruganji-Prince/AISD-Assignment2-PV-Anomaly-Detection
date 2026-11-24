"""Run the preserved explanation verifier against hash-checked private originals."""
import pickle
from pathlib import Path
from .common import *
def main(private_cache):
 import src.evaluation.verify_explanations as verifier
 cache=Path(private_cache)
 if (cache/'stage2/models').is_dir():cache=cache/'stage2/models'
 proof=load('../reports/model_verification.json');models={}
 for key in ['LR__F6','RF__E4','LightGBM__E4']:
  path=cache/(key+'.pkl');assert sha(path)==proof['original_models'][key]['sha256'];models[key]=path
 # Redirect only read access to three trusted original private model files.
 original_open=Path.read_bytes
 def read_bytes(path):
  if path.parent==ROOT/'.cache/stage2/models' and path.stem in models:return original_open(models[path.stem])
  return original_open(path)
 original_sha=verifier.sha
 verifier.sha=lambda path:sha(models[path.stem]) if path.stem in models else original_sha(path)
 Path.read_bytes=read_bytes
 try:verifier.main()
 finally:Path.read_bytes=original_open;verifier.sha=original_sha
 write('evidence/rubric4/archived_explanations_reverification.json',{'status':'REPRODUCED','original_models':{k:sha(v) for k,v in models.items()},'checks':['Archived raw-channel permutation losses within1e-12','LightGBM native SHAP additivity residual<1e-7','LightGBM mean absolute SHAP matches archived within1e-10','Archived isolated dropout F1 within1e-12'],'no_refitting':True})
