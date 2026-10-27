"""Verify the exact publication package without experiments, model caches or Git."""
import json,re,sys,subprocess,tempfile,shutil,collections
from pathlib import Path
from src.phase2_stage4.common import ROOT,sha,load,write,audit_text
CANONICAL='phase2_implementation/stage4/evidence/Publication_File_Hashes.json'
EXCEPTIONS='phase2_implementation/stage5/Publication_Exceptions.json'
PROTECTION='phase2_implementation/stage5/Scientific_Protection.json'
PATHS=re.compile(r'(?<![A-Za-z])(?:[A-Za-z]:[\\/]|/(?:Users|home)/)')
SECRET_PATTERNS=[re.compile(p) for p in [r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}',r'AKIA[A-Z0-9]{16}',r'AIza[A-Za-z0-9_-]{30,}',r'sk-(?:proj-)?[A-Za-z0-9_-]{30,}',r'(?i)authorization\s*[:=]\s*[\"\x27]?(?:Bearer|Basic)\s+[A-Za-z0-9+/=._-]{12,}']]
def verify():
 manifest=load(CANONICAL);names=sorted(set(manifest['sha256'])|{CANONICAL});protection=load(PROTECTION);exceptions=load(EXCEPTIONS)
 for n,h in manifest['sha256'].items():assert sha(ROOT/n)==h,('Publication hash mismatch',n)
 for n,h in protection['scientific_sha256'].items():assert sha(ROOT/n)==h,('Frozen scientific mismatch',n)
 readme=(ROOT/'README.md').read_bytes();prefix=exceptions['README']['remote_prefix_bytes'];assert __import__('hashlib').sha256(readme[:prefix]).hexdigest()==exceptions['README']['remote_prefix_sha256'];assert sha(ROOT/'README.md')==exceptions['README']['published_sha256']
 local=ROOT/'phase2_implementation/stage4/Protected_Stage123_Hashes.json';local_count=0
 if local.exists():
  for n,h in load(local.relative_to(ROOT))['sha256'].items():
   if n=='README.md':continue
   assert sha(ROOT/n)==h,('Local frozen mismatch',n);local_count+=1
 paths=[];secrets=[];large=[];figures=[]
 for n in names:
  p=ROOT/n;assert p.is_file();assert not any(part in ['.venv','.git','.tools','__pycache__'] for part in p.relative_to(ROOT).parts);assert p.suffix not in ['.pkl','.npz','.joblib','.pem','.key']
  if p.stat().st_size>25*2**20:large.append({'file':n,'bytes':p.stat().st_size,'existing_approved_raw_CSV':n=='data/raw/pv_fault_dataset.csv'})
  assert p.stat().st_size<=100*2**20,('Oversized',n)
  if p.suffix.lower() in ['.py','.md','.json','.csv','.txt','.ipynb','.tex']:
   text=audit_text(p)
   if PATHS.search(text) or ('CMU_'+'Studies') in text or ('Assignment2_Submission_'+'Preparation_20261013') in text:paths.append(n)
   if any(pattern.search(text) for pattern in SECRET_PATTERNS):secrets.append(n)
  if p.suffix.lower()=='.png':figures.append((n,sha(p)))
 # Print only filenames for any credential finding; never the matching value.
 if secrets:raise RuntimeError('Possible credentials in files: '+', '.join(secrets))
 assert not paths,('Accidental local paths',paths)
 assert all(r['existing_approved_raw_CSV'] for r in large),('Unreviewed large files',large)
 assert len({h for _,h in figures})==len(figures),'Duplicate public PNG bytes'
 cache=ROOT/'.cache/publication-review';cache.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='package-',dir=cache) as folder:
  target=Path(folder).resolve();assert target.is_relative_to(cache.resolve())
  for n in names:
   dest=target/n;assert dest.resolve().is_relative_to(target);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/n,dest)
  assert not (target/'.git').exists() and not (target/'.cache/stage2/models').exists()
  command=[sys.executable,'-B','-X','utf8','-m','src.phase2_stage4.verification'];r=subprocess.run(command,cwd=target,capture_output=True,text=True,encoding='utf8')
  if r.returncode:raise RuntimeError('Isolated publication verification failed: '+r.stderr)
  checked=json.loads(r.stdout)
 result={'status':'passed','public_files':len(names),'scientific_public_hashes_unchanged':len(protection['scientific_sha256']),'local_scientific_hashes_unchanged':local_count,'README_remote_prefix_preserved':True,'report_sha256':sha(ROOT/'phase2_implementation/reports/Phase2_Final_Report.pdf'),'absolute_path_findings':paths,'credential_findings':secrets,'files_over_25MiB':large,'files_over_100MiB':0,'public_PNGs':len(figures),'duplicate_public_PNGs':False,'isolated_without_Git_or_model_caches':True,'portable_checks':checked,'no_experiments_executed':True}
 write(cache/'verification.json',result);print(json.dumps(result,indent=2));return result
if __name__=='__main__':verify()
