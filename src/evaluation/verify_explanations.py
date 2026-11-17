"""Reproduce archived explanations/dropout; requires original private model cache, no fitting."""
import json
import pickle
import numpy as np
import pandas as pd
from src.phase2_stage1.contracts import ROOT,sha
from src.phase2_stage3.common import load_part,FrozenPredictor,BLOCK13
from src.phase2_stage1.evaluation import evaluate

def main():
 v=load_part(BLOCK13);e=ROOT/'phase2_implementation/stage3/evidence'
 meta=json.loads((e/'explainability_metadata.json').read_text());sample=v.loc[meta['source_positions']]
 rows=pd.read_csv(e/'physical_channel_permutation.csv');proof=json.loads((ROOT/'reports/model_verification.json').read_text())
 old=json.loads((ROOT/'phase2_implementation/stage2/evidence/isolated_dropout_validation.json').read_text())
 drop=json.loads((e/'dropout_validation.json').read_text());results={}
 for key in ['LR__F6','RF__E4','LightGBM__E4']:
  path=ROOT/'.cache/stage2/models'/f'{key}.pkl';assert sha(path)==proof['original_models'][key]['sha256']
  m=pickle.loads(path.read_bytes());adapter=FrozenPredictor(m,BLOCK13);X=sample[m.channels]
  base=evaluate(adapter.predict_proba(X),sample.f_nv)
  for row in rows[rows.candidate==key].to_dict('records'):
   z=X.copy();z[row['channel']]=np.random.default_rng(42+int(row['repeat'])).permutation(z[row['channel']].to_numpy())
   met=evaluate(adapter.predict_proba(z),sample.f_nv)
   assert abs(base['macro_f1']-met['macro_f1']-row['macro_f1_loss'])<1e-12
  if key=='LightGBM__E4':
   t=m.pipeline[:-1].transform(X);est=m.pipeline.named_steps['model']
   con=np.asarray(est.booster_.predict(t,pred_contrib=True,num_threads=2)).reshape(len(X),5,14)
   raw=est.booster_.predict(t,raw_score=True,num_threads=2)
   assert np.max(abs(con.sum(2)-raw))<1e-7
   expected=pd.read_csv(e/'shap_mean_absolute.csv')
   for row in expected.to_dict('records'):
    j=list(m.names()).index(row['feature']);k=int(row['class'])
    assert abs(np.abs(con[:,k,j]).mean()-row['mean_abs_SHAP'])<1e-10
  altered=v[m.channels].copy();positions=np.array(old['positions_in_block13']);choices=np.array(drop['outcomes'][key]['channel_choices'])
  for j in range(len(m.channels)):altered.iloc[positions[choices==j],j]=np.nan
  met=evaluate(adapter.predict_proba(altered),v.f_nv)
  assert abs(met['macro_f1']-drop['outcomes'][key]['dropout_macro_f1'])<1e-12
  results[key]='PASS'
 print(json.dumps(results,indent=2))
if __name__=='__main__':main()
