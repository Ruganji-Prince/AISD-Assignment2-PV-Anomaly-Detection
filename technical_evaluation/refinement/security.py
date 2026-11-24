"""Combine full reachable-history scan with every current changed/new file."""
import argparse,subprocess,re,json
from pathlib import Path
from technical_evaluation.common import ROOT
from .experiments import write

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--git',default='git');args=parser.parse_args()
 import technical_evaluation.security as legacy
 report={};previous=legacy.write
 legacy.write=lambda name,x:report.update(x)
 try:legacy.main(args.git)
 finally:legacy.write=previous
 names=set(subprocess.check_output([args.git,'diff','--name-only'],cwd=ROOT,text=True).splitlines())|set(subprocess.check_output([args.git,'ls-files','--others','--exclude-standard'],cwd=ROOT,text=True).splitlines())
 patterns={'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----','github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{60,})','AWS_access_key':rb'AKIA[0-9A-Z]{16}','Slack_token':rb'xox[baprs]-[0-9A-Za-z-]{20,}','Google_API_key':rb'AIza[0-9A-Za-z_-]{35}'}
 findings=[];paths=[]
 for name in sorted(names):
  p=ROOT/name
  if not p.is_file():continue
  b=p.read_bytes()
  for kind,pattern in patterns.items():
   if re.search(pattern,b):findings.append({'file':name,'kind':kind,'value':'REDACTED'})
  if p.suffix.lower() in ['.json','.md','.py','.toml','.yml','.txt','.lock'] and re.search(rb'[A-Za-z]:[\\/](?:Users|CMU_Studies)[\\/]',b):paths.append(name)
 report.update({'all_changed_new_files_checked':len(names),'changed_new_secret_findings':findings,'changed_new_private_paths':paths,'locked_production_advisory_receipt':'runtime_dependency_audit.json','runtime_policy':'Only explicit independently verified CPython patches; scientific dependency pins unchanged. Provider patch selection is outside application control.','rate_limit_review':'../Rate_Limit_Review.json','scope_note':'All reachable Git refs plus every changed/new unignored file; high-specificity heuristics are not a proof against arbitrary secret formats.'});write('results/security.json',report)
 assert not findings and not paths,'New secrets/private paths require review; no values printed'
 print('COMPLETE_CHANGED_FILE_SECRET_SCAN_PASS',len(names),flush=True)
if __name__=='__main__':main()
