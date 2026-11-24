import time,json,contextlib
import numpy as np,pandas as pd
from joblib import parallel_backend
from technical_evaluation.common import original,raw,CHANNELS,ROOT,SHA
from src.inference.cli import predict
from .experiments import write,freeze

def stats(a):
 a=np.asarray(a);return {'N':len(a),'mean_ms':a.mean(),'std_ms':a.std(ddof=1) if len(a)>1 else 0,'min_ms':a.min(),'max_ms':a.max(),'p50_ms':np.quantile(a,.5),'p95_ms':np.quantile(a,.95),'p99_ms':np.quantile(a,.99)}
def main():
 freeze();start=time.perf_counter();m=original();initialization=(time.perf_counter()-start)*1000;d=raw();rng=np.random.default_rng(42);idx=np.sort(rng.choice(1006129,200,replace=False));x=d.iloc[idx][CHANNELS];reference=m.pipeline.predict_proba(x)
 with parallel_backend('sequential'):candidate=m.pipeline.predict_proba(x)
 np.testing.assert_allclose(candidate,reference,rtol=0,atol=1e-12);assert np.array_equal(candidate.argmax(1),reference.argmax(1));before=m.pipeline[-1].get_params();records=[]
 for mode in ['original','sequential']:
  context=lambda:parallel_backend('sequential') if mode=='sequential' else contextlib.nullcontext()
  for i in range(3):
   with context():predict(x.iloc[i].to_dict(),m,timings={})
  values={k:[] for k in ['validation','frame','preprocessing','forest','total']}
  for i in range(50):
   timing={};start=time.perf_counter()
   with context():result=predict(x.iloc[i].to_dict(),m,timings=timing)
   timing['total']=(time.perf_counter()-start)*1000
   assert result['predicted_class']==int(reference[i].argmax())
   for k in values:values[k].append(timing[k])
  records.append({'mode':mode,'statistics':{k:stats(v) for k,v in values.items()},'failures':0})
 assert m.pipeline[-1].get_params()==before
 write('results/local_runtime.json',{'model_sha256':SHA,'initialization_ms':initialization,'TRAIN_parity_N':200,'class_parity':True,'max_probability_difference':float(abs(candidate-reference).max()),'estimator_params_unchanged':True,'selected_execution_backend':'sequential','rationale':'Thread-local joblib backend avoids per-observation parallel scheduling; no learned object, parameter, feature, threshold or decision change. Selection uses TRAIN runtime/parity only.','results':records,'engineering_target_ms':10,'limitations':'Local wall-clock durations, not billed CPU or cloud latency; selected backend must be separately preview-verified.'})
 print(json.dumps(records,default=float),flush=True)
if __name__=='__main__':main()
