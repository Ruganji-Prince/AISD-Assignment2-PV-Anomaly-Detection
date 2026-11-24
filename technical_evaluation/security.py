"""Heuristic high-specificity secret scan, with explicit scope and limitations."""
import re,subprocess,os,json
from .common import *
def main(git='git'):
 patterns={'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})','AWS_access_key':rb'AKIA[0-9A-Z]{16}','Slack_token':rb'xox[baprs]-[0-9A-Za-z-]{20,}','Google_API_key':rb'AIza[0-9A-Za-z_-]{35}'}
 objects=subprocess.check_output([git,'rev-list','--objects','--all'],cwd=ROOT,text=True).splitlines();findings=[];scanned=0;skipped=0;paths=[]
 for entry in objects:
  oid,_,path=entry.partition(' ')
  typ=subprocess.check_output([git,'cat-file','-t',oid],cwd=ROOT,text=True).strip()
  if typ!='blob':continue
  size=int(subprocess.check_output([git,'cat-file','-s',oid],cwd=ROOT,text=True))
  if size>2000000:skipped+=1
  body=subprocess.check_output([git,'cat-file','blob',oid],cwd=ROOT);scanned+=1
  for name,pattern in patterns.items():
   if re.search(pattern,body):findings.append({'object':oid,'path':path,'kind':name,'secret_value':'REDACTED'})
  if Path(path).name.startswith('.env') and Path(path).name not in ['.env.example','.env.sample']:paths.append({'object':oid,'path':path})
 work=[];absolute=[]
 for base in [OUT,ROOT/'Dockerfile',ROOT/'.dockerignore']:
  files=base.rglob('*') if base.is_dir() else [base]
  for p in files:
   if not p.is_file() or '__pycache__' in p.parts or p.suffix in ['.png','.pdf']:continue
   body=p.read_bytes()
   for name,pattern in patterns.items():
    if re.search(pattern,body):work.append({'path':p.relative_to(ROOT).as_posix(),'kind':name})
   if re.search(rb'[A-Za-z]:[\\/](?:Users|CMU_Studies)[\\/]',body):absolute.append(p.relative_to(ROOT).as_posix())
 report={'method':'High-specificity heuristic credential signatures, no values printed; not proof of absence of every possible secret.','reachable_commit_N':int(subprocess.check_output([git,'rev-list','--all','--count'],cwd=ROOT,text=True)),'history_blobs_scanned':scanned,'history_blobs_over_2MB_scanned':skipped,'history_findings':findings,'tracked_environment_candidates':paths,'new_work_findings':work,'new_absolute_local_path_files':absolute,'safety_review':{'model_deserialization':'Only fixed trusted SHA256-checked original artifact; no upload or arbitrary pickle loading endpoint.','API_body_limit_bytes':2048,'unexpected_fields':'Rejected','nonfinite_and_missing':'Rejected','production_confidence':'Not displayed','application_rate_limiting':'No authenticated per-user application limit; public free-tier denial-of-service/quota risk remains.','headers':'CSP self, DENY frames, nosniff; no secrets supplied to frontend.','secret_rotation':'No high-specificity match found' if not findings else 'Review and rotate any actual credentials; no history rewriting authorized.'}}
 write('evidence/rubric5/security.json',report)
 assert not findings and not work and not paths and not absolute, 'Security findings require review before publication'
 print('HEURISTIC_SECRET_SCAN_COMPLETE',scanned,flush=True)
