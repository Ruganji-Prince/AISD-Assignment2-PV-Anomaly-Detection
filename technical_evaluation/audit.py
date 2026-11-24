"""Single audit entry point. Default verifies evidence; expensive experiments are opt-in."""
import argparse,json,re,subprocess,sys,datetime
from pathlib import Path
import numpy as np
from .common import *
def links():
 failures=[];count=0
 for p in ROOT.rglob('*.md'):
  if any(t in p.relative_to(ROOT).parts for t in ['.git','.cache','.review','node_modules','.vercel','__pycache__']):continue
  for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf8')):
   target=target.strip('<>').split('#')[0]
   if not target or '://' in target or target.startswith(('mailto:','/')):continue
   target=target.replace('%20',' ');count+=1
   if not (p.parent/target).exists():failures.append({'file':p.relative_to(ROOT).as_posix(),'target':target})
 return {'relative_links_checked':count,'failures':failures}
def verify(write_receipt=True):
 freeze_check();baseline=load('Protected_Baseline.json');allowed=baseline.get('allowed_existing_file_updates',['README.md','.vercelignore']);bad=[p for p,h in baseline['sha256'].items() if p not in allowed and (not (ROOT/p).exists() or sha(ROOT/p)!=h)];assert not bad,bad
 leakage=load('evidence/rubric2/leakage.json');assert leakage['source_index_disjoint'] and leakage['operating_blocks_disjoint'];assert leakage['excluded_N']==104231
 for group in leakage['feature_vectors'].values():assert all(r['shared_distinct_feature_vectors']==0 for r in group['cross_partition_overlap'])
 cal=load('evidence/rubric3/calibration_selection_freeze.json');assert not cal['new_calibrated_threshold_search'];assert all(r['fit_eval_overlap']==0 and r['source_tile_overlap']==0 for r in cal['folds'])
 checks=links();assert not checks['failures'],checks
 from src.inference.cli import predict
 m=original();cases=load('../deployment/example_cases.json')
 for c in cases:assert predict(c['input'],m)['predicted_class']==c['output']['predicted_class']
 # Recompute F1 directly from saved confusion matrices, not from prose.
 count=0
 def walk(x):
  nonlocal count
  if isinstance(x,dict):
   if 'confusion_matrix' in x and 'macro_f1_fixed_five' in x:
    cm=np.array(x['confusion_matrix']);tp=np.diag(cm[:,:5]);den=cm.sum(1)+cm[:,:5].sum(0);f=np.divide(2*tp,den,out=np.zeros(5),where=den>0);assert abs(f.mean()-x['macro_f1_fixed_five'])<1e-12;count+=1
   for v in x.values():walk(v)
  elif isinstance(x,list):
   for v in x:walk(v)
 for p in (OUT/'evidence').rglob('*.json'):walk(json.loads(p.read_text()))
 receipt={'status':'PASS','recorded_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protected_files_checked':len(baseline['sha256'])-len(allowed),'protected_hash_mismatches':bad,'original_RF_sha256':SHA,'protocol_sha256':sha(OUT/'Protocol.json'),'metric_tables_recomputed_from_confusions':count,'CLI_cases':len(cases),'links':checks,'runtime':version_info(),'scope':'Lightweight integrity/metric/schema verification; does not refit models, repeat cloud requests, or imply Docker execution.'}
 if write_receipt:write('evidence/rubric5/audit_verification.json',receipt)
 print(json.dumps(receipt,indent=2));return receipt
def main():
 p=argparse.ArgumentParser();p.add_argument('--run',action='store_true',help='Re-run data, calibration and robustness diagnostics (minutes).');p.add_argument('--train',action='store_true',help='Refit separate clipping and grouped-CV experimental models (expensive).');p.add_argument('--cloud',action='store_true',help='Explicitly permit bounded live API calls.');p.add_argument('--private-cache',type=Path);args=p.parse_args()
 from threadpoolctl import threadpool_limits
 threadpool_limits(2)
 if args.run:
  from .data_audit import main as data
  from .experiments import calibration,model_metrics
  from .robustness import main as robust
  data();d=raw();calibration(d);model_metrics(d,args.private_cache);robust()
  from .robustness import contiguous_dropout
  contiguous_dropout()
 if args.train:
  from .experiments import training_experiments
  training_experiments(raw())
 if args.private_cache:
  from .archived_explanations import main as explanations
  explanations(args.private_cache)
 if args.cloud:
  from .cloud import main as cloud
  cloud()
 for command in [[sys.executable,'-B','-m','unittest','technical_evaluation.tests','-v'],[sys.executable,'-B','-m','unittest','discover','-s','tests','-v'],[sys.executable,'-B','-m','unittest','discover','-s','web/tests','-v']]:subprocess.run(command,cwd=ROOT,check=True)
 verify()
if __name__=='__main__':main()
