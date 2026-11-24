"""Lightweight professor entry point; no fitting, cloud calls or tracked-file writes."""
import argparse,json,subprocess,sys
from technical_evaluation.common import ROOT,SHA,sha,raw,freeze_check
from technical_evaluation.audit import links,verify as previous_verify
from .experiments import OUT,freeze,load,write
ALLOWED={'README.md','.vercelignore','web/app.py','src/inference/cli.py','technical_evaluation/audit.py','technical_evaluation/reconstruct.py','pyproject.toml','Dockerfile','web/tests/test_api.py','vercel.json','.gitignore'}
def integrity():
 freeze();freeze_check();baseline=json.loads((OUT/'Baseline.json').read_text());bad=[p for p,h in baseline['sha256'].items() if p not in ALLOWED and (not (ROOT/p).exists() or sha(ROOT/p)!=h)];assert not bad,bad
 assert sha(ROOT/'models/rf_e4/model.pkl')==SHA
 near=load('refinement/results/full_near_duplicates.json');assert len(near['results'])==4
 for r in near['results']:assert r['TRAIN_reference_N']==1006129 and r['query_N']==({'VALIDATION':116977,'TEST':146461}[r['partition']]) and r['zero_distance_N']==0
 cal=load('refinement/results/calibration/calibration_selection_freeze.json');assert not cal['new_calibrated_threshold_search'];assert all(x['fit_eval_overlap']==0 and x['source_tile_overlap']==0 for x in cal['folds'])
 first=load('refinement/results/reconstruction_comparison.json');rerun=load('refinement/results/LR_thread_sensitivity.json');assert first['count']==21 and all(abs(x['delta'])<1e-12 for x in rerun['controlled_rerun'])
 empirical=load('refinement/results/empirical_scenarios.json');assert len(empirical['samples'])==250 and empirical['no_TEST_used'] and empirical['no_prediction_rejection'];assert all(x['source_position']<1006129 for x in empirical['samples'])
 linkcheck=links();assert not linkcheck['failures'],linkcheck
 result={'status':'PASS','protected_prior_files':sum(p not in ALLOWED for p in baseline['sha256']),'prior_hash_mismatches':bad,'original_model_SHA256':SHA,'near_duplicate_queries':4,'reconstructed_candidates':21,'empirical_scenarios':250,'relative_links':linkcheck,'mandatory_checks':{'repository_README':'Local files/links and public URLs documented; final publication independently checked.','leakage':'No identified unaddressed target/preprocessing overlap; close feature vectors and historical TEST remain disclosed.','cloud_and_secrets':'Use separately recorded live/secret receipts; this command makes no network calls.'}}
 cache=ROOT/'.cache/technical_refinement';cache.mkdir(parents=True,exist_ok=True);(cache/'latest_verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--skip-tests',action='store_true');a=p.parse_args()
 if not a.skip_tests:
  for args in [['-m','unittest','technical_evaluation.tests','technical_evaluation.refinement.tests','-v'],['-m','unittest','discover','-s','tests','-v'],['-m','unittest','discover','-s','web/tests','-v']]:subprocess.run([sys.executable,'-B',*args],cwd=ROOT,check=True)
 previous_verify(write_receipt=False);print(json.dumps(integrity(),indent=2))
if __name__=='__main__':main()
