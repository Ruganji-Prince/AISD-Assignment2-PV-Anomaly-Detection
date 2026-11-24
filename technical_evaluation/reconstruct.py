"""Explicit opt-in public reconstruction from verified archived parameters, never original bytes."""
import argparse,pickle,time
import pandas as pd,numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from lightgbm import LGBMClassifier
from src.phase2_stage2.models import build_preprocessor
from .common import *
from .experiments import assert_fit_isolated
from .metrics import evaluate

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--candidate',default='RF__E4',help='One recorded key or all (expensive).');args=parser.parse_args();d=raw();train=part(d,'TRAIN');val=d.iloc[slice(*B13)];specs=load('evidence/rubric3/original_model_parameters.json');keys=list(specs) if args.candidate=='all' else [args.candidate];rows=[]
 for key in keys:
  spec=specs[key];params=spec['estimator_params'];params['class_weight']={int(k):v for k,v in params['class_weight'].items()};counts=train.f_nv.value_counts();expected={int(k):len(train)/(len(counts)*int(v)) for k,v in counts.items()}
  for k,v in expected.items():assert abs(params['class_weight'][k]-v)<1e-12
  estimator={'LR':LogisticRegression,'RF':RandomForestClassifier,'LightGBM':LGBMClassifier}[spec['family']](**params);prep=build_preprocessor(spec['family'],spec['channels']);pipe=Pipeline(prep.steps+[('model',estimator)]);assert_fit_isolated(train.index,val.index);start=time.perf_counter();pipe.fit(train[spec['channels']],train.f_nv);prob=pipe.predict_proba(val[spec['channels']]);path=CACHE/('public_reconstruction_'+key+'.pkl');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(pickle.dumps(pipe));rows.append({'candidate':key,'new_sha256':sha(path),'original_reference_sha256':spec['original_sha256'],'fit_seconds':time.perf_counter()-start,'fit_index_digest':digest(train.index),'validation':evaluate(prob,val.f_nv),'provenance':'NEW reconstruction; no byte-identical claim; no TEST used.'})
 write('evidence/rubric3/public_reconstruction_run.json',{'models':rows,'original_deployed_model_changed':False})
if __name__=='__main__':main()
