"""Repair affected resource evidence using existing cached models; never fit estimators."""
import json,pickle,warnings,collections
import pandas as pd
from .contracts import *
from .resources import measure
from .run import save_csv,dropout
from .selection import pass_flags,select

def main():
 foundation_check();val=pd.read_csv(ROOT/'data/raw/pv_fault_dataset.csv',skiprows=range(1,BLOCK13[0]+1),nrows=BLOCK13[1]-BLOCK13[0],float_precision='round_trip');val.index=range(*BLOCK13)
 details=json.loads((EVIDENCE/'ablation_details.json').read_text());resources=pd.read_csv(EVIDENCE/'resource_metrics.csv',float_precision='round_trip').to_dict('records')
 table=pd.read_csv(EVIDENCE/'sensor_ablation_validation.csv',float_precision='round_trip').to_dict('records')
 correction=json.loads((EVIDENCE/'resource_benchmark_correction.json').read_text());outcomes={};count=collections.Counter();original_show=warnings.showwarning
 def show(message,category,filename,lineno,file=None,line=None):
  if str(message).startswith('`sklearn.utils.parallel.delayed` should be used'):
   count['known_parallel_diagnostic']+=1;return
  return original_show(message,category,filename,lineno,file,line)
 warnings.showwarning=show
 try:
  for key in ['RF__F6','RF__E5','RF__E4']:
   print('Resource-only remeasurement '+key,flush=True)
   family,config=key.split('__');path=ROOT/'.cache/stage2/models'/(key+'.pkl');before=sha(path)
   with path.open('rb') as f:model=pickle.load(f)
   prior=dict(next(x for x in resources if x['key']==key));previous_count=count['known_parallel_diagnostic']
   latency=measure(model,val[CONFIGS[config]])
   assert sha(path)==before
   resource=next(x for x in resources if x['key']==key)
   for field in ['p50_ms','p95_ms','p99_ms']:resource[field]=latency[field]
   details[key]['latency']=latency
   row=next(x for x in table if x['key']==key)
   for field in ['p50_ms','p95_ms']:row[field]=latency[field]
   cp_path=EVIDENCE/'checkpoints'/(key+'.json');cp=json.loads(cp_path.read_text())
   cp['resource']=resource;cp['details']=details[key]
   for field in ['p50_ms','p95_ms']:cp['summary'][field]=latency[field]
   write_json(cp_path,cp)
   outcomes[key]={'previous_resource':prior,'corrected_resource':dict(resource),'known_diagnostic_handler_calls':count['known_parallel_diagnostic']-previous_count,'model_sha256_unchanged':before}
   print(f'  p95={latency["p95_ms"]:.3f} ms; no retraining',flush=True)
 finally:warnings.showwarning=original_show
 for row in table:
  flags=pass_flags(row)
  for k,v in flags.items():row[k]=v
 records=[dict(row,criteria=pass_flags(row)) for row in table]
 selection=select(records);old_selection=json.loads((EVIDENCE/'stage2_selection.json').read_text())
 for k in ['frozen_stage1_settings','F6_macro_f1_references','criteria_note','selection_population','revised_test_evaluation','block14_threshold_selection','prior_test_exposure']:selection[k]=old_selection[k]
 selection['resource_measurement_revision']='Repeated framework warnings compacted; RF F6 control plus affected E5/E4 remeasured without per-warning record accumulation; model predictions unchanged.'
 save_csv(EVIDENCE/'resource_metrics.csv',resources);save_csv(EVIDENCE/'sensor_ablation_validation.csv',table);write_json(EVIDENCE/'ablation_details.json',details);write_json(EVIDENCE/'stage2_selection.json',selection)
 correction.update({'status':'completed','resource_only_refits':0,'results':outcomes,'prediction_or_hyperparameter_changes':False,
 'interpretation':'Only RF E5/E4 emitted repeated diagnostics in the initial capture. Other pipelines emitted none. RF F6 was remeasured as a control. Initial measurements and repeated diagnostics remain archived; corrected measurements replace these three entries consistently.'})
 write_json(EVIDENCE/'resource_benchmark_correction.json',correction)
 proto=json.loads((EVIDENCE/'measurement_protocol.json').read_text());proto['warning_handling']='Known scikit-learn parallel configuration diagnostic is filtered during timed calls; no per-warning append or diagnostic I/O is included. RF F6/E5/E4 were resource-only remeasured after detecting repeated warning capture.';write_json(EVIDENCE/'measurement_protocol.json',proto)
 if selection['shortlist_before_dropout']!=old_selection['shortlist_before_dropout']:dropout(selection,val)
 from .diagnostics import generate
 generate(pd.DataFrame(table))
 from .verification import verify
 print(json.dumps(verify(),indent=2))

if __name__=='__main__':main()
